"""Watch folder: only new, finished recordings are queued, once, from a copy."""

import os

from minutes import config
from minutes.watcher import FolderWatcher


def _setup(isolated):
    inbox = isolated / "Recordings"
    inbox.mkdir()
    submitted = []
    watcher = FolderWatcher(lambda path, name, mtime_ms: submitted.append((path, name, mtime_ms)), poll_seconds=0)
    return inbox, watcher, submitted


def _write(path, data=b"x" * 2048):
    path.write_bytes(data)


def test_off_until_a_folder_is_set(isolated):
    inbox, watcher, submitted = _setup(isolated)
    _write(inbox / "call.m4a")
    assert watcher.check() == [] and watcher.check() == []
    assert submitted == []


def test_existing_files_are_ignored_and_new_ones_queued_once_stable(isolated):
    inbox, watcher, submitted = _setup(isolated)
    _write(inbox / "old.mp4")
    config.save({"watch_dir": str(inbox)})
    watcher.check()  # starts watching: old.mp4 is remembered, not queued
    _write(inbox / "new.mp4")
    _write(inbox / "notes.txt")  # not media
    assert watcher.check() == []  # first sighting: wait for the size to settle
    assert [p.name for p in watcher.check()] == ["new.mp4"]
    assert watcher.check() == []  # never twice
    assert [name for _, name, _ in submitted] == ["new.mp4"]


def test_growing_file_waits_until_it_stops_changing(isolated):
    inbox, watcher, submitted = _setup(isolated)
    config.save({"watch_dir": str(inbox)})
    watcher.check()
    rec = inbox / "obs.mkv"
    _write(rec, b"x" * 100)
    watcher.check()
    _write(rec, b"x" * 200)  # still recording
    assert watcher.check() == []
    assert [p.name for p in watcher.check()] == ["obs.mkv"]


def test_original_is_kept_and_a_copy_is_queued(isolated):
    inbox, watcher, submitted = _setup(isolated)
    config.save({"watch_dir": str(inbox)})
    watcher.check()
    rec = inbox / "meeting.m4a"
    _write(rec, b"audio-bytes" * 300)
    os.utime(rec, (1_760_000_000, 1_760_000_000))
    watcher.check()
    watcher.check()
    copy, name, mtime_ms = submitted[0]
    assert rec.exists() and copy != rec
    assert copy.read_bytes() == rec.read_bytes()
    assert copy.parent == config.run_dir()
    assert mtime_ms == 1_760_000_000_000  # meeting date comes from the recording, not today


def test_remembered_across_restarts(isolated):
    inbox, watcher, submitted = _setup(isolated)
    config.save({"watch_dir": str(inbox)})
    watcher.check()
    _write(inbox / "a.wav")
    watcher.check()
    watcher.check()
    again = FolderWatcher(lambda *a: submitted.append(a), poll_seconds=0)
    again.check()  # sees the folder "for the first time" this run
    _write(inbox / "b.wav")
    again.check()
    again.check()
    assert [s[1] for s in submitted] == ["a.wav", "b.wav"]


def test_setting_round_trips_through_the_api(client, isolated):
    folder = str(isolated / "Recordings")
    assert client.post("/api/settings", json={"watch_dir": folder}).json()["watch_dir"] == folder
