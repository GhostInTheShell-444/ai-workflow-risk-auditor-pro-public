# Local AI / Ollama Tab

## Purpose

The Local AI / Ollama tab makes optional localhost-only AI value visible without changing deterministic scoring.

## What It Shows

- Ollama availability.
- Local endpoint: `http://localhost:11434`.
- Local models listed by Ollama.
- Cloud/proxy-like models blocked.
- Synthetic prompt test.
- Exact prompt sent.
- Exact response received.
- Optional local narrative for the current report.
- Deterministic report vs local AI narrative comparison.

## Guardrails

- Ollama is optional.
- Only localhost endpoints are allowed.
- Cloud/proxy-like model names are blocked.
- Local AI never changes deterministic findings, scores, controls, or residual-risk simulation.
- Prompt and response are visible to the user.
- If Ollama is unavailable, the app remains fully deterministic.

## What Local AI Adds

- Local narrative drafting.
- Optional explanation wording.
- Synthetic local-only test.
- Report wording assistance.

## What Local AI Does Not Add

- Scientific validation.
- Compliance certification.
- Score authority.
- Cloud analysis.
- Automatic remediation.

## Remaining Manual Checks

Test with a real local model only if Ollama is installed. Without Ollama, verify that the tab shows a clean unavailable state and does not block the app.
