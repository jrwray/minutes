"""Deleting a meeting moves it to the system's trash, and the UI uses the system's name for it."""

import os
import sys
from pathlib import Path

import pytest

from minutes import export


def test_trash_name_matches_the_platform():
    assert export.TRASH_NAME == ("Recycle Bin" if os.name == "nt" else "Trash")


def test_status_reports_trash_name(client):
    assert client.get("/api/status").json()["trash"] == export.TRASH_NAME


@pytest.mark.skipif(os.name == "nt" or sys.platform == "darwin", reason="freedesktop.org trash is Linux only")
def test_linux_trash_follows_freedesktop_spec(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "share"))
    monkeypatch.setattr(export.shutil, "which", lambda name: None)  # force the spec path, not gio
    for _ in range(2):  # same name twice: the second gets a suffix instead of overwriting
        meeting = tmp_path / "Transcripts" / "2026-10-20_Sync"
        meeting.mkdir(parents=True)
        (meeting / "notes.txt").write_text("hi", encoding="utf-8")
        export.to_recycle_bin(meeting)
        assert not meeting.exists()
    trash = tmp_path / "share" / "Trash"
    assert sorted(p.name for p in (trash / "files").iterdir()) == ["2026-10-20_Sync", "2026-10-20_Sync.2"]
    info = (trash / "info" / "2026-10-20_Sync.trashinfo").read_text(encoding="utf-8")
    assert info.startswith("[Trash Info]\nPath=/")
    assert "DeletionDate=" in info
    assert (trash / "files" / "2026-10-20_Sync" / "notes.txt").read_text(encoding="utf-8") == "hi"


def test_open_folder_uses_the_platform_file_manager(monkeypatch, tmp_path):
    calls = []
    if os.name == "nt":
        monkeypatch.setattr(os, "startfile", lambda p: calls.append(["startfile", str(p)]), raising=False)
    else:
        monkeypatch.setattr("subprocess.Popen", lambda args, **kw: calls.append(args))
    export.open_in_file_manager(tmp_path)
    expected = {"nt": "startfile"}.get(os.name, "open" if sys.platform == "darwin" else "xdg-open")
    assert calls == [[expected, str(Path(tmp_path))]]
