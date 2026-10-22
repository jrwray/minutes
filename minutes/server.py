"""FastAPI app: JSON API + static UI, bound to localhost only."""

from __future__ import annotations

import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import config, export, summarize
from .jobs import Manager, clean_work_dir

STATIC = config.ROOT / "static"
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

@asynccontextmanager
async def lifespan(_app: FastAPI):
    clean_work_dir()
    yield


app = FastAPI(title="Minutes", docs_url=None, redoc_url=None, lifespan=lifespan)
manager = Manager()


# ---------------------------------------------------------------- request protection
# The server only listens on 127.0.0.1, but any web page open in the user's browser can
# still send requests to it. Two checks keep other sites out:
#  1. Host allowlist: defeats DNS rebinding (a hostile domain re-pointed at 127.0.0.1
#     would otherwise be able to read transcripts).
#  2. State-changing requests from a browser must be same-origin and carry the custom
#     X-Minutes header, which a cross-site page can't add without a CORS preflight that
#     this server never grants.
# Cross-site attacks can only come from a browser, and browsers mark every request with
# Sec-Fetch-Site (and Origin on cross-origin writes); pages can't remove those. Requests
# with neither are from scripts (curl, Python) and don't need the header.


@app.middleware("http")
async def same_origin_writes(request: Request, call_next):
    if request.method in UNSAFE_METHODS:
        origin = request.headers.get("origin")
        fetch_site = request.headers.get("sec-fetch-site")
        if origin is not None and urlsplit(origin).netloc != request.headers.get("host", ""):
            return JSONResponse({"detail": "Cross-site request blocked."}, status_code=403)
        if fetch_site is not None and fetch_site != "same-origin":
            return JSONResponse({"detail": "Cross-site request blocked."}, status_code=403)
        from_browser = origin is not None or fetch_site is not None
        if from_browser and request.headers.get("x-minutes") != "1":
            return JSONResponse({"detail": "Missing X-Minutes header."}, status_code=403)
    return await call_next(request)


@app.middleware("http")
async def revalidate_ui_files(request: Request, call_next):
    # Without this, browsers cache app.js/app.css heuristically, and after an update
    # the old UI keeps running against the new server. "no-cache" means "check first";
    # unchanged files come back as a tiny 304.
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"
    return response


app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")


# ---------------------------------------------------------------- status & settings


@app.get("/api/status")
def status():
    from .transcribe import is_model_cached

    from . import device

    s = config.load()
    models = summarize.ollama_models(s["ollama_url"])
    return {
        "whisper": {"model": s["whisper_model"], "cached": is_model_cached(s["whisper_model"])},
        "device": {
            "setting": s["device"],  # "" until the user picks one
            "active": device.resolve(s["device"] or "cpu"),
            "cpu": device.cpu_name(),
            "gpu": device.gpu_info(),
        },
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
        "trash": export.TRASH_NAME,
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
    suffix = Path(file.filename or "").suffix[:10] or ".bin"
    dest = config.run_dir() / f"{uuid.uuid4().hex}{suffix}"
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


@app.delete("/api/meetings/{meeting_id}")
def delete_meeting(meeting_id: str):
    try:
        manager.delete_meeting(meeting_id)
    except KeyError:
        raise HTTPException(404, "Meeting not found")
    except (RuntimeError, OSError) as exc:
        raise HTTPException(409, str(exc))
    return {"ok": True}


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
    export.open_in_file_manager(Path(m["folder"]))
    return {"ok": True}


@app.post("/api/open-output")
def open_output():
    folder = Path(config.load()["output_dir"])
    folder.mkdir(parents=True, exist_ok=True)
    export.open_in_file_manager(folder)
    return {"ok": True}
