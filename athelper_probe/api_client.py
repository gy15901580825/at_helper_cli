"""Minimal httpx wrapper around the ATHelper REST API."""

from __future__ import annotations

import time

import httpx

_org_id: str | None = None


def set_org_id(org_id: str | None) -> None:
    """Organization the CLI acts in; sent as x-org-id on every ATHelper API request."""
    global _org_id
    _org_id = org_id


def _headers(token: str) -> dict[str, str]:
    headers = {"x-api-token": token}
    if _org_id:
        headers["x-org-id"] = _org_id
    return headers


def post_run(api_url: str, token: str, body: dict, timeout: float = 30.0) -> dict:
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(f"{api_url}/api/v1/redteam/runs", json=body, headers=_headers(token))
        resp.raise_for_status()
        return resp.json()


def get_run(api_url: str, token: str, run_id: str, timeout: float = 30.0) -> dict:
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(f"{api_url}/api/v1/redteam/runs/{run_id}", headers=_headers(token))
        resp.raise_for_status()
        return resp.json()


def get_report(api_url: str, token: str, run_id: str, format: str, timeout: float = 30.0) -> str:
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(
            f"{api_url}/api/v1/redteam/runs/{run_id}/report",
            params={"format": format},
            headers=_headers(token),
        )
        resp.raise_for_status()
        return resp.text


def poll_until_complete(api_url: str, token: str, run_id: str, interval: float = 2.0, max_wait: float = 1800.0) -> dict:
    deadline = time.monotonic() + max_wait
    while time.monotonic() < deadline:
        run = get_run(api_url, token, run_id)
        if run["status"] in ("completed", "failed", "cancelled"):
            return run
        time.sleep(interval)
    raise TimeoutError(f"run {run_id} did not complete within {max_wait}s")


def list_probes(api_url: str, token: str, timeout: float = 30.0) -> list[str]:
    """GET /api/v1/redteam/probes (TBD endpoint — Plan 3 Task 14 adds it)."""
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(f"{api_url}/api/v1/redteam/probes", headers=_headers(token))
        resp.raise_for_status()
        return resp.json()["probe_ids"]
