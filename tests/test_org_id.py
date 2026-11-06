"""--org-id / ATHELPER_ORG_ID makes every API request carry x-org-id."""
from __future__ import annotations

import httpx
import pytest
from click.testing import CliRunner

from athelper_probe import api_client
from athelper_probe.__main__ import main

ORG_A = "11111111-1111-4111-8111-111111111111"
ORG_B = "22222222-2222-4222-8222-222222222222"


@pytest.fixture
def seen(monkeypatch):
    """Capture the headers of every request made through api_client."""
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(200, json={"run_id": "r1"})
        if request.url.path.endswith("/report"):
            return httpx.Response(200, text="<html></html>")
        if request.url.path.endswith("/probes"):
            return httpx.Response(200, json={"probe_ids": ["p1"]})
        return httpx.Response(200, json={"status": "completed", "findings": []})

    real_client = httpx.Client
    monkeypatch.setattr(
        api_client.httpx, "Client",
        lambda **kw: real_client(transport=httpx.MockTransport(handler), **kw),
    )
    monkeypatch.delenv("ATHELPER_ORG_ID", raising=False)
    return requests


def _list_probes(args=(), env=None):
    return CliRunner().invoke(
        main, [*args, "list-probes", "--token", "t", "--api-url", "https://x.test"], env=env
    )


def test_flag_sends_header(seen):
    result = _list_probes(["--org-id", ORG_A])
    assert result.exit_code == 0, result.output
    assert seen[0].headers["x-org-id"] == ORG_A
    assert seen[0].headers["x-api-token"] == "t"


def test_env_sends_header(seen):
    result = _list_probes(env={"ATHELPER_ORG_ID": ORG_B})
    assert result.exit_code == 0, result.output
    assert seen[0].headers["x-org-id"] == ORG_B


def test_flag_beats_env(seen):
    result = _list_probes(["--org-id", ORG_A], env={"ATHELPER_ORG_ID": ORG_B})
    assert result.exit_code == 0, result.output
    assert seen[0].headers["x-org-id"] == ORG_A


def test_header_absent_when_unset(seen):
    _list_probes(["--org-id", ORG_A])
    seen.clear()
    result = _list_probes()
    assert result.exit_code == 0, result.output
    assert "x-org-id" not in seen[0].headers


def test_run_sends_header_on_every_request(seen, tmp_path):
    target = tmp_path / "t.json"
    target.write_text('{"kind":"openai_compat","endpoint_url":"https://a.test/v1/chat/completions","model":"m","api_key":"k"}')
    result = CliRunner().invoke(main, [
        "--org-id", ORG_A, "run", "--target", str(target), "--probes", "p1",
        "--out", str(tmp_path / "r.html"), "--token", "t", "--api-url", "https://x.test",
    ])
    assert result.exit_code == 0, result.output
    assert len(seen) == 3
    assert all(r.headers["x-org-id"] == ORG_A for r in seen)


@pytest.mark.parametrize("bad", ["not-a-uuid", "123"])
def test_invalid_org_id_exits_with_usage_error(seen, bad):
    result = _list_probes(["--org-id", bad])
    assert result.exit_code == 2
    assert "not a valid organization UUID" in result.output
    assert seen == []


def test_invalid_env_exits_with_usage_error(seen):
    result = _list_probes(env={"ATHELPER_ORG_ID": "nope"})
    assert result.exit_code == 2
    assert "not a valid organization UUID" in result.output
