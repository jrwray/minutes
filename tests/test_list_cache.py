"""The sidebar polls /api/meetings every few seconds; unchanged meetings must not be re-read."""

import shutil
from pathlib import Path

import pytest

from minutes import config, export


@pytest.fixture
def reads(monkeypatch):
    calls = []
    real = export.read_meeting

    def counting(path):
        calls.append(Path(path))
        return real(path)

    monkeypatch.setattr(export, "read_meeting", counting)
    return calls


def make(api, n):
    for i in range(n):
        assert api.wait(api.upload(f"call{i}.mp4")["id"])["status"] == "done"


def test_unchanged_meetings_are_not_reparsed(api, reads):
    make(api, 3)
    api.get("/api/meetings")
    reads.clear()
    for _ in range(5):
        assert len(api.get("/api/meetings").json()) == 3
    assert reads == []


def test_changed_meeting_is_reparsed(api, reads):
    make(api, 2)
    first = api.get("/api/meetings").json()[0]
    reads.clear()
    api.post(f"/api/meetings/{first['id']}", json={"name": "Renamed"})
    reads.clear()
    names = {m["name"] for m in api.get("/api/meetings").json()}
    assert "Renamed" in names
    assert len(reads) == 1  # only the renamed meeting


def test_external_changes_are_picked_up(api):
    make(api, 2)
    listed = api.get("/api/meetings").json()
    out = Path(config.load()["output_dir"])
    # Deleted in Explorer
    shutil.rmtree(out / listed[0]["name"])
    assert [m["id"] for m in api.get("/api/meetings").json()] == [listed[1]["id"]]
    # Unrelated folders and stray JSON files are ignored
    (out / "Holiday photos").mkdir()
    (out / "Holiday photos" / "album.json").write_text('{"photos": []}', encoding="utf-8")
    (out / "notes.json").write_text("{}", encoding="utf-8")
    assert len(api.get("/api/meetings").json()) == 1


def test_output_dir_change_switches_list(api, isolated):
    make(api, 1)
    api.post("/api/settings", json={"output_dir": str(isolated / "Elsewhere")})
    assert api.get("/api/meetings").json() == []
