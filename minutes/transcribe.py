"""Speech-to-text with faster-whisper (CPU, int8)."""

from __future__ import annotations

import os
import threading
from typing import Callable

import numpy as np

from .audio import SAMPLE_RATE

_lock = threading.Lock()
_model = None
_model_key: tuple | None = None


class Cancelled(Exception):
    pass


def default_threads() -> int:
    # Physical cores is the sweet spot for CTranslate2 on CPU.
    return max(1, (os.cpu_count() or 2) // 2)


def is_model_cached(name: str) -> bool:
    from faster_whisper.utils import download_model

    try:
        download_model(name, local_files_only=True)
        return True
    except Exception:
        return False


def get_model(name: str, compute_type: str, threads: int):
    global _model, _model_key
    key = (name, compute_type, threads)
    with _lock:
        if _model is None or _model_key != key:
            from faster_whisper import WhisperModel

            _model = None  # free the old one before loading a new one
            _model = WhisperModel(
                name,
                device="cpu",
                compute_type=compute_type,
                cpu_threads=threads or default_threads(),
            )
            _model_key = key
        return _model


def transcribe(
    audio: np.ndarray,
    settings: dict,
    on_progress: Callable[[float, str], None],
    is_cancelled: Callable[[], bool],
) -> dict:
    model = get_model(
        settings["whisper_model"], settings["compute_type"], int(settings.get("cpu_threads") or 0)
    )
    language = settings.get("language") or "auto"
    vocabulary = (settings.get("vocabulary") or "").strip()

    segments_iter, info = model.transcribe(
        audio,
        language=None if language == "auto" else language,
        initial_prompt=f"Glossary: {vocabulary}." if vocabulary else None,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        word_timestamps=True,
        beam_size=5,
        # Avoids the classic Whisper failure of repeating a phrase for minutes.
        condition_on_previous_text=False,
    )

    duration = len(audio) / SAMPLE_RATE
    segments = []
    for seg in segments_iter:
        if is_cancelled():
            raise Cancelled()
        text = seg.text.strip()
        if not text:
            continue
        segments.append(
            {
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": text,
                "words": [
                    {"start": round(w.start, 2), "end": round(w.end, 2), "word": w.word}
                    for w in (seg.words or [])
                ],
            }
        )
        on_progress(min(seg.end / duration, 1.0) if duration else 0.0, text)

    return {
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "duration": round(duration, 2),
        "segments": segments,
    }
