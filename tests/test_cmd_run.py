"""Tests for `athelper-probe run`."""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from athelper_probe.__main__ import main


def test_run_calls_api_and_writes_report(tmp_path):
    runner = CliRunner()
    target_spec = {
        "kind": "openai_compat",
        "endpoint_url": "https://api.example.com/v1/chat/completions",
        "model": "gpt-4",
        "api_key": "sk-test",
    }
    target_file = tmp_path / "target.json"
    target_file.write_text(json.dumps(target_spec))

    fake_api = {
        "post_run": {"run_id": "abc-123"},
        "poll": [{"status": "running", "findings": []},
                 {"status": "completed", "findings": [{"id":"f1","probe_id":"p1","verdict":"pass","severity":"info"}]}],
        "report": "<html><body>Test report</body></html>",
    }

    with patch("athelper_probe.api_client.post_run", return_value=fake_api["post_run"]) as mock_post, \
         patch("athelper_probe.api_client.get_run") as mock_get, \
         patch("athelper_probe.api_client.get_report", return_value=fake_api["report"]):
        mock_get.side_effect = fake_api["poll"]

        out_file = tmp_path / "report.html"
        result = runner.invoke(main, [
            "run",
            "--target", str(target_file),
            "--probes", "p1",
            "--format", "html",
            "--out", str(out_file),
            "--token", "test-token",
            "--api-url", "https://dev.at-helper.com",
        ])
        assert result.exit_code == 0, result.output
        assert "abc-123" in result.output
        assert out_file.exists()
        assert "Test report" in out_file.read_text()
        # Verify the post call shape
        body = mock_post.call_args.kwargs["body"]
        assert body["target"]["model"] == "gpt-4"
        assert body["probe_ids"] == ["p1"]
