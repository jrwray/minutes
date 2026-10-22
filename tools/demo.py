"""Run the Minutes UI with a sample meeting and stand-in engines. No models, GPU or keys.

    uv run python tools/demo.py [--port 7861]

Useful for trying the interface, working on the front end, and taking screenshots.
Everything goes to a temporary folder that is deleted on exit.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# A made-up product meeting. Times are in seconds.
SAMPLE = [
    ("SPEAKER_00", 0.0, "Okay, let's get started. Three things today: the beta feedback, the pricing page, and the launch date."),
    ("SPEAKER_01", 7.5, "Beta first. We had forty-two testers, and the top request by far was offline mode."),
    ("SPEAKER_01", 14.0, "Second was faster search. Nobody complained about the editor, which is a nice change."),
    ("SPEAKER_02", 20.5, "Offline mode is bigger than it sounds. Sync conflicts alone are probably two weeks."),
    ("SPEAKER_00", 27.0, "Then it's not in the launch. Let's put it first on the list after launch and say so in the release notes."),
    ("SPEAKER_02", 34.0, "Search I can do this sprint. The index is already there, it's mostly the ranking."),
    ("SPEAKER_00", 40.0, "Great. Pricing page next. Priya, where are we?"),
    ("SPEAKER_01", 44.5, "The draft is up. Two tiers, plus a team plan. Legal still has to look at the refund wording."),
    ("SPEAKER_00", 51.0, "Can you get that to legal by Wednesday?"),
    ("SPEAKER_01", 53.5, "Yes, I'll send it tomorrow morning."),
    ("SPEAKER_02", 57.0, "On the date: if search lands this sprint, the twelfth still works for me."),
    ("SPEAKER_00", 62.5, "Then we hold the twelfth. If search slips, we decide on Friday whether to move it."),
]
DURATION = 70.0
NAMES = {"Speaker 1": "Dana", "Speaker 2": "Priya", "Speaker 3": "Marco"}


def segments():
    out = []
    for i, (_, start, text) in enumerate(SAMPLE):
        end = SAMPLE[i + 1][1] - 0.5 if i + 1 < len(SAMPLE) else DURATION
        out.append({"start": start, "end": end, "text": text,
                    "words": [{"start": start, "end": end, "word": " " + text}]})
    return out


def install_fakes():
    import numpy as np

    from minutes import audio, diarize, export, summarize, transcribe

    def fake_transcribe(_audio, _settings, on_progress, is_cancelled):
        for i in range(20):
            on_progress((i + 1) / 20, SAMPLE[min(i, len(SAMPLE) - 1)][2][:60])
            time.sleep(0.05)
        return {"language": "en", "language_probability": 0.99, "duration": DURATION, "segments": segments()}

    def fake_diarize(_audio, _token, _n, on_progress, is_cancelled):
        turns = []
        for i, (spk, start, _) in enumerate(SAMPLE):
            end = SAMPLE[i + 1][1] if i + 1 < len(SAMPLE) else DURATION
            turns.append((start, end, spk))
        on_progress(1.0, "")
        return turns

    def fake_summarize(_segments, speakers, _date, _settings, _engine, on_progress, is_cancelled):
        name = lambda k: speakers.get(k, k)  # noqa: E731
        return {
            "title": "Beta Feedback and Launch Plan",
            "overview": (f"{name('Speaker 2')} shared beta results: offline mode was the top request and faster search "
                         f"second. The team kept offline mode out of the launch, scheduled search for this sprint, "
                         f"and held the launch date, with a check on Friday."),
            "decisions": ["Offline mode ships after launch, first on the list, and the release notes say so.",
                          "Launch stays on the 12th unless search slips."],
            "action_items": [
                {"task": "Finish search ranking", "owner": name("Speaker 3"), "due": "End of sprint"},
                {"task": "Send pricing page draft to legal", "owner": name("Speaker 2"), "due": "Tomorrow"},
                {"task": "Decide whether to move the launch", "owner": name("Speaker 1"), "due": "Friday"},
            ],
            "open_questions": ["Refund wording on the pricing page (with legal)."],
            "topics": [{"start": 0.0, "topic": "Agenda"}, {"start": 7.5, "topic": "Beta feedback"},
                       {"start": 40.0, "topic": "Pricing page"}, {"start": 57.0, "topic": "Launch date"}],
        }

    audio.load_audio = lambda path, display_name=None: np.zeros(int(16000 * DURATION), dtype="float32")
    transcribe.transcribe = fake_transcribe
    transcribe.is_model_cached = lambda name: True
    diarize.diarize = fake_diarize
    summarize.summarize = fake_summarize
    summarize.ollama_models = lambda url: ["qwen2.5:7b"]  # show Ollama as ready
    export.to_recycle_bin = lambda p: shutil.rmtree(p, ignore_errors=True)


def seed_meeting(port: int) -> None:
    """Upload a placeholder file, wait for the fake pipeline, then name the speakers."""
    import httpx

    base = f"http://127.0.0.1:{port}"
    headers = {"X-Minutes": "1", "Origin": base}
    for _ in range(50):
        try:
            httpx.get(f"{base}/api/status", timeout=1)
            break
        except httpx.HTTPError:
            time.sleep(0.2)
    httpx.post(f"{base}/api/upload", files={"file": ("2026-10-20 product sync.m4a", b"demo", "audio/mp4")},
               headers=headers, timeout=10)
    for _ in range(100):
        meetings = httpx.get(f"{base}/api/meetings", timeout=5).json()
        items = meetings if isinstance(meetings, list) else meetings.get("meetings", [])
        if items:
            mid = items[0]["id"]
            httpx.post(f"{base}/api/meetings/{mid}", json={"speakers": NAMES}, headers=headers, timeout=10)
            return
        time.sleep(0.2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=7861)
    args = parser.parse_args()

    from minutes import config

    tmp = Path(tempfile.mkdtemp(prefix="minutes-demo-"))
    data = tmp / "data"
    config.DATA_DIR, config.WORK_DIR, config.SETTINGS_PATH = data, data / "work", data / "settings.json"
    config.save({"output_dir": str(tmp / "Transcripts"), "summary_engine": "ollama",
                 "diarization": True, "hf_token": "demo", "device": "cpu",
                 "ollama_model": "qwen2.5:7b"})
    install_fakes()

    import uvicorn

    threading.Thread(target=seed_meeting, args=(args.port,), daemon=True).start()
    print(f"\n  Minutes demo at http://127.0.0.1:{args.port}  (sample data, stand-in engines)\n")
    try:
        uvicorn.run("minutes.server:app", host="127.0.0.1", port=args.port, log_level="warning")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
