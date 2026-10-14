"""The job queue and API, end to end, with fake engines (no models needed)."""

import time
from pathlib import Path

from minutes import config


def settings(api, **patch):
    assert api.post("/api/settings", json=patch).status_code == 200


def process(api, **patch):
    if patch:
        settings(api, **patch)
    job = api.wait(api.upload()["id"])
    assert job["status"] == "done", job
    return job, api.get(f"/api/meetings/{job['meeting_id']}").json()


def test_upload_produces_named_meeting_folder(api):
    job, m = process(api, summary_engine="ollama")
    folder = Path(m["folder"])
    assert m["name"] == "2026-10-14_Budget-Review"  # date from the file's lastModified + AI title
    assert folder.parent == Path(config.load()["output_dir"])
    assert {p.name for p in folder.iterdir()} == set(m["files"])
    assert "Welcome everyone" in (folder / f"{m['name']}_transcript.txt").read_text(encoding="utf-8")
    assert job["skipped"] == ["speakers"]


def test_upload_temp_file_is_removed(api, isolated):
    process(api)
    assert not any(config.WORK_DIR.rglob("*.mp4"))


def test_without_summary_uses_file_name(api):
    job, m = process(api, summary_engine="none")
    assert m["summary"] is None
    assert m["name"] == "2026-10-14_Call"
    assert "summary" in job["skipped"]


def test_summary_failure_is_a_warning_not_an_error(api):
    api.fakes.summary_fails = True
    job, m = process(api, summary_engine="ollama")
    assert any("Summary failed" in w for w in job["warnings"])
    assert m["summary"] is None and Path(m["folder"]).exists()


def test_keep_wav(api):
    _, m = process(api, keep_wav=True)
    assert (Path(m["folder"]) / f"{m['name']}_audio.wav").exists()


def test_speakers_are_labelled_and_renamable(api):
    _, m = process(api, diarization=True, hf_token="hf_test", summary_engine="ollama")
    assert m["speakers"] == {"Speaker 1": "Speaker 1", "Speaker 2": "Speaker 2"}
    assert [s["speaker"] for s in m["segments"]] == ["Speaker 1", "Speaker 2"]
    assert all("words" not in s for s in m["segments"])  # word timings aren't saved

    r = api.post(f"/api/meetings/{m['id']}", json={"speakers": {"Speaker 1": "Priya", "Speaker 2": "Sam"}})
    m2 = r.json()
    assert m2["speakers"] == {"Speaker 1": "Priya", "Speaker 2": "Sam"}
    assert m2["summary"]["action_items"][0]["owner"] == "Sam"
    assert "Sam reported" in m2["summary"]["overview"]
    txt = (Path(m2["folder"]) / f"{m2['name']}_transcript.txt").read_text(encoding="utf-8")
    assert "Priya:" in txt and "Sam:" in txt and "Speaker 1" not in txt


def test_rename_via_api(api):
    _, m = process(api)
    m2 = api.post(f"/api/meetings/{m['id']}", json={"name": "Q4 Planning"}).json()
    assert Path(m2["folder"]).name == "Q4 Planning"
    assert not Path(m["folder"]).exists()
    assert [x["name"] for x in api.get("/api/meetings").json()] == ["Q4 Planning"]


def test_resummarize_replaces_summary(api):
    _, m = process(api, summary_engine="none")
    job = api.post(f"/api/meetings/{m['id']}/summarize", json={"engine": "claude"}).json()
    assert api.wait(job["id"])["status"] == "done"
    m2 = api.get(f"/api/meetings/{m['id']}").json()
    assert m2["summary"]["title"] == "Budget Review"
    assert api.fakes.summary_calls[-1]["engine"] == "claude"


def test_failed_resummarize_keeps_old_summary(api):
    _, m = process(api, summary_engine="ollama")
    api.fakes.summary_fails = True
    job = api.wait(api.post(f"/api/meetings/{m['id']}/summarize", json={"engine": "ollama"}).json()["id"])
    assert job["status"] == "error" and "Ollama isn't running" in job["error"]
    assert api.get(f"/api/meetings/{m['id']}").json()["summary"] == m["summary"]


def test_resummarize_unknown_engine_rejected(api):
    _, m = process(api)
    assert api.post(f"/api/meetings/{m['id']}/summarize", json={"engine": "gpt"}).status_code == 400


def test_delete(api):
    _, m = process(api)
    assert api.delete(f"/api/meetings/{m['id']}").status_code == 200
    assert not Path(m["folder"]).exists()
    assert api.get("/api/meetings").json() == []
    assert api.get(f"/api/meetings/{m['id']}").status_code == 404
    assert api.delete(f"/api/meetings/{m['id']}").status_code == 404


def test_cancel_running_job(api):
    api.fakes.slow = True
    job = api.upload()
    while api.get("/api/jobs").json()[-1]["stage"] != "transcribe":
        time.sleep(0.01)
    assert api.post(f"/api/jobs/{job['id']}/cancel").status_code == 200
    assert api.wait(job["id"])["status"] == "cancelled"
    assert api.get("/api/meetings").json() == []


def test_cancel_queued_job(api):
    api.fakes.slow = True
    first, second = api.upload("a.mp4"), api.upload("b.mp4")
    assert api.post(f"/api/jobs/{second['id']}/cancel").status_code == 200
    assert api.wait(second["id"])["status"] == "cancelled"
    api.fakes.slow = False
    assert api.wait(first["id"])["status"] == "done"
    assert len(api.get("/api/meetings").json()) == 1


def test_dismiss_finished_job(api):
    job = api.wait(api.upload()["id"])
    api.delete(f"/api/jobs/{job['id']}")
    assert all(j["id"] != job["id"] for j in api.get("/api/jobs").json())
