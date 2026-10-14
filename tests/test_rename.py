"""Renaming rewrites the folder and every file; it must never lose data."""

import json
from pathlib import Path

from minutes import export


def listing(folder: Path) -> set[str]:
    return {p.name for p in folder.iterdir()}


def saved(tmp_path, meeting, wav=False):
    wav_src = None
    if wav:
        wav_src = tmp_path / "src.wav"
        wav_src.write_bytes(b"RIFF fake wav")
    return export.write_meeting(meeting, tmp_path / "out", wav_src)


def renamed(m, name):
    return export.write_meeting({**m, "name": name}, Path(m["folder"]).parent)


def test_first_write_creates_all_files(tmp_path, meeting):
    m = saved(tmp_path, meeting, wav=True)
    assert listing(Path(m["folder"])) == set(m["files"])
    assert len(m["files"]) == 5


def test_case_only_rename_keeps_every_file(tmp_path, meeting):
    # Regression: on Windows this used to delete all files, including the WAV.
    m = saved(tmp_path, meeting, wav=True)
    m2 = renamed(m, m["name"].lower())
    folder = Path(m2["folder"])
    assert folder.name == m["name"].lower()
    assert listing(folder) == set(m2["files"])
    assert len(m2["files"]) == 5
    assert (folder / f"{m2['name']}_audio.wav").read_bytes() == b"RIFF fake wav"
    data = json.loads((folder / f"{m2['name']}.json").read_text(encoding="utf-8"))
    assert data["id"] == meeting["id"]


def test_case_only_rename_round_trip(tmp_path, meeting):
    m = saved(tmp_path, meeting)
    m = renamed(m, "notes")
    m = renamed(m, "NOTES")
    m = renamed(m, "Notes")
    assert Path(m["folder"]).name == "Notes"
    assert listing(Path(m["folder"])) == set(m["files"])


def test_rename_moves_wav(tmp_path, meeting):
    m = renamed(saved(tmp_path, meeting, wav=True), "New Name")
    assert (Path(m["folder"]) / "New Name_audio.wav").read_bytes() == b"RIFF fake wav"
    assert listing(Path(m["folder"])) == set(m["files"])


def test_rename_collision_gets_suffix(tmp_path, meeting):
    m = saved(tmp_path, meeting)
    (Path(m["folder"]).parent / "Taken").mkdir()
    m = renamed(m, "Taken")
    assert Path(m["folder"]).name == "Taken (2)"
    assert m["name"] == "Taken (2)"
    assert listing(Path(m["folder"])) == set(m["files"])


def test_rename_to_same_name_is_noop(tmp_path, meeting):
    m = saved(tmp_path, meeting)
    m2 = renamed(m, m["name"])
    assert m2["folder"] == m["folder"]
    assert listing(Path(m2["folder"])) == set(m2["files"])


def test_illegal_characters_are_stripped(tmp_path, meeting):
    m = renamed(saved(tmp_path, meeting), 'Bad:/\\*?"<>| name.')
    assert Path(m["folder"]).name == "Bad name"


def test_long_names_are_capped(tmp_path, meeting):
    m = renamed(saved(tmp_path, meeting), "x" * 300)
    assert len(Path(m["folder"]).name) <= 100
    assert listing(Path(m["folder"])) == set(m["files"])
