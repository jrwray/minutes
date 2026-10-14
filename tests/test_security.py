"""Other web pages open in the user's browser must not be able to use the local API."""

import pytest


def test_same_origin_requests_work(client):
    assert client.get("/api/settings").status_code == 200
    r = client.post("/api/settings", json={"keep_wav": True}, headers={"Origin": "http://127.0.0.1:7860"})
    assert r.status_code == 200


@pytest.mark.parametrize("host", ["evil.example", "evil.example:7860", "127.0.0.1.evil.example"])
def test_foreign_host_is_rejected(client, host):
    # DNS rebinding: a hostile domain resolving to 127.0.0.1 sends its own Host header.
    assert client.get("/api/meetings", headers={"Host": host}).status_code == 400
    assert client.get("/api/settings", headers={"Host": host}).status_code == 400


def test_localhost_host_is_allowed(client):
    assert client.get("/api/meetings", headers={"Host": "localhost:7860"}).status_code == 200


@pytest.mark.parametrize("method,path", [
    ("POST", "/api/settings"),
    ("POST", "/api/upload"),
    ("POST", "/api/open-output"),
    ("POST", "/api/meetings/abc/open"),
    ("DELETE", "/api/meetings/abc"),
    ("DELETE", "/api/jobs/abc"),
])
def test_writes_without_header_are_blocked(client, method, path):
    r = client.request(method, path, headers={"X-Minutes": ""})
    assert r.status_code == 403


def test_cross_origin_write_is_blocked_even_with_header(client):
    r = client.post("/api/settings", json={"keep_wav": True}, headers={"Origin": "https://evil.example"})
    assert r.status_code == 403


def test_cross_site_form_upload_is_blocked(client):
    # What an <form enctype="multipart/form-data"> on another site would send.
    r = client.post(
        "/api/upload",
        files={"file": ("x.mp4", b"data")},
        headers={"Origin": "https://evil.example", "X-Minutes": ""},
    )
    assert r.status_code == 403


def test_no_cors_grant(client):
    r = client.get("/api/meetings", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in {k.lower() for k in r.headers}


def test_secrets_are_masked(client):
    client.post("/api/settings", json={"anthropic_api_key": "test-not-a-real-key-1234"})
    body = client.get("/api/settings").json()
    assert body["anthropic_api_key"] == "••••1234"
    # Sending the mask back must not overwrite the real key.
    client.post("/api/settings", json={"anthropic_api_key": "••••1234"})
    from minutes import config
    assert config.load()["anthropic_api_key"] == "test-not-a-real-key-1234"
