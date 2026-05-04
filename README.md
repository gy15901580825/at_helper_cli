# athelper-probe

Open-source CLI for [ATHelper](https://www.at-helper.com), the red-team testing service for AI agents.

Point `athelper-probe` at any AI agent endpoint — chat APIs, custom HTTP services, gRPC, or browser-using agents — and get a report mapped to MITRE ATLAS, OWASP LLM Top 10, NIST AI RMF, and the EU AI Act.

```
$ athelper-probe run --target athelper-target.json --probes owasp_07_system_prompt_leakage --format html --out report.html
[..] submitted run abc123
[..] polling for completion (typically 10–30s)
[..] report written to report.html
```

## Install

**Linux x86_64**

```bash
curl -sSL https://github.com/gy15901580825/at_helper_cli/releases/download/v0.1.1/athelper-probe-linux-x86_64 \
  -o /usr/local/bin/athelper-probe
chmod +x /usr/local/bin/athelper-probe
```

**macOS arm64**

```bash
curl -sSL https://github.com/gy15901580825/at_helper_cli/releases/download/v0.1.1/athelper-probe-darwin-arm64 \
  -o /usr/local/bin/athelper-probe
chmod +x /usr/local/bin/athelper-probe
```

**From source (Python 3.11+)**

```bash
pip install git+https://github.com/gy15901580825/at_helper_cli.git@v0.1.1
```

## Quickstart

```bash
# 1. Generate a target spec interactively
athelper-probe init --kind openai_compat

# 2. Set your ATHelper API token
export ATHELPER_API_TOKEN="<your token>"

# 3. Sanity-check the target is reachable
athelper-probe validate-target --target athelper-target.json

# 4. Run a probe
athelper-probe run \
  --target athelper-target.json \
  --probes owasp_07_system_prompt_leakage \
  --format html --out report.html
```

Get an API token by emailing `ops@at-helper.com`.

## Supported agent shapes

`athelper-probe init --kind <X>` generates a target spec for one of:

| `--kind` | For |
|---|---|
| `openai_compat` | OpenAI Chat Completions protocol — OpenAI, Azure OpenAI, Foundry, Mistral, vLLM/llama.cpp with the OpenAI shim |
| `anthropic_native` | Anthropic Messages API |
| `custom_http` | Production agents wrapping an LLM behind their own HTTP shape (Jinja2 request templates + JSONPath response selectors) |
| `grpc` | gRPC services with server reflection enabled |
| `browser_use` | Browser-using agents driving Playwright / computer-use / browser-use |

Full configuration reference: [target spec cookbook](https://www.at-helper.com/docs).

## What it does

`athelper-probe` is a thin client. It submits the target spec and probe selection to the ATHelper service over HTTPS; the service runs the probes against your agent and returns the report. The CLI itself does not call LLMs or store secrets.

Secret references in your target spec (`${OPENAI_API_KEY}`, etc.) are resolved from the local shell environment at run time and sent only as outbound headers to your agent — they never enter the target.json file or the ATHelper service.

## Output formats

- `html` — human-readable report
- `sarif` — SARIF 2.1.0, uploads cleanly to GitHub code-scanning (Security tab)
- `junit` — JUnit XML for any CI tool that parses test results

## CI integration

Wire into GitHub Actions with the official action:

```yaml
- uses: gy15901580825/athelper-probe-action@v1
  with:
    api-token: ${{ secrets.ATHELPER_API_TOKEN }}
    target-config: athelper-target.json
    threshold: block-on-critical
```

## Cost controls

```bash
athelper-probe run --target ... --per-run-cap 0.50
```

Runs that would exceed the cap are rejected by the service before any LLM cost is incurred (HTTP 402).

## Subcommands

```
athelper-probe init                Interactive target.json generator
athelper-probe validate-target     Sanity-check target reachability
athelper-probe list-probes         List probe ids available to your account
athelper-probe run                 Submit a run + write the report
athelper-probe report              Re-render an existing run's report
```

Each command's `--help` lists its flags.

## License

MIT — see [LICENSE](./LICENSE).

## Security

To report a vulnerability: see [SECURITY.md](./SECURITY.md).

## Links

- Documentation: https://www.at-helper.com/docs
- Become a design partner: https://www.at-helper.com/design-partners
- Pricing: https://www.at-helper.com/pricing
