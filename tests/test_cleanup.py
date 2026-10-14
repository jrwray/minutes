import os
import subprocess
import sys
import time

from minutes import config, jobs


def dead_pid() -> int:
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    return p.pid


def test_leftovers_from_dead_runs_are_removed(isolated):
    work = config.WORK_DIR
    dead = work / f"run-{dead_pid()}"
    alive = work / f"run-{os.getpid()}"
    for d in (dead, alive):
        d.mkdir(parents=True)
        (d / "upload.mp4").write_bytes(b"x")
    old_loose, new_loose = work / "old.mp4", work / "new.mp4"
    old_loose.write_bytes(b"x")
    new_loose.write_bytes(b"x")
    two_hours_ago = time.time() - 7200
    os.utime(old_loose, (two_hours_ago, two_hours_ago))

    jobs.clean_work_dir()

    assert not dead.exists()
    assert (alive / "upload.mp4").exists()  # a running copy's queue is left alone
    assert not old_loose.exists() and new_loose.exists()


def test_other_running_process_is_kept(isolated):
    p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        other = config.WORK_DIR / f"run-{p.pid}"
        other.mkdir(parents=True)
        (other / "upload.mp4").write_bytes(b"x")
        jobs.clean_work_dir()
        assert (other / "upload.mp4").exists()
    finally:
        p.kill()
        p.wait()


def test_cleanup_runs_on_startup(isolated):
    from fastapi.testclient import TestClient

    from minutes import server

    leftover = config.WORK_DIR / f"run-{dead_pid()}"
    leftover.mkdir(parents=True)
    with TestClient(server.app, base_url="http://127.0.0.1:7860"):
        pass
    assert not leftover.exists()


def test_uploads_go_to_this_process_folder(api, monkeypatch):
    from minutes import audio

    seen = []
    real = api.fakes.load_audio
    monkeypatch.setattr(audio, "load_audio", lambda path, name=None: seen.append(path) or real(path, name))
    api.wait(api.upload()["id"])
    assert seen and seen[0].parent == config.WORK_DIR / f"run-{os.getpid()}"
    assert not seen[0].exists()  # removed once processed
