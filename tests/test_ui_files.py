import pytest


@pytest.mark.parametrize("path", ["/", "/static/app.js", "/static/app.css"])
def test_ui_files_are_revalidated(client, path):
    # After an update the browser must not keep running the old UI (it would, for
    # example, lack the X-Minutes header and every save would be rejected).
    r = client.get(path)
    assert r.status_code == 200
    assert r.headers["cache-control"] == "no-cache"


def test_unchanged_file_is_a_304(client):
    etag = client.get("/static/app.js").headers["etag"]
    assert client.get("/static/app.js", headers={"If-None-Match": etag}).status_code == 304


def test_ui_sends_the_write_header():
    from pathlib import Path

    js = (Path(__file__).resolve().parent.parent / "static" / "app.js").read_text(encoding="utf-8")
    assert '"X-Minutes": "1"' in js and 'setRequestHeader("X-Minutes", "1")' in js
