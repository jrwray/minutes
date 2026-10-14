"""Single-worker job queue. Transcription is CPU-bound, so jobs run one at a time."""

from __future__ import annotations

import datetime as dt
import logging
import os
import queue
import shutil
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from . import config, export
from .transcribe import Cancelled

log = logging.getLogger("minutes")

STAGES = ["audio", "transcribe", "speakers", "summary", "save"]


def _pid_alive(pid: int) -> bool:
    if pid == os.getpid():
        return True
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return ctypes.get_last_error() == 5  # access denied: exists, owned by someone else
        code = ctypes.c_ulong()
        ok = kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
        kernel32.CloseHandle(handle)
        return bool(ok) and code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)  # POSIX only: signal 0 just checks. (On Windows os.kill terminates!)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def clean_work_dir() -> None:
    """Remove uploads and temp files left behind when the app was closed mid-job.
    The queue lives in memory, so a dead process's files can never be processed.
    Folders of copies that are still running are left alone."""
    if not config.WORK_DIR.exists():
        return
    removed = 0
    for entry in config.WORK_DIR.iterdir():
        try:
            if entry.is_dir() and entry.name.startswith("run-"):
                pid = entry.name.removeprefix("run-")
                if pid.isdigit() and not _pid_alive(int(pid)):
                    shutil.rmtree(entry, ignore_errors=True)
                    removed += 1
            elif entry.is_file() and time.time() - entry.stat().st_mtime > 3600:
                entry.unlink()  # loose files from versions before per-process folders
                removed += 1
        except OSError:
            continue
    if removed:
        log.info("Cleaned up %d leftover upload(s) from earlier runs", removed)


@dataclass
class Job:
    id: str
    kind: str  # "process" | "summarize"
    filename: str
    upload: Path | None = None
    meeting_id: str | None = None
    meeting_date: str = ""
    engine: str | None = None
    status: str = "queued"  # queued | running | done | error | cancelled
    stage: str = ""
    stage_progress: float = 0.0
    message: str = ""
    preview: str = ""
    warnings: list[str] = field(default_factory=list)
    error: str = ""
    skipped: list[str] = field(default_factory=list)
    created: float = field(default_factory=time.time)
    started: float | None = None
    finished: float | None = None
    cancel: threading.Event = field(default_factory=threading.Event)

    def public(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "filename": self.filename,
            "meeting_id": self.meeting_id,
            "status": self.status,
            "stage": self.stage,
            "stages": STAGES if self.kind == "process" else ["summary", "save"],
            "skipped": self.skipped,
            "stage_progress": round(self.stage_progress, 4),
            "message": self.message,
            "preview": self.preview,
            "warnings": self.warnings,
            "error": self.error,
            "created": self.created,
            "started": self.started,
            "finished": self.finished,
        }


