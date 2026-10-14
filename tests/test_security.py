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


WRITES = [
    ("POST", "/api/settings"),
    ("POST", "/api/upload"),
    ("POST", "/api/open-output"),
    ("POST", "/api/meetings/abc/open"),
    ("DELETE", "/api/meetings/abc"),
    ("DELETE", "/api/jobs/abc"),
]

# Headers a real browser attaches (pages can't remove or forge them).
SAME_ORIGIN = {"Origin": "http://127.0.0.1:7860", "Sec-Fetch-Site": "same-origin"}
CROSS_SITE = {"Origin": "https://evil.example", "Sec-Fetch-Site": "cross-site"}
OTHER_LOCAL_APP = {"Origin": "http://localhost:3000", "Sec-Fetch-Site": "same-site"}


@pytest.mark.parametrize("method,path", WRITES)
def test_browser_writes_without_header_are_blocked(client, method, path):
    r = client.request(method, path, headers={**SAME_ORIGIN, "X-Minutes": ""})
    assert r.status_code == 403


@pytest.mark.parametrize("method,path", WRITES)
@pytest.mark.parametrize("browser", [CROSS_SITE, OTHER_LOCAL_APP], ids=["cross-site", "other-local-port"])
def test_cross_site_writes_are_blocked_even_with_header(client, method, path, browser):
    assert client.request(method, path, headers=browser).status_code == 403


@pytest.mark.parametrize("headers", [
    {"Sec-Fetch-Site": "cross-site"},          # browser that omitted Origin
    {"Origin": "https://evil.example"},        # older browser without Sec-Fetch-*
    {"Origin": "null"},                        # sandboxed iframe / file:// page
])
def test_partial_browser_signals_are_still_checked(client, headers):
    assert client.post("/api/settings", json={"keep_wav": True}, headers=headers).status_code == 403


def test_cross_site_form_upload_is_blocked(client):
    # What a <form enctype="multipart/form-data"> on another site would send.
    r = client.post("/api/upload", files={"file": ("x.mp4", b"data")}, headers={**CROSS_SITE, "X-Minutes": ""})
    assert r.status_code == 403


def test_same_origin_browser_write_with_header_works(client):
    r = client.post("/api/settings", json={"keep_wav": True}, headers=SAME_ORIGIN)
    assert r.status_code == 200


def test_scripts_do_not_need_the_header(client):
    # curl / Python send neither Origin nor Sec-Fetch-Site.
    r = client.post("/api/settings", json={"keep_wav": True}, headers={"X-Minutes": ""})
    assert r.status_code == 200


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
