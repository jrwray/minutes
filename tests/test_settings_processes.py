"""Two copies of the app (e.g. Start.bat plus one on another port) share settings.json."""

import json
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SETUP = textwrap.dedent("""
    import sys, time
    from pathlib import Path
    sys.path.insert(0, {root!r})
    from minutes import config
    data = Path({data!r})
    config.DATA_DIR, config.WORK_DIR, config.SETTINGS_PATH = data, data / "work", data / "settings.json"
    start = {start!r}
    while time.time() < start:
        time.sleep(0.001)
""")

WRITER = "for i in range(30):\n    config.save({{{key!r}: {value!r}}})\n"
READER = "end = time.time() + 3\nwhile time.time() < end:\n    config.load()\n"


def run_all(scripts):
    procs = [subprocess.Popen([sys.executable, "-c", s], stderr=subprocess.PIPE) for s in scripts]
    errors = [p.communicate(timeout=120)[1].decode() for p in procs]
    assert all(p.returncode == 0 for p in procs), errors


def test_concurrent_saves_from_separate_processes(tmp_path):
    import time

    data = tmp_path / "data"
    values = {"language": "de", "vocabulary": "EcoRouter", "ollama_model": "qwen3:8b", "num_speakers": 3}
    start = time.time() + 2  # let every process start, then go at once
    setup = lambda: SETUP.format(root=str(ROOT), data=str(data), start=start)  # noqa: E731
    scripts = [setup() + WRITER.format(key=k, value=v) for k, v in values.items()]
    scripts.append(setup() + READER)  # a reader holding the file open makes Windows refuse replaces

    run_all(scripts)

    saved = json.loads((data / "settings.json").read_text(encoding="utf-8"))
    assert {k: saved[k] for k in values} == values
    assert not list(data.glob("settings.json.tmp-*"))