class Manager:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}
        self.q: queue.Queue[str] = queue.Queue()
        self.lock = threading.Lock()  # guards self.jobs
        # Serializes every write to a meeting's folder (rename, speaker edits, summary
        # saves, delete) so two writers never interleave on the same files.
        self.write_lock = threading.RLock()
        self.meetings: dict[str, Path] = {}  # meeting id -> json path
        self._list_cache: dict[Path, tuple[tuple[int, int], dict | None]] = {}
        self._list_lock = threading.Lock()
        threading.Thread(target=self._worker, daemon=True, name="minutes-worker").start()

    # ------------------------------------------------------------ public API

    def submit_file(self, upload: Path, filename: str, last_modified_ms: float | None) -> Job:
        when = dt.datetime.fromtimestamp(last_modified_ms / 1000) if last_modified_ms else dt.datetime.now()
        job = Job(id=uuid.uuid4().hex[:10], kind="process", filename=filename, upload=upload,
                  meeting_date=when.strftime("%Y-%m-%d"))
        return self._enqueue(job)

    def submit_summary(self, meeting_id: str, engine: str) -> Job:
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            raise KeyError(meeting_id)
        job = Job(id=uuid.uuid4().hex[:10], kind="summarize", filename=meeting["name"],
                  meeting_id=meeting_id, engine=engine)
        return self._enqueue(job)

    def cancel(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if not job or job.status not in ("queued", "running"):
            return False
        job.cancel.set()
        if job.status == "queued":
            self._finish(job, "cancelled")
        return True

    def dismiss(self, job_id: str) -> None:
        with self.lock:
            job = self.jobs.get(job_id)
            if job and job.status in ("done", "error", "cancelled"):
                del self.jobs[job_id]

    def list_jobs(self) -> list[dict]:
        with self.lock:
            return [j.public() for j in sorted(self.jobs.values(), key=lambda j: j.created)]

    def list_meetings(self) -> list[dict]:
        """Sidebar entries for every meeting folder. The UI polls this every few seconds,
        so each JSON (which holds the whole transcript) is only parsed again when its
        size or modification time changes."""
        out_dir = Path(config.load()["output_dir"])
        with self._list_lock:
            entries, seen = [], set()
            for paths in export.candidate_files(out_dir):
                for path in paths:
                    seen.add(path)
                    try:
                        st = path.stat()
                    except OSError:
                        continue
                    key = (st.st_mtime_ns, st.st_size)
                    cached = self._list_cache.get(path)
                    if cached and cached[0] == key:
                        entry = cached[1]
                    else:
                        meeting = export.read_meeting(path)
                        entry = self._list_entry(meeting) if meeting else None
                        self._list_cache[path] = (key, entry)
                    if entry:
                        entries.append((entry, path))
                        break
            for path in set(self._list_cache) - seen:
                del self._list_cache[path]
            self.meetings = {entry["id"]: path for entry, path in entries}
            return sorted((e for e, _ in entries), key=lambda e: e.get("created") or 0, reverse=True)

    @staticmethod
    def _list_entry(m: dict) -> dict:
        s = m.get("summary") or {}
        return {
            "id": m["id"],
            "name": m["name"],
            "title": s.get("title") or "",
            "meeting_date": m.get("meeting_date"),
            "duration": m.get("duration"),
            "created": m.get("created"),
            "speakers": len(set((m.get("speakers") or {}).values())),
            "has_summary": bool(m.get("summary")),
            "action_items": len(s.get("action_items") or []),
        }

    def get_meeting(self, meeting_id: str) -> dict | None:
        path = self.meetings.get(meeting_id)
        if not path or not path.exists():
            self.list_meetings()
            path = self.meetings.get(meeting_id)
        return export.read_meeting(path) if path and path.exists() else None

    def update_meeting(self, meeting_id: str, name: str | None, speakers: dict | None) -> dict:
        with self.write_lock:
            return self._update_meeting(meeting_id, name, speakers)

    def _update_meeting(self, meeting_id: str, name: str | None, speakers: dict | None) -> dict:
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            raise KeyError(meeting_id)
        if speakers is not None:
            old = meeting.get("speakers") or {}
            new = {label: (speakers.get(label) or "").strip() or label for label in old}
            renames = {old[label]: new[label] for label in old if old[label] != new[label]}
            if meeting.get("summary") and renames:
                meeting["summary"] = export.replace_names(meeting["summary"], renames)
            meeting["speakers"] = new
        if name is not None and name.strip():
            meeting["name"] = export.clean_name(name)
        return self._save(meeting, config.load())

    def delete_meeting(self, meeting_id: str) -> None:
        with self.write_lock:
            meeting = self.get_meeting(meeting_id)
            if not meeting:
                raise KeyError(meeting_id)
            if any(j.meeting_id == meeting_id and j.status in ("queued", "running") for j in self.jobs.values()):
                raise RuntimeError("This meeting is being summarized. Wait for it to finish or cancel it first.")
            export.to_recycle_bin(Path(meeting["folder"]))
            self.meetings.pop(meeting_id, None)

    # ------------------------------------------------------------ internals

    def _enqueue(self, job: Job) -> Job:
        with self.lock:
            self.jobs[job.id] = job
        self.q.put(job.id)
        return job

    def _finish(self, job: Job, status: str, error: str = "") -> None:
        job.status, job.error, job.finished = status, error, time.time()
        job.stage = "" if status != "error" else job.stage
        if job.upload and job.upload.exists():
            try:
                job.upload.unlink()
            except OSError:
                pass

    def _worker(self) -> None:
        while True:
            job = self.jobs.get(self.q.get())
            if not job or job.status != "queued":
                continue
            job.status, job.started = "running", time.time()
            try:
                if job.kind == "process":
                    self._process(job)
                else:
                    self._resummarize(job)
                self._finish(job, "done")
            except Cancelled:
                self._finish(job, "cancelled")
            except Exception as exc:  # surface everything to the UI
                log.error("job %s failed\n%s", job.id, traceback.format_exc())
                self._finish(job, "error", str(exc) or exc.__class__.__name__)

    def _stage(self, job: Job, stage: str, message: str = "") -> None:
        job.stage, job.stage_progress, job.message = stage, 0.0, message

    def _progress(self, job: Job):
        def cb(p: float, message: str = "") -> None:
            job.stage_progress = max(0.0, min(1.0, p))
            if message:
                job.message = message
        return cb

    def _process(self, job: Job) -> None:
        from . import audio as audio_mod
        from . import transcribe as tr

        settings = config.load()
        cancelled = job.cancel.is_set

        self._stage(job, "audio", "Reading audio…")
        audio = audio_mod.load_audio(job.upload, job.filename)
        if len(audio) < audio_mod.SAMPLE_RATE // 2:
            raise audio_mod.AudioError(f"“{job.filename}” has less than half a second of audio.")
        job.stage_progress = 1.0

        self._stage(job, "transcribe", "Loading Whisper…")
        if not tr.is_model_cached(settings["whisper_model"]):
            job.message = "Downloading Whisper model (first run only, ~1.6 GB)…"
        progress = self._progress(job)

        from . import device as dev

        where = "on GPU" if dev.resolve(settings.get("device") or "cpu") == "cuda" else "on CPU"

        def on_text(p: float, text: str) -> None:
            progress(p, f"Transcribing {where}…")
            job.preview = text

        result = tr.transcribe(audio, settings, on_text, cancelled)
        job.preview = ""
        if result.get("gpu_fallback"):
            job.warnings.append(f"Used the CPU instead of the GPU: {result['gpu_fallback']}")
        segments = result["segments"]
        if not segments:
            job.warnings.append("No speech was detected.")

        speakers: dict[str, str] = {}
        if settings["diarization"] and settings["hf_token"] and segments:
            self._stage(job, "speakers", "Identifying speakers…")
            from . import diarize as dz
            try:
                turns = dz.diarize(audio, settings["hf_token"], int(settings.get("num_speakers") or 0),
                                   self._progress(job), cancelled)
                segments = dz.assign_speakers(segments, turns)
                labels = list(dict.fromkeys(s["speaker"] for s in segments if s.get("speaker")))
                speakers = {label: label for label in labels}
            except Cancelled:
                raise
            except Exception as exc:
                log.error("diarization failed\n%s", traceback.format_exc())
                job.warnings.append(f"Speaker detection failed: {exc}")
        else:
            job.skipped.append("speakers")

        for seg in segments:
            seg.pop("words", None)  # keep saved files lean
            seg.setdefault("speaker", None)

        meeting = {
            "id": uuid.uuid4().hex[:12],
            "name": "",
            "created": time.time(),
            "meeting_date": job.meeting_date,
            "source_name": job.filename,
            "duration": result["duration"],
            "language": result["language"],
            "segments": segments,
            "speakers": speakers,
            "summary": None,
            "summary_engine": None,
            "whisper_model": settings["whisper_model"],
            "device": result.get("device", "cpu"),
            "folder": None,
            "files": [],
        }

        engine = settings["summary_engine"]
        if engine != "none" and segments:
            self._stage(job, "summary", "Summarizing…")
            self._summarize_into(job, meeting, engine, settings)
        else:
            job.skipped.append("summary")

        self._stage(job, "save", "Saving files…")
        fallback = export.slug_title(Path(job.filename).stem) or "Meeting"
        title = (meeting["summary"] or {}).get("title") or ""
        meeting["name"] = export.default_name(job.meeting_date, title, fallback)
        wav_tmp = None
        if settings["keep_wav"]:
            wav_tmp = config.run_dir() / f"{job.id}.wav"
            audio_mod.write_wav(audio, wav_tmp)
        meeting = self._save(meeting, settings, wav_tmp)
        job.meeting_id = meeting["id"]
        job.stage_progress = 1.0

    def _save(self, meeting: dict, settings: dict, wav_source: Path | None = None) -> dict:
        with self.write_lock:
            meeting = export.write_meeting(meeting, Path(settings["output_dir"]), wav_source)
            self.meetings[meeting["id"]] = Path(meeting["folder"]) / export.file_names(meeting["name"])["json"]
            return meeting

    @staticmethod
    def _engine_label(engine: str, settings: dict) -> str:
        return f"Claude ({settings['claude_model']})" if engine == "claude" else f"Ollama ({settings['ollama_model']})"

    def _summarize_into(self, job: Job, meeting: dict, engine: str, settings: dict) -> None:
        from . import summarize as sm
        try:
            meeting["summary"] = sm.summarize(
                meeting["segments"], meeting["speakers"], meeting["meeting_date"], settings, engine,
                self._progress(job), job.cancel.is_set,
            )
            meeting["summary_engine"] = self._engine_label(engine, settings)
        except Cancelled:
            raise
        except Exception as exc:
            log.error("summary failed\n%s", traceback.format_exc())
            job.warnings.append(f"Summary failed: {exc}")

    def _resummarize(self, job: Job) -> None:
        from . import summarize as sm

        settings = config.load()
        meeting = self.get_meeting(job.meeting_id)
        if not meeting:
            raise RuntimeError("Meeting not found.")
        self._stage(job, "summary", "Summarizing…")
        snapshot = dict(meeting.get("speakers") or {})
        summary = sm.summarize(
            meeting["segments"], snapshot, meeting["meeting_date"], settings, job.engine,
            self._progress(job), job.cancel.is_set,
        )
        self._stage(job, "save", "Saving files…")
        with self.write_lock:
            # Summaries take minutes; the meeting may have been renamed or had speakers
            # renamed meanwhile. Apply the summary to the latest version, never the
            # stale copy (writing that would resurrect the old folder).
            latest = self.get_meeting(job.meeting_id)
            if not latest:
                raise RuntimeError("The meeting was deleted while it was being summarized.")
            current = latest.get("speakers") or {}
            renames = {snapshot[k]: current[k] for k in snapshot if k in current and snapshot[k] != current[k]}
            latest["summary"] = export.replace_names(summary, renames)
            latest["summary_engine"] = self._engine_label(job.engine, settings)
            self._save(latest, settings)
        job.stage_progress = 1.0
