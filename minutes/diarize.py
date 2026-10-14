"""Speaker diarization (pyannote) and alignment of speakers onto Whisper words."""

from __future__ import annotations

import bisect
import os
import threading
from typing import Callable

import numpy as np

from .audio import SAMPLE_RATE
from .transcribe import Cancelled

PIPELINE_ID = "pyannote/speaker-diarization-3.1"

_lock = threading.Lock()
_pipeline = None
_pipeline_token: str | None = None


def get_pipeline(token: str):
    global _pipeline, _pipeline_token
    with _lock:
        if _pipeline is None or _pipeline_token != token:
            from pyannote.audio import Pipeline

            # PyTorch >= 2.6 defaults torch.load to weights_only=True, which rejects the
            # pyannote 3.x checkpoints (they pickle a TorchVersion and other metadata).
            # These come from pyannote's official, gated Hugging Face repos, so allow the
            # full load for this call only and restore the safe default afterwards.
            previous = os.environ.get("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD")
            os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
            try:
                pipeline = Pipeline.from_pretrained(PIPELINE_ID, use_auth_token=token)
            finally:
                if previous is None:
                    os.environ.pop("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", None)
                else:
                    os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = previous
            if pipeline is None:
                raise RuntimeError(
                    "Couldn't load the speaker model. Check your Hugging Face token and that "
                    "you accepted the terms for pyannote/speaker-diarization-3.1 and "
                    "pyannote/segmentation-3.0."
                )
            _pipeline, _pipeline_token = pipeline, token
        return _pipeline


def diarize(
    audio: np.ndarray,
    token: str,
    num_speakers: int,
    on_progress: Callable[[float, str], None],
    is_cancelled: Callable[[], bool],
) -> list[tuple[float, float, str]]:
    import torch

    pipeline = get_pipeline(token)
    # pyannote runs two heavy passes; weight them so the bar moves sensibly.
    weights = {"segmentation": (0.0, 0.35), "embeddings": (0.35, 0.95)}

    def hook(step_name, step_artifact, file=None, total=None, completed=None):
        if is_cancelled():
            raise Cancelled()
        if step_name in weights and total:
            lo, hi = weights[step_name]
            on_progress(lo + (hi - lo) * (completed or 0) / total, step_name)

    kwargs = {"num_speakers": num_speakers} if num_speakers else {}
    waveform = torch.from_numpy(np.ascontiguousarray(audio)).unsqueeze(0)
    annotation = pipeline({"waveform": waveform, "sample_rate": SAMPLE_RATE}, hook=hook, **kwargs)
    on_progress(1.0, "done")
    return [
        (float(turn.start), float(turn.end), str(label))
        for turn, _, label in annotation.itertracks(yield_label=True)
    ]


def assign_speakers(segments: list[dict], turns: list[tuple[float, float, str]]) -> list[dict]:
    """Label every word with the speaker whose turn overlaps it most, then split Whisper
    segments wherever the speaker changes. Labels become 'Speaker 1', 'Speaker 2'… in
    order of first appearance."""
    if not turns:
        return [{**s, "speaker": None} for s in segments]

    turns = sorted(turns)
    starts = [t[0] for t in turns]
    max_len = max(t[1] - t[0] for t in turns)

    def speaker_at(start: float, end: float) -> str:
        best, best_overlap = None, 0.0
        i = bisect.bisect_left(starts, start - max_len)
        while i < len(turns) and turns[i][0] <= end:
            t_start, t_end, label = turns[i]
            overlap = min(end, t_end) - max(start, t_start)
            if overlap > best_overlap:
                best, best_overlap = label, overlap
            i += 1
        if best is None:  # word fell in a gap: take the nearest turn
            mid = (start + end) / 2
            best = min(turns, key=lambda t: min(abs(mid - t[0]), abs(mid - t[1])))[2]
        return best

    names: dict[str, str] = {}

    def friendly(label: str) -> str:
        if label not in names:
            names[label] = f"Speaker {len(names) + 1}"
        return names[label]

    out = []
    for seg in segments:
        words = seg.get("words") or []
        if not words:
            out.append({**seg, "speaker": friendly(speaker_at(seg["start"], seg["end"]))})
            continue
        current, bucket = None, []
        for w in words:
            label = friendly(speaker_at(w["start"], max(w["end"], w["start"] + 0.01)))
            if current is not None and label != current and bucket:
                out.append(_piece(bucket, current))
                bucket = []
            current = label
            bucket.append(w)
        if bucket:
            out.append(_piece(bucket, current))
    return out


def _piece(words: list[dict], speaker: str) -> dict:
    return {
        "start": words[0]["start"],
        "end": words[-1]["end"],
        "text": "".join(w["word"] for w in words).strip(),
        "words": words,
        "speaker": speaker,
    }
