import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


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
