# Security policy

## Reporting a vulnerability

If you believe you've found a security issue in `athelper-probe`, please report it privately to **contact@veyon.solutions**.

Please include:

- A description of the issue
- Steps to reproduce
- Affected versions (e.g. `athelper-probe --version`)
- Your assessment of impact

We aim to acknowledge reports within 2 business days and ship a fix or mitigation within 30 days, depending on severity.

**Please do not** open a public GitHub issue for security-sensitive reports.

## Scope

In scope:

- The `athelper-probe` CLI itself (this repository)
- The PyInstaller-built binaries published under [Releases](https://github.com/gy15901580825/at_helper_cli/releases)

Out of scope (report to `contact@veyon.solutions` separately if relevant):

- The ATHelper service / API
- Probe content or judge behavior
- Findings reported by the tool against your own agent (those are the tool's intended output, not vulnerabilities in this CLI)

## Supported versions

Only the latest released version receives security patches. Pin to `@vX.Y.Z` in CI; upgrade promptly when an advisory lands.

## Handling secrets

`athelper-probe` is designed so that API keys and other credentials referenced in `athelper-target.json` (e.g. `${OPENAI_API_KEY}`) are read from the local environment at run time and used only as outbound headers to your own agent endpoint. They are not written to the target file, transmitted to the ATHelper service, or logged.

If you observe behavior that contradicts this — for example, secrets appearing in logs, transcripts, or transmitted payloads — that is a security issue and should be reported via the address above.
