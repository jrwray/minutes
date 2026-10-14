"""Meeting summaries via Ollama (local) or Claude (Anthropic API)."""

from __future__ import annotations

import json
from typing import Callable

import httpx

from .transcribe import Cancelled

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Specific 3-6 word title naming what the meeting was about, e.g. "
            "'EcoRouter Partnership Intro Call'. Never generic ('Meeting Notes', 'Team Meeting'). No date.",
        },
        "overview": {"type": "string", "description": "2-4 sentence overview."},
        "decisions": {"type": "array", "items": {"type": "string"}},
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "owner": {"type": "string", "description": "Person responsible, or empty."},
                    "due": {"type": "string", "description": "Due date as said, or empty."},
                },
                "required": ["task", "owner", "due"],
                "additionalProperties": False,
            },
        },
        "open_questions": {"type": "array", "items": {"type": "string"}},
        "topics": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {
                        "type": "number",
                        "description": "Seconds from the start where the topic begins.",
                    },
                    "topic": {"type": "string"},
                },
                "required": ["start", "topic"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["title", "overview", "decisions", "action_items", "open_questions", "topics"],
    "additionalProperties": False,
}

SYSTEM = """You write concise, accurate meeting notes from transcripts.
Rules:
- The title becomes the file name, so make it specific to this meeting's subject.
- Use only what is in the transcript. Never invent names, dates, numbers or decisions.
- Refer to people by the speaker names shown in the transcript.
- Decisions are things the group agreed on. Action items are concrete follow-ups.
- Leave owner/due empty when the transcript doesn't say.
- Topics: the main agenda items in order, with the second they start (from the [mm:ss] stamps).
- Lists may be empty when nothing fits. Keep every item to one sentence.
- Respond with JSON matching the schema."""

# ~4 chars per token; keep chunks well inside a 32k context for local models.
CHUNK_CHARS = 60_000


def fmt_time(seconds: float) -> str:
    s = int(seconds)
    h, m, s = s // 3600, (s % 3600) // 60, s % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def transcript_text(segments: list[dict], speakers: dict[str, str]) -> str:
    lines = []
    for seg in segments:
        who = speakers.get(seg.get("speaker") or "", seg.get("speaker"))
        prefix = f"{who}: " if who else ""
        lines.append(f"[{fmt_time(seg['start'])}] {prefix}{seg['text']}")
    return "\n".join(lines)


def _user_prompt(transcript: str, meeting_date: str, notes: bool = False) -> str:
    if notes:
        return (
            "Below are notes from consecutive parts of one meeting. Combine them into the "
            f"final meeting summary.\nMeeting date: {meeting_date}\n\n{transcript}"
        )
    return f"Meeting date: {meeting_date}\n\nTranscript:\n{transcript}"


def summarize(
    segments: list[dict],
    speakers: dict[str, str],
    meeting_date: str,
    settings: dict,
    engine: str,
    on_progress: Callable[[float, str], None],
    is_cancelled: Callable[[], bool],
) -> dict:
    text = transcript_text(segments, speakers)
    if not text.strip():
        raise RuntimeError("The transcript is empty — nothing to summarize.")
    if engine == "claude":
        return _claude(text, meeting_date, settings, on_progress)
    if engine == "ollama":
        return _ollama_summary(text, meeting_date, settings, on_progress, is_cancelled)
    raise RuntimeError(f"Unknown summary engine: {engine}")


# ---------------------------------------------------------------- Ollama


def ollama_models(url: str) -> list[str] | None:
    """Installed model names, or None if Ollama isn't running."""
    try:
        r = httpx.get(f"{url.rstrip('/')}/api/tags", timeout=1.5)
        r.raise_for_status()
        return sorted(m["name"] for m in r.json().get("models", []))
    except Exception:
        return None


def _ollama_chat(
    system: str,
    user: str,
    settings: dict,
    schema: dict | None,
    on_progress: Callable[[float, str], None],
    is_cancelled: Callable[[], bool],
    label: str,
) -> str:
    url = settings["ollama_url"].rstrip("/")
    est_tokens = (len(system) + len(user)) // 4 + 3000
    num_ctx = min(32768, max(8192, 1 << (est_tokens - 1).bit_length()))
    body = {
        "model": settings["ollama_model"],
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": True,
        "options": {"temperature": 0.2, "num_ctx": num_ctx},
    }
    if schema:
        body["format"] = schema
    out: list[str] = []
    on_progress(0.0, f"{label}: reading transcript…")
    try:
        with httpx.stream("POST", f"{url}/api/chat", json=body, timeout=httpx.Timeout(30, read=1800)) as r:
            if r.status_code == 404:
                raise RuntimeError(
                    f"Ollama model '{settings['ollama_model']}' isn't installed. "
                    f"Run: ollama pull {settings['ollama_model']}"
                )
            r.raise_for_status()
            for line in r.iter_lines():
                if is_cancelled():
                    raise Cancelled()
                if not line:
                    continue
                chunk = json.loads(line)
                if chunk.get("error"):
                    raise RuntimeError(f"Ollama: {chunk['error']}")
                out.append(chunk.get("message", {}).get("content", ""))
                words = len("".join(out).split())
                on_progress(min(0.95, words / 600), f"{label}: writing… {words} words")
                if chunk.get("done"):
                    break
    except httpx.ConnectError as exc:
        raise RuntimeError("Ollama isn't running. Start the Ollama app and try again.") from exc
    return "".join(out)


