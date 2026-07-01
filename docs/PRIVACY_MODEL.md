# Privacy Model

## Scope

AI Workflow Risk Auditor Pro is designed for local review of synthetic or anonymized workflow descriptions. It is not a data-loss-prevention product and cannot guarantee that users will avoid entering sensitive information.

## Data flow and storage

- Analysis runs in the local Streamlit process using Python modules and JSON knowledge files.
- Workflow text is held in the active Streamlit session and is not automatically written to SQLite.
- Downloads are generated in memory and do not create database history.
- The explicit **Save analysis and report locally** action writes the workflow, assessment, findings, controls, report, and related audit events to `data/aiwra.db`.
- A simulation is saved only through an explicit save action and only after the associated assessment exists.
- The SQLite path is project-local and contains no user-specific absolute path.
- Clearing only the input does not delete the current analysis or saved SQLite history.
- Clearing the current session requires confirmation and removes current input, analysis, simulation, report state, and Local AI response without deleting saved SQLite history.
- Deleting the active project is targeted to one selected non-demo project and its related saved records; the bundled synthetic demo project is protected.
- Resetting the demo database requires confirmation and deletes saved projects, workflows, assessments, findings, simulations, reports, and audit events before recreating synthetic seed content.

## Network boundary

The deterministic application requires no cloud API, cloud SDK, vendor key, telemetry service, or external database. No hidden analytics or telemetry code is implemented. The application has no production-system integration and does not automatically transmit workflow text.

The AI Provider Gateway is disabled by default. The only implemented provider is Ollama through an explicitly invoked loopback URL. `ollama_client.py` accepts `localhost`, `127.0.0.1`, or `::1`; non-loopback endpoints are rejected. Ollama requests reject HTTP redirects and disable environment proxy routing. Models identified by cloud-like names or remote model metadata are blocked. There is no cloud fallback, cloud provider enabled by default, or API key storage.

A generic OpenAI-compatible provider is a future opt-in design, not a current runtime capability. If implemented, its safe local mode may support explicitly configured LM Studio, LocalAI, or vLLM endpoints. LiteLLM remains a possible future gateway. Remote or cloud endpoints require separate explicit design and security approval.

Important boundary: a locally installed third-party service or model remains part of the user's environment. Users are responsible for verifying their Ollama installation and model provenance. The app's endpoint and model guards reduce accidental remote use but cannot attest to all behavior of external local software.

## Score and narrative separation

Deterministic Python rules are authoritative for findings, scores, controls, and residual-risk simulation. Optional Ollama output can add narrative wording, evidence summaries, missing-context prompts, and reviewer questions. It does not modify the deterministic analysis object or scoring model.

## Repository protections

Git ignores runtime databases, virtual environments, Python caches, test caches, environment files, Streamlit secrets, logs, notebook checkpoints, and common tool caches. `data/.gitkeep` preserves the runtime directory without publishing user data.

## User responsibilities

- Prefer bundled synthetic scenarios.
- Anonymize custom workflow text before entry.
- Never paste credentials, secrets, regulated records, or unnecessary personal data.
- Review reports and screenshots before sharing.
- Delete local `data/aiwra.db` when local history is no longer needed.
- Perform a separate security, privacy, legal, and governance review before production integration.

## Known limitations

Streamlit session state is process-local but not a hardened secrets store. Explicitly saved SQLite data is unencrypted at rest by this application. The app provides no authentication, access control, retention automation, secure deletion guarantee, or multi-user isolation. Run it only in a trusted local environment and do not expose the Streamlit server to untrusted networks.
