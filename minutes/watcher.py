"""Watch folder: new recordings that appear in a chosen folder are queued automatically.

Point it at the folder where Zoom, OBS or a voice recorder saves files. Rules:
- Only files that appear after watching starts are queued, so turning it on doesn't
  flood the queue with old recordings.
- A file is queued once its size has stopped changing for two checks in a row, so a
  recording that is still being written is left alone.
- The original file is never moved or deleted: a copy goes through the normal pipeline.
- Each file is queued once (remembered across restarts in data/watched.json).
"""

from __future__ import annotations

import json
import logging
import shutil
import threading
import uuid
from pathlib import Path
from typing import Callable

from . import config

log = logging.getLogger("minutes")

MEDIA = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".m4a", ".mp3", ".wav", ".aac", ".flac", ".ogg", ".opus", ".wma"}
POLL_SECONDS = 5.0
MAX_REMEMBERED = 5000


def _key(path: Path, size: int, mtime: float) -> str:
    return f"{path.resolve()}|{size}|{int(mtime)}"


class FolderWatcher:
    """Polls the watch_dir setting. Polling (not OS events) works the same on every
    platform and on network drives, and a 5 s delay doesn't matter for recordings."""

    def __init__(self, submit: Callable[[Path, str, float], object], poll_seconds: float = POLL_SECONDS):
        self.submit = submit
        self.poll_seconds = poll_seconds
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._folder: Path | None = None
        self._pending: dict[Path, tuple[int, float]] = {}  # path -> (size, mtime) at the last check
        self._seen: list[str] = self._load_seen()

    # ------------------------------------------------------------ lifecycle

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="minutes-watcher")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self.check()
            except Exception:  # a bad file or a missing drive must not kill the watcher
                log.exception("Watch folder check failed")
            self._stop.wait(self.poll_seconds)

    # ------------------------------------------------------------ one pass

    def check(self) -> list[Path]:
        """Look at the folder once. Returns the files queued on this pass."""
        raw = (config.load().get("watch_dir") or "").strip()
        folder = Path(raw).expanduser() if raw else None
        if folder != self._folder:
            self._folder = folder
            self._pending.clear()
            if folder and folder.is_dir():
                self._mark_existing(folder)
                log.info("Watching %s for new recordings", folder)
            return []
        if not folder or not folder.is_dir():
            return []

        queued = []
        current = {}
        for path, size, mtime in self._media_files(folder):
            if _key(path, size, mtime) in self._seen:
                continue
            current[path] = (size, mtime)
            if self._pending.get(path) == (size, mtime) and size > 0 and self._readable(path):
                self._queue(path, size, mtime)
                queued.append(path)
                current.pop(path)
        self._pending = current
        return queued

    # ------------------------------------------------------------ helpers

    @staticmethod
    def _media_files(folder: Path):
        for path in folder.iterdir():
            if path.suffix.lower() in MEDIA and not path.name.startswith("."):
                try:
                    st = path.stat()
                except OSError:
                    continue
                if path.is_file():
                    yield path, st.st_size, st.st_mtime

    @staticmethod
    def _readable(path: Path) -> bool:
        try:
            with path.open("rb") as f:
                f.read(1)
            return True
        except OSError:  # still locked by the recorder (Windows), or permissions
            return False

    def _mark_existing(self, folder: Path) -> None:
        for path, size, mtime in self._media_files(folder):
            self._remember(_key(path, size, mtime))
        self._save_seen()

    def _queue(self, path: Path, size: int, mtime: float) -> None:
        copy = config.run_dir() / f"{uuid.uuid4().hex}{path.suffix.lower()[:10]}"
        shutil.copy2(path, copy)
        self._remember(_key(path, size, mtime))
        self._save_seen()
        log.info("Watch folder: queued %s", path.name)
        self.submit(copy, path.name, mtime * 1000)

    def _remember(self, key: str) -> None:
        if key not in self._seen:
            self._seen.append(key)
            del self._seen[:-MAX_REMEMBERED]

    @staticmethod
    def _seen_path() -> Path:
        return config.DATA_DIR / "watched.json"

    def _load_seen(self) -> list[str]:
        try:
            return list(json.loads(self._seen_path().read_text(encoding="utf-8")))
        except (OSError, ValueError):
            return []

    def _save_seen(self) -> None:
        path = self._seen_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._seen), encoding="utf-8")
        tmp.replace(path)