def _ollama_summary(text, meeting_date, settings, on_progress, is_cancelled) -> dict:
    if len(text) <= CHUNK_CHARS:
        raw = _ollama_chat(
            SYSTEM, _user_prompt(text, meeting_date), settings, SCHEMA, on_progress, is_cancelled, "Summary"
        )
        return _parse(raw)

    # Long meeting: summarize parts into notes, then combine the notes.
    chunks, current = [], []
    size = 0
    for line in text.splitlines():
        if size + len(line) > CHUNK_CHARS and current:
            chunks.append("\n".join(current))
            current, size = [], 0
        current.append(line)
        size += len(line) + 1
    if current:
        chunks.append("\n".join(current))

    notes = []
    for i, chunk in enumerate(chunks, 1):
        part = _ollama_chat(
            "Write detailed bullet-point notes of this meeting excerpt: topics with their "
            "[mm:ss] start times, decisions, action items with owners/dates, open questions. "
            "Use only what is said.",
            chunk,
            settings,
            None,
            on_progress,
            is_cancelled,
            f"Part {i}/{len(chunks)}",
        )
        notes.append(f"## Part {i}\n{part}")
    raw = _ollama_chat(
        SYSTEM,
        _user_prompt("\n\n".join(notes), meeting_date, notes=True),
        settings,
        SCHEMA,
        on_progress,
        is_cancelled,
        "Combining",
    )
    return _parse(raw)


# ---------------------------------------------------------------- Claude


def _claude(text, meeting_date, settings, on_progress) -> dict:
    import anthropic

    key = settings.get("anthropic_api_key") or None
    workspace = (settings.get("anthropic_workspace_id") or "").strip()
    client = anthropic.Anthropic(
        api_key=key,
        timeout=600,
        default_headers={"anthropic-workspace-id": workspace} if workspace else None,
    )
    on_progress(0.1, "Summary: sent to Claude…")
    request = dict(
        model=settings.get("claude_model") or "claude-opus-5-5",
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": _user_prompt(text, meeting_date)}],
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
    )
    try:
        # Server-side fallback: if a safety classifier declines, the API retries on
        # another model inside the same call.
        response = client.beta.messages.create(
            betas=["server-side-fallback-2026-07-01"], fallbacks="default", **request
        )
    except anthropic.BadRequestError as exc:
        if "workspace" in str(exc).lower():
            raise _workspace_error() from exc
        # Model or account without fallback support: retry as a plain request.
        try:
            response = client.messages.create(**request)
        except anthropic.APIError as retry_exc:
            raise _claude_error(retry_exc) from retry_exc
    except anthropic.APIError as exc:
        raise _claude_error(exc) from exc

    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined to summarize this transcript.")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Claude's summary was cut off (too long).")
    raw = "".join(b.text for b in response.content if b.type == "text")
    on_progress(1.0, "Summary: done")
    return _parse(raw)


def _workspace_error() -> RuntimeError:
    return RuntimeError(
        "This Anthropic key isn't tied to a workspace. Add your Workspace ID in Settings → Summary, "
        "or create a key inside a workspace at console.anthropic.com."
    )


def _claude_error(exc) -> RuntimeError:
    import anthropic

    if isinstance(exc, anthropic.AuthenticationError):
        return RuntimeError("Claude rejected the API key. Check it in Settings.")
    if isinstance(exc, anthropic.APIConnectionError):
        return RuntimeError("Couldn't reach the Claude API. Check your internet connection.")
    if isinstance(exc, anthropic.RateLimitError):
        return RuntimeError("Claude rate limit hit. Wait a minute and re-summarize.")
    if "workspace" in str(exc).lower():
        return _workspace_error()
    message = getattr(exc, "message", None) or str(exc)
    return RuntimeError(f"Claude API error: {message}")


# ---------------------------------------------------------------- helpers


def _parse(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw[raw.find("{") :]
    try:
        data = json.loads(raw[raw.find("{") : raw.rfind("}") + 1])
    except (ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError("The summary model returned malformed output. Try again.") from exc
    out = {
        "title": str(data.get("title") or "").strip(),
        "overview": str(data.get("overview") or "").strip(),
        "decisions": [str(x).strip() for x in data.get("decisions") or [] if str(x).strip()],
        "action_items": [],
        "open_questions": [str(x).strip() for x in data.get("open_questions") or [] if str(x).strip()],
        "topics": [],
    }
    for item in data.get("action_items") or []:
        if isinstance(item, dict) and str(item.get("task") or "").strip():
            out["action_items"].append(
                {k: str(item.get(k) or "").strip() for k in ("task", "owner", "due")}
            )
    for topic in data.get("topics") or []:
        if isinstance(topic, dict) and str(topic.get("topic") or "").strip():
            try:
                start = float(topic.get("start") or 0)
            except (TypeError, ValueError):
                start = 0.0
            out["topics"].append({"start": start, "topic": str(topic["topic"]).strip()})
    return out
