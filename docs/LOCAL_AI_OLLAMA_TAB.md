# Local AI / Ollama Tab

## Purpose

AIWRA uses a local-first AI Provider Gateway boundary. The current implemented provider is Ollama, exposed as a bounded local reviewer assistant without changing deterministic scoring.

The gateway is logically disabled by default: no model request occurs until the user explicitly invokes a local AI action. The deterministic application remains complete without a provider.

## Provider architecture

- Default: disabled; no automatic model call.
- Implemented runtime: Ollama over an explicit loopback endpoint.
- Future compatible design: a generic OpenAI-compatible provider may target an explicitly configured local endpoint.
- Possible compatible local servers include LM Studio, LocalAI, and vLLM; none is a dependency.
- LiteLLM may be evaluated later as an optional gateway; it is not required or active.
- Cloud providers remain future roadmap items requiring explicit opt-in and separate security review.
- There is no implicit cloud fallback and no API key storage.

An OpenAI-compatible provider is not implemented in the current module. Adding a clean provider abstraction would require a separately approved module boundary rather than coupling the Ollama protocol and OpenAI-compatible protocol in `ollama_client.py`.

## What It Shows

- Ollama availability.
- Local endpoint: `http://localhost:11434`.
- Local models listed by Ollama.
- Cloud/proxy-like models blocked.
- Synthetic prompt test.
- Exact prompt sent.
- Exact response received.
- Optional local narrative for the current report.
- Reviewer questions, missing-context prompts, evidence summaries, and challenge questions.
- Deterministic report vs local AI narrative comparison.

## Guardrails

- Ollama is optional.
- Only explicit loopback endpoints (`localhost`, `127.0.0.1`, `::1`) are allowed.
- HTTP redirects are rejected.
- Environment proxy routing is disabled.
- Cloud/proxy-like model names are blocked.
- Local AI never changes deterministic findings, scores, controls, or residual-risk simulation.
- The deterministic engine is the source of truth.
- Workflow text is treated as untrusted context in the prompt.
- Prompt and response are visible to the user.
- If Ollama is unavailable, the app remains fully deterministic.

## What Local AI Adds

- Local narrative drafting.
- Optional explanation wording.
- Reviewer and challenge questions.
- Missing-context questions.
- Evidence summary based on deterministic findings.
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

Local AI output is displayed and stored separately from the deterministic analysis object. It may be included as clearly labeled wording assistance in a report, but it cannot become score authority.
