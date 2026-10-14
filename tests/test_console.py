import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_logging_non_ascii_on_legacy_console_does_not_fail():
    # Simulate a Windows console on code page 1252, then log text it can't encode.
    code = (
        "import logging, minutes.__main__ as m; m.utf8_console();"
        "logging.basicConfig(level=logging.INFO);"
        "logging.error('Settings → Summary · Café · 会議');"
        "print('ok →')"
    )
    env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True)
    # Without the fix, print() raises UnicodeEncodeError and log lines come out as "→".
    assert r.returncode == 0
    assert b"Logging error" not in r.stderr
    assert "ok →" in r.stdout.decode("utf-8")
    assert "Settings → Summary · Café · 会議" in r.stderr.decode("utf-8")
