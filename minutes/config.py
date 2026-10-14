"""Settings persisted to data/settings.json (local only; keys never leave this machine
except the Anthropic key, which is sent to Anthropic when the Claude engine is used)."""

from __future__ import annotations

import json
import os
import threading
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
WORK_DIR = DATA_DIR / "work"
SETTINGS_PATH = DATA_DIR / "settings.json"

DEFAULTS: dict = {
    "output_dir": str(Path.home() / "Videos" / "Transcripts"),
    "whisper_model": "large-v3-turbo",
    "compute_type": "int8",  # CPU; the GPU always uses float16
    "device": "",  # "" = not chosen yet (the UI asks on first run) | "cpu" | "gpu"
    "language": "auto",
    "vocabulary": "",
    "diarization": True,
    "num_speakers": 0,  # 0 = auto-detect
    "hf_token": "",
    "summary_engine": "ollama",  # ollama | claude | none
    "ollama_url": "http://127.0.0.1:11434",
    "ollama_model": "qwen2.5:7b",
    "claude_model": "claude-opus-5-5",
    "anthropic_api_key": "",
    "anthropic_workspace_id": "",  # only for keys that aren't scoped to a workspace
    "keep_wav": False,
    "cpu_threads": 0,  # 0 = auto
}

SECRET_KEYS = ("hf_token", "anthropic_api_key")


def run_dir() -> Path:
    """This process's scratch folder for uploads and temp WAVs. Per-process, so a
    second running copy of the app can tell its files apart (see jobs.clean_work_dir)."""
    path = WORK_DIR / f"run-{os.getpid()}"
    path.mkdir(parents=True, exist_ok=True)
    return path

# save() holds both locks across its load-modify-write so concurrent saves of different
# keys can't overwrite each other: the RLock between threads of this process, the lock
# file between processes (e.g. Start.bat plus a second copy on another port).
_lock = threading.RLock()


@contextmanager
def _process_lock():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "settings.lock", "a+b") as f:
        if os.name == "nt":
            import msvcrt

            while True:
                try:
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)  # blocks (retries ~10 s)
                    break
                except OSError:
                    continue
            try:
                yield
            finally:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)


def load() -> dict:
    with _lock:
        data = dict(DEFAULTS)
        if SETTINGS_PATH.exists():
            try:
                data.update(json.loads(SETTINGS_PATH.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                pass
        return data


def save(patch: dict) -> dict:
    from .export import write_atomic

    with _lock, _process_lock():
        current = load()
        for key, value in patch.items():
            if key not in DEFAULTS:
                continue
            # The UI sends secrets back masked; only overwrite when a real value is given.
            if key in SECRET_KEYS and isinstance(value, str) and value.startswith("••"):
                continue
            current[key] = value
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        write_atomic(SETTINGS_PATH, json.dumps(current, indent=2))
        return current


def public(settings: dict) -> dict:
    """Settings safe to send to the browser: secrets masked."""
    out = dict(settings)
    for key in SECRET_KEYS:
        value = out.get(key) or ""
        out[key] = ("••••" + value[-4:]) if value else ""
    return out
