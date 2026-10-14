"""Audio decoding (no ffmpeg CLI needed: faster-whisper ships PyAV)."""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SAMPLE_RATE = 16000


class AudioError(RuntimeError):
    """A file that can't be turned into audio, with a message fit for the UI."""


def load_audio(path: str | Path, display_name: str | None = None) -> np.ndarray:
    """Decode any audio/video file to 16 kHz mono float32."""
    import av
    from faster_whisper import decode_audio

    name = display_name or Path(path).name
    try:
        return decode_audio(str(path), sampling_rate=SAMPLE_RATE)
    except IndexError as exc:  # PyAV: the container has no audio stream
        raise AudioError(f"“{name}” has no audio track.") from exc
    except FileNotFoundError as exc:
        raise AudioError(f"“{name}” could not be found.") from exc
    except av.FFmpegError as exc:
        raise AudioError(
            f"“{name}” couldn't be read as audio or video. "
            "Try an MP4, MOV, MKV, M4A, MP3 or WAV file."
        ) from exc


def write_wav(audio: np.ndarray, path: str | Path) -> None:
    """Write 16 kHz mono 16-bit PCM — the format Whisper actually uses."""
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm.tobytes())
