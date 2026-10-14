"""Concurrent edits and interrupted writes must not lose or duplicate data."""

import json
import threading
from pathlib import Path

import pytest

from minutes import config, export


def make_meeting(api, **patch):
    if patch:
        api.post("/api/settings", json=patch)
    job = api.wait(api.upload()["id"])
    return api.get(f"/api/meetings/{job['meeting_id']}").json()


def start_blocked_resummarize(api, m):
    api.fakes.summary_gate, api.fakes.summary_started = threading.Event(), threading.Event()
    job = api.post(f"/api/meetings/{m['id']}/summarize", json={"engine": "ollama"}).json()
    assert api.fakes.summary_started.wait(5)
    return job


def test_rename_during_resummarize_keeps_one_folder(api):
    m = make_meeting(api, summary_engine="none")
    job = start_blocked_resummarize(api, m)
    renamed = api.post(f"/api/meetings/{m['id']}", json={"name": "Renamed Meanwhile"}).json()
    api.fakes.summary_gate.set()
    assert api.wait(job["id"])["status"] == "done"

    out = Path(config.load()["output_dir"])
    assert [p.name for p in out.iterdir()] == ["Renamed Meanwhile"]  # no resurrected old folder
    final = api.get(f"/api/meetings/{m['id']}").json()
    assert final["name"] == "Renamed Meanwhile" and final["summary"]["title"] == "Budget Review"
    assert renamed["folder"] == final["folder"]


def test_speaker_rename_during_resummarize_applies_to_new_summary(api):
    m = make_meeting(api, diarization=True, hf_token="hf_x", summary_engine="none")
    job = start_blocked_resummarize(api, m)
    api.post(f"/api/meetings/{m['id']}", json={"speakers": {"Speaker 2": "Sam"}})
    api.fakes.summary_gate.set()
    api.wait(job["id"])
    final = api.get(f"/api/meetings/{m['id']}").json()
    assert final["speakers"]["Speaker 2"] == "Sam"
    assert final["summary"]["action_items"][0]["owner"] == "Sam"


def test_delete_during_resummarize_is_refused(api):
    m = make_meeting(api, summary_engine="none")
    job = start_blocked_resummarize(api, m)
    assert api.delete(f"/api/meetings/{m['id']}").status_code == 409
    api.fakes.summary_gate.set()
    api.wait(job["id"])


def test_interrupted_write_keeps_previous_json(tmp_path, meeting, monkeypatch):
    m = export.write_meeting(meeting, tmp_path)
    json_path = Path(m["folder"]) / f"{m['name']}.json"
    before = json_path.read_text(encoding="utf-8")

    real_replace = export.os.replace

    def crash_on_json(src, dst):
        if str(dst).endswith(".json"):
            raise OSError("disk full")
        return real_replace(src, dst)

    monkeypatch.setattr(export.os, "replace", crash_on_json)
    with pytest.raises(OSError):
        export.write_meeting({**m, "summary": None}, tmp_path)

    assert json_path.read_text(encoding="utf-8") == before  # old version intact
    assert json.loads(before)["summary"] is not None
    assert not [p for p in Path(m["folder"]).iterdir() if ".tmp" in p.name]  # no temp debris


def test_concurrent_settings_saves_lose_nothing(isolated):
    keys = ["keep_wav", "diarization", "language", "vocabulary", "cpu_threads", "num_speakers", "ollama_model", "claude_model"]
    values = {"keep_wav": True, "diarization": True, "language": "de", "vocabulary": "x",
              "cpu_threads": 3, "num_speakers": 4, "ollama_model": "m", "claude_model": "c"}
    barrier = threading.Barrier(len(keys))

    def save(k):
        barrier.wait()
        for _ in range(20):
            config.save({k: values[k]})

    threads = [threading.Thread(target=save, args=(k,)) for k in keys]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    final = config.load()
    assert {k: final[k] for k in keys} == values
    assert json.loads(config.SETTINGS_PATH.read_text(encoding="utf-8"))  # valid JSON on disk
