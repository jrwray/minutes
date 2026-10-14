import httpx
import pytest

from minutes import summarize as sm


def test_parse_plain_json():
    raw = '{"title": "T", "overview": "O", "decisions": ["d"], "action_items": [{"task": "x", "owner": "", "due": ""}], "open_questions": [], "topics": [{"start": 12, "topic": "Intro"}]}'
    out = sm._parse(raw)
    assert out["title"] == "T" and out["topics"] == [{"start": 12.0, "topic": "Intro"}]


def test_parse_fenced_and_messy():
    raw = '```json\n{"title": " T ", "decisions": ["", "keep"], "action_items": [{"task": ""}, {"task": "do it", "owner": null}], "topics": [{"start": "bad", "topic": "x"}]}\n```'
    out = sm._parse(raw)
    assert out["title"] == "T"
    assert out["decisions"] == ["keep"]
    assert out["action_items"] == [{"task": "do it", "owner": "", "due": ""}]
    assert out["topics"] == [{"start": 0.0, "topic": "x"}]
    assert out["overview"] == "" and out["open_questions"] == []


def test_parse_garbage_raises_friendly_error():
    with pytest.raises(RuntimeError, match="malformed"):
        sm._parse("I'm sorry, I can't do that.")


def test_transcript_text_uses_current_speaker_names():
    segs = [{"start": 65, "end": 70, "text": "Hi", "speaker": "Speaker 1"}, {"start": 3700, "end": 3701, "text": "Bye", "speaker": None}]
    assert sm.transcript_text(segs, {"Speaker 1": "Priya"}) == "[01:05] Priya: Hi\n[1:01:40] Bye"


def test_empty_transcript_is_rejected():
    with pytest.raises(RuntimeError, match="empty"):
        sm.summarize([], {}, "2026-10-14", {}, "ollama", lambda *a: None, lambda: False)


def test_long_meetings_are_chunked(monkeypatch):
    calls = []

    def fake_chat(system, user, settings, schema, on_progress, is_cancelled, label):
        calls.append((label, schema is not None, len(user)))
        return '{"title": "Long"}' if schema else "- notes"

    monkeypatch.setattr(sm, "_ollama_chat", fake_chat)
    segs = [{"start": i, "end": i + 1, "text": "word " * 40, "speaker": None} for i in range(800)]
    out = sm.summarize(segs, {}, "2026-10-14", {}, "ollama", lambda *a: None, lambda: False)
    assert out["title"] == "Long"
    parts = [c for c in calls if c[0].startswith("Part")]
    assert len(parts) >= 2 and all(not c[1] for c in parts)
    assert calls[-1][0] == "Combining" and calls[-1][1]
    assert all(c[2] <= sm.CHUNK_CHARS + 500 for c in parts)


def test_short_meeting_is_one_call(monkeypatch):
    calls = []
    monkeypatch.setattr(sm, "_ollama_chat", lambda *a: calls.append(a) or '{"title": "Short"}')
    sm.summarize([{"start": 0, "end": 1, "text": "hi", "speaker": None}], {}, "d", {}, "ollama", lambda *a: None, lambda: False)
    assert len(calls) == 1


# ---------------------------------------------------------------- Claude error handling

def _api_error(cls, status, message):
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    return cls(message, response=httpx.Response(status, request=req), body={"error": {"message": message}})


class FakeAnthropic:
    """Records requests; raises/returns whatever the test queues up."""
    plan = []
    seen = []

    def __init__(self, **kwargs):
        FakeAnthropic.seen.append(("client", kwargs))
        self.messages = self
        self.beta = self

    def create(self, **kwargs):
        FakeAnthropic.seen.append(("create", kwargs))
        result = FakeAnthropic.plan.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class Msg:
    def __init__(self, text, stop_reason="end_turn"):
        self.stop_reason = stop_reason
        self.content = [type("B", (), {"type": "thinking"})(), type("B", (), {"type": "text", "text": text})()]


@pytest.fixture
def fake_claude(monkeypatch):
    import anthropic
    FakeAnthropic.plan, FakeAnthropic.seen = [], []
    monkeypatch.setattr(anthropic, "Anthropic", FakeAnthropic)
    return FakeAnthropic


SETTINGS = {"anthropic_api_key": "k", "claude_model": "claude-opus-5-5", "anthropic_workspace_id": ""}


def run_claude(settings=SETTINGS):
    return sm._claude("[00:00] hi", "2026-10-14", settings, lambda *a: None)


def test_claude_success_uses_fallbacks_and_ignores_thinking(fake_claude):
    fake_claude.plan = [Msg('{"title": "Hello"}')]
    assert run_claude()["title"] == "Hello"
    create = [kw for kind, kw in fake_claude.seen if kind == "create"][0]
    assert create["fallbacks"] == "default" and create["betas"] == ["server-side-fallback-2026-07-01"]
    assert create["output_config"]["format"]["type"] == "json_schema"


def test_claude_workspace_header_sent_when_set(fake_claude):
    fake_claude.plan = [Msg('{"title": "x"}')]
    run_claude({**SETTINGS, "anthropic_workspace_id": " wrkspc_123 "})
    client_kwargs = [kw for kind, kw in fake_claude.seen if kind == "client"][0]
    assert client_kwargs["default_headers"] == {"anthropic-workspace-id": "wrkspc_123"}


def test_claude_workspace_error_is_explained(fake_claude):
    import anthropic
    fake_claude.plan = [_api_error(anthropic.BadRequestError, 400, "This API key is not scoped to a workspace")]
    with pytest.raises(RuntimeError, match="Workspace ID"):
        run_claude()


def test_claude_falls_back_to_plain_request(fake_claude):
    import anthropic
    fake_claude.plan = [_api_error(anthropic.BadRequestError, 400, "fallbacks not supported"), Msg('{"title": "Plain"}')]
    assert run_claude()["title"] == "Plain"
    assert "fallbacks" not in [kw for kind, kw in fake_claude.seen if kind == "create"][1]


def test_claude_bad_key(fake_claude):
    import anthropic
    fake_claude.plan = [_api_error(anthropic.AuthenticationError, 401, "invalid x-api-key")]
    with pytest.raises(RuntimeError, match="rejected the API key"):
        run_claude()


def test_claude_refusal(fake_claude):
    fake_claude.plan = [Msg("", stop_reason="refusal")]
    with pytest.raises(RuntimeError, match="declined"):
        run_claude()
