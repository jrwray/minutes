"""FastAPI app: JSON API + static UI, bound to localhost only."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config, summarize
from .jobs import Manager

STATIC = config.ROOT / "static"

app = FastAPI(title="Minutes", docs_url=None, redoc_url=None)
manager = Manager()


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-store"})


app.mount("/static", StaticFiles(directory=STATIC), name="static")


# ---------------------------------------------------------------- status & settings


@app.get("/api/status")
def status():
    from .transcribe import is_model_cached

    s = config.load()
    models = summarize.ollama_models(s["ollama_url"])
    return {
        "whisper": {"model": s["whisper_model"], "cached": is_model_cached(s["whisper_model"])},
        "speakers": {"enabled": bool(s["diarization"]), "ready": bool(s["hf_token"])},
        "ollama": {
            "running": models is not None,
            "models": models or [],
            "model": s["ollama_model"],
            "installed": bool(models) and (
                s["ollama_model"] in models or f"{s['ollama_model']}:latest" in models
            ),
        },
        "claude": {"ready": bool(s["anthropic_api_key"] or os.environ.get("ANTHROPIC_API_KEY")),
                   "model": s["claude_model"]},
        "engine": s["summary_engine"],
        "output_dir": s["output_dir"],
    }


@app.get("/api/settings")
def get_settings():
    return config.public(config.load())


@app.post("/api/settings")
def set_settings(patch: dict):
    return config.public(config.save(patch))


# ---------------------------------------------------------------- jobs


@app.post("/api/upload")
async def upload(file: UploadFile = File(...), last_modified: float | None = Form(None)):
    config.WORK_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix[:10] or ".bin"
    dest = config.WORK_DIR / f"{uuid.uuid4().hex}{suffix}"
    with dest.open("wb") as out:
        while chunk := await file.read(8 * 1024 * 1024):
            out.write(chunk)
    job = manager.submit_file(dest, file.filename or dest.name, last_modified)
    return job.public()


@app.get("/api/jobs")
def jobs():
    return manager.list_jobs()


@app.post("/api/jobs/{job_id}/cancel")
def cancel(job_id: str):
    if not manager.cancel(job_id):
        raise HTTPException(404, "No running job with that id")
    return {"ok": True}


@app.delete("/api/jobs/{job_id}")
def dismiss(job_id: str):
    manager.dismiss(job_id)
    return {"ok": True}


# ---------------------------------------------------------------- meetings


@app.get("/api/meetings")
def meetings():
    return manager.list_meetings()


@app.get("/api/meetings/{meeting_id}")
def meeting(meeting_id: str):
    m = manager.get_meeting(meeting_id)
    if not m:
        raise HTTPException(404, "Meeting not found")
    return m


class MeetingPatch(BaseModel):
    name: str | None = None
    speakers: dict[str, str] | None = None


@app.post("/api/meetings/{meeting_id}")
def update_meeting(meeting_id: str, patch: MeetingPatch):
    try:
        return manager.update_meeting(meeting_id, patch.name, patch.speakers)
    except KeyError:
        raise HTTPException(404, "Meeting not found")
    except OSError as exc:
        raise HTTPException(409, f"Couldn't rename: {exc.strerror or exc}. Is a file open in another app?")


class SummarizeRequest(BaseModel):
    engine: str


@app.post("/api/meetings/{meeting_id}/summarize")
def resummarize(meeting_id: str, req: SummarizeRequest):
    if req.engine not in ("ollama", "claude"):
        raise HTTPException(400, "Unknown engine")
    try:
        return manager.submit_summary(meeting_id, req.engine).public()
    except KeyError:
        raise HTTPException(404, "Meeting not found")


@app.post("/api/meetings/{meeting_id}/open")
def open_folder(meeting_id: str):
    m = manager.get_meeting(meeting_id)
    if not m:
        raise HTTPException(404, "Meeting not found")
    os.startfile(m["folder"])  # noqa: S606 — local desktop app
    return {"ok": True}


@app.post("/api/open-output")
def open_output():
    folder = Path(config.load()["output_dir"])
    folder.mkdir(parents=True, exist_ok=True)
    os.startfile(folder)
    return {"ok": True}
