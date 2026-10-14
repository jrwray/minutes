import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    """Point settings, work dir and output dir at a temp folder."""
    from minutes import config

    data = tmp_path / "data"
    monkeypatch.setattr(config, "DATA_DIR", data)
    monkeypatch.setattr(config, "WORK_DIR", data / "work")
    monkeypatch.setattr(config, "SETTINGS_PATH", data / "settings.json")
    config.save({"output_dir": str(tmp_path / "Transcripts"), "summary_engine": "none", "diarization": False})
    return tmp_path


@pytest.fixture
def client(isolated):
    """In-process API client addressed the way the browser addresses the real server."""
    from fastapi.testclient import TestClient

    from minutes import server

    with TestClient(server.app, base_url="http://127.0.0.1:7860", headers={"X-Minutes": "1"}) as c:
        yield c


class FakeEngines:
    """Stand-ins for Whisper, pyannote and the summary models. Deterministic, instant,
    and controllable (slow mode for cancel tests, failure switches)."""

    SEGMENTS = [
        {"start": 0.0, "end": 4.0, "text": "Welcome everyone, let's review the budget.",
         "words": [{"start": 0.0, "end": 2.0, "word": " Welcome everyone,"}, {"start": 2.0, "end": 4.0, "word": " let's review the budget."}]},
        {"start": 5.0, "end": 9.0, "text": "We're ten percent under. I'll send the report Friday.",
         "words": [{"start": 5.0, "end": 7.0, "word": " We're ten percent under."}, {"start": 7.0, "end": 9.0, "word": " I'll send the report Friday."}]},
    ]

    def __init__(self):
        self.slow = False
        self.summary_fails = False
        self.summary_calls = []

    def load_audio(self, path, display_name=None):
        import numpy as np
        return np.zeros(16000 * 10, dtype="float32")

    def transcribe(self, audio, settings, on_progress, is_cancelled):
        import time
        from minutes.transcribe import Cancelled
        steps = 200 if self.slow else 1
        for i in range(steps):
            if is_cancelled():
                raise Cancelled()
            on_progress((i + 1) / steps, "…")
            if self.slow:
                time.sleep(0.02)
        return {"language": "en", "language_probability": 0.99, "duration": 10.0,
                "segments": [dict(s, words=list(s["words"])) for s in self.SEGMENTS]}

    def diarize(self, audio, token, num_speakers, on_progress, is_cancelled):
        return [(0.0, 4.5, "SPEAKER_00"), (4.5, 10.0, "SPEAKER_01")]

    def summarize(self, segments, speakers, meeting_date, settings, engine, on_progress, is_cancelled):
        self.summary_calls.append({"engine": engine, "speakers": dict(speakers)})
        if self.summary_fails:
            raise RuntimeError("Ollama isn't running.")
        owner = speakers.get("Speaker 2", "Speaker 2")
        return {
            "title": "Budget Review",
            "overview": f"The team reviewed the budget; {owner} reported the numbers.",
            "decisions": ["Keep the budget as is."],
            "action_items": [{"task": "Send the report", "owner": owner, "due": "Friday"}],
            "open_questions": [],
            "topics": [{"start": 0.0, "topic": "Budget"}],
        }


@pytest.fixture
def fakes(monkeypatch):
    import shutil

    from minutes import audio, diarize, export, summarize, transcribe

    f = FakeEngines()
    monkeypatch.setattr(audio, "load_audio", f.load_audio)
    monkeypatch.setattr(transcribe, "transcribe", f.transcribe)
    monkeypatch.setattr(transcribe, "is_model_cached", lambda name: True)
    monkeypatch.setattr(diarize, "diarize", f.diarize)
    monkeypatch.setattr(summarize, "summarize", f.summarize)
    # Tests must never send temp folders to the user's real Recycle Bin.
    monkeypatch.setattr(export, "to_recycle_bin", lambda p: shutil.rmtree(p))
    return f


@pytest.fixture
def api(client, fakes):
    """API client with fake engines plus upload/wait helpers."""
    import time

    def upload(name="call.mp4", data=b"fake media"):
        r = client.post("/api/upload", files={"file": (name, data)}, data={"last_modified": "1791979200000"})  # 2026-10-14 12:00 UTC
        assert r.status_code == 200, r.text
        return r.json()

    def wait(job_id, timeout=10):
        end = time.time() + timeout
        while time.time() < end:
            job = next(j for j in client.get("/api/jobs").json() if j["id"] == job_id)
            if job["status"] in ("done", "error", "cancelled"):
                return job
            time.sleep(0.02)
        raise TimeoutError(job_id)

    client.upload, client.wait, client.fakes = upload, wait, fakes
    return client


@pytest.fixture
def meeting():
    """A small, fully-formed meeting as the pipeline would produce it."""
    return {
        "id": "abc123def456",
        "name": "2026-10-14_Budget-Review",
        "created": 1_700_000_000.0,
        "meeting_date": "2026-10-14",
        "source_name": "call.mp4",
        "duration": 95.0,
        "language": "en",
        "segments": [
            {"start": 0.0, "end": 4.2, "text": "Let's start with the budget.", "speaker": "Speaker 1"},
            {"start": 4.5, "end": 9.0, "text": "Speaker 2 has the numbers.", "speaker": "Speaker 1"},
            {"start": 9.4, "end": 15.1, "text": "Yes, we're under by ten percent.", "speaker": "Speaker 2"},
        ],
        "speakers": {"Speaker 1": "Speaker 1", "Speaker 2": "Speaker 2"},
        "summary": {
            "title": "Budget Review",
            "overview": "Speaker 1 and Speaker 2 reviewed the budget.",
            "decisions": ["Keep the current budget."],
            "action_items": [{"task": "Send the report", "owner": "Speaker 2", "due": "Friday"}],
            "open_questions": [],
            "topics": [{"start": 0.0, "topic": "Budget"}],
        },
        "summary_engine": "Ollama (qwen2.5:7b)",
        "whisper_model": "large-v3-turbo",
        "folder": None,
        "files": [],
    }
