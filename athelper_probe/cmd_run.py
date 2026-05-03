"""athelper-probe run — POST a redteam run + poll + write report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
import yaml

from athelper_probe import api_client


@click.command()
@click.option("--target", "target_file", type=click.Path(exists=True), required=True, help="Path to target YAML/JSON spec.")
@click.option("--probes", "probe_ids", required=True, help="Comma-separated probe ids OR 'all'.")
@click.option("--format", "report_format", type=click.Choice(["html", "sarif", "junit"]), default="html")
@click.option("--out", "out_file", type=click.Path(), required=True, help="Output report file path.")
@click.option("--token", envvar="ATHELPER_API_TOKEN", required=True, help="Your ATHelper API token (or env ATHELPER_API_TOKEN).")
@click.option("--api-url", default="https://www.at-helper.com", help="ATHelper API base URL.")
@click.option("--max-wait", type=float, default=1800.0, help="Max seconds to wait for run completion.")
def cmd_run(target_file: str, probe_ids: str, report_format: str, out_file: str, token: str, api_url: str, max_wait: float):
    """Submit a red-team run and write the report to disk."""
    spec = yaml.safe_load(Path(target_file).read_text())
    body = {
        "target": spec,
        "probe_ids": [s.strip() for s in probe_ids.split(",") if s.strip() != "all"] or [],
    }
    if probe_ids.strip() == "all":
        # Empty probe_ids means "all" per orchestrator convention.
        body["probe_ids"] = []

    click.echo(f"Submitting run to {api_url}/api/v1/redteam/runs ...")
    resp = api_client.post_run(api_url, token, body=body)
    run_id = resp["run_id"]
    click.echo(f"  run_id: {run_id}")

    click.echo("Polling until completion...")
    run = api_client.poll_until_complete(api_url, token, run_id, max_wait=max_wait)
    click.echo(f"  status: {run['status']}, findings: {len(run.get('findings', []))}")

    click.echo(f"Fetching {report_format} report...")
    report = api_client.get_report(api_url, token, run_id, report_format)
    Path(out_file).write_text(report)
    click.echo(f"Wrote report to {out_file}")
