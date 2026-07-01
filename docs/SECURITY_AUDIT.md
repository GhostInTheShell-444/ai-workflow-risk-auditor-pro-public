# Security Audit

Review date: 2026-06-21

## Scope and outcome

The tracked repository, dependency list, local persistence path, optional model client, and automated security/privacy tests were reviewed for the initial public candidate. No real secret, private key, API credential, environment file, Streamlit secrets file, personal machine path, tracked runtime database, or cloud SDK dependency was found.

This is a repository security review, not a security certification, penetration test, or guarantee about a user's environment.

## Credential-pattern classification

Broad searches intentionally find words such as `credential`, `secret`, and `token` in defensive rules, warnings, design-token terminology, and synthetic test fixtures. Notable safe fixtures include `token=DEMOONLY12345`, `token=REDACTED123`, and `api_key=DEMO_ONLY`; they exist to verify credential-like evidence detection and are not usable credentials.

A narrower scan for vendor key assignments, bearer-like values, authorization assignments, and private-key markers found no credential value in the public candidate.

## Runtime and local data boundaries

- `.gitignore` excludes SQLite databases, virtual environments, caches, bytecode, logs, environment files, and `.streamlit/secrets.toml`.
- The runtime database is `data/aiwra.db`; it is created locally and is not tracked.
- Analysis does not write workflow text to history. Persistence occurs only after an explicit save action.
- SQLite data is not encrypted by the app and is intended for one trusted local user.
- Streamlit is documented with a loopback binding; the app is not a hardened network service.

## Network boundary

Deterministic audits, scoring, simulations, reports, and tests require no network service. Optional requests in `ollama_client.py` accept loopback endpoints only. The client rejects non-loopback URLs and cloud/proxy-like model names or metadata before generation. Ollama output cannot replace or mutate deterministic analysis, scoring, controls, or simulation.

The AI Provider Gateway is disabled by default. Its implemented Ollama client disables environment proxy routing, blocks redirect following, rejects 3xx responses, and has no cloud fallback or API key storage. OpenAI-compatible local endpoints remain a future opt-in design and are not active.

The app contains no telemetry, cloud API integration, external database, authentication, authorization, tenant isolation, vulnerability scanner, or automated remediation.

## HTML, Markdown, and export rendering

- `unsafe_allow_html=True` is limited to controlled UI component markup and the sanitized report preview wrapper.
- Dynamic values inserted into controlled component HTML are escaped with `html.escape`.
- Workflow evidence and local AI output are rendered through normal Streamlit text/code components.
- `markdown_to_html` escapes every report heading, paragraph, and list item before the preview is passed to Streamlit.
- JSON export is data-only and does not execute markup.
- Regression tests verify that workflow and local AI strings containing `<script>` or event-handler markup remain escaped.
- Runtime CSS uses no external font, CDN, script, remote image, telemetry, or analytics resource.

This review reduces known rendering risks but is not a penetration test or browser-security guarantee.

## Reproducible checks

The public test suite exercises local persistence, export safety, no-cloud dependency boundaries, and Ollama endpoint/model rejection. See [Quality and Validation](QUALITY_AND_VALIDATION.md) for commands and [SECURITY.md](../SECURITY.md) for reporting and operational boundaries.

Users must still review their environment, dependencies, inputs, exports, local model installation, and deployment choices. Use synthetic or anonymized content and do not expose the app to untrusted networks.
