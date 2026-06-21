# Ollama Local Diagnostics

Test date: 2026-06-14

## Local-Only Policy

Ollama is optional. The deterministic analyzer, findings, scoring, controls, residual risk, Markdown export, JSON export, reports, dashboard, and tests must work without Ollama.

The app must never send user workflow text to a cloud API. Local narrative enrichment is allowed only through a localhost Ollama endpoint and only with models that appear local-only.

## Endpoint Tested

```text
http://127.0.0.1:11434
```

The app code also accepts `http://localhost:11434`. Non-local endpoints are rejected by `ollama_client._is_localhost()`.

## `/api/tags` Result

Status: PASS/PARTIAL

Ollama responded on localhost. The response contained both local models and cloud/proxy-like models.

Local-only models detected by the app:

```text
qwen25-coder-7b-64k:latest
qwen3-8b-8k:latest
qwen2.5-coder:7b
qwen25-coder-7b-8k:latest
qwen3:8b
```

Cloud/proxy-like models detected:

```text
40 models
sample:
minimax-m2.5:cloud
gemma3:27b-cloud
gemma3:12b-cloud
kimi-k2:1t-cloud
gemma3:4b-cloud
kimi-k2-thinking:cloud
glm-4.6:cloud
minimax-m2:cloud
deepseek-v3.1:671b-cloud
qwen3-coder:480b-cloud
```

The raw `/api/tags` payload showed `remote_host=https://ollama.com:443` for cloud/proxy models. These are blocked for local-only enrichment.

## `/api/generate` Tests

| Model | Status | Result |
| --- | --- | --- |
| `llama3` | FAIL/PARTIAL | HTTP 404 in direct diagnostic; app now rejects it because it is not listed locally. |
| `gemma3:cloud` | PASS fallback | Rejected before generation because it is cloud/proxy-like. |
| `qwen25-coder-7b-8k:latest` | PASS | Local model responded to a synthetic diagnostic prompt. |

## UX Improvement Applied

- Sidebar now lists only local-only models when Ollama is enabled.
- Sidebar warns when cloud/proxy-like models are detected.
- Missing selected model message: "Ollama is reachable, but the selected model is not installed. Deterministic report was used."
- No local model message: "Ollama is reachable, but no local-only models were listed. Deterministic report was used."
- Cloud/proxy message: "Cloud/proxy-like model names were detected. Local-only deterministic fallback was used."
- Ollama remains disabled by default.

## Code-Level Controls

- `check_ollama_status()` separates `models`, `cloud_models`, and `all_models`.
- `is_cloud_or_proxy_model()` rejects names containing `:cloud` or `-cloud`, and model payloads with `remote_host` or `remote_model`.
- `generate_enrichment()` rejects non-local endpoints, cloud/proxy model names, unavailable Ollama status, and models not listed as local.
- Tests verify local/cloud separation, cloud rejection, missing model rejection, and non-local endpoint rejection.

## Important Finding

A valid local model can still produce imperfect wording. The report renderer was changed so Ollama enrichment no longer replaces the deterministic executive summary. The deterministic score and raw matrix remain the source of truth.

## Limitations

- The app trusts Ollama `/api/tags` metadata to distinguish local from cloud/proxy models.
- The app does not inspect Ollama server configuration beyond `/api/tags`.
- Local generation was tested only with synthetic prompt content.
- No user-provided sensitive content was sent to Ollama during diagnostics.
