"""Audio decoding (no ffmpeg CLI needed: faster-whisper ships PyAV)."""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SAMPLE_RATE = 16000


def load_audio(path: str | Path) -> np.ndarray:
    """Decode any audio/video file to 16 kHz mono float32."""
    from faster_whisper import decode_audio

    return decode_audio(str(path), sampling_rate=SAMPLE_RATE)


def write_wav(audio: np.ndarray, path: str | Path) -> None:
    """Write 16 kHz mono 16-bit PCM — the format Whisper actually uses."""
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm.tobytes())
