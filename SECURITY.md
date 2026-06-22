# Security Policy

## Reporting a vulnerability

Use GitHub's private security advisory feature for this repository when available. Include the affected version or commit, impact, reproduction steps using synthetic data, and any suggested mitigation. If private reporting is unavailable, contact the maintainers through a private repository-owner channel before opening a public issue.

Do not post secrets, personal data, real workflow content, exploit details, or sensitive screenshots in a public issue. Use synthetic reproduction data. Security testing is authorized only for systems you own or have explicit written permission to assess; do not target third-party or production systems through this project.

## Supported versions

Before the first published release, the default branch is the only supported line. After releases begin, security fixes are targeted to the latest published version. Older snapshots may not receive backports.

## Security boundaries

AI Workflow Risk Auditor Pro is a local defensive review aid, not a hardened multi-user service. It provides no authentication, authorization, encrypted database, tenant isolation, secure deletion guarantee, production integration, vulnerability scanner, or automated remediation. Run it on a trusted machine, bind Streamlit to `127.0.0.1`, and do not expose it to untrusted networks.

The application is local-first:

- Deterministic analysis and report generation require no cloud API.
- No vendor API key or cloud account is required.
- User workflow text is persisted only after an explicit local save action.
- Saved data is stored in project-local SQLite and is not encrypted by the app.
- No telemetry is implemented.

## Ollama policy

Ollama support is optional. The client accepts only loopback endpoints and blocks models identified as cloud/proxy models. There is no cloud fallback. Optional narrative output cannot change deterministic findings, scores, controls, or residual-risk simulation.

Users remain responsible for the security and behavior of their local Ollama installation and model files. Use only synthetic or anonymized workflow content even when a model is local.

## Responsible disclosure expectations

Allow maintainers reasonable time to reproduce and address a report before public disclosure. Keep demonstrations minimal, local, non-destructive, and free of real sensitive data.
