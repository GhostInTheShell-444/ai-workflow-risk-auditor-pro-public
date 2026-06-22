# Architecture

AI Workflow Risk Auditor Pro is a single-process, local-first Streamlit application. Deterministic analysis and reporting run without microservices, a cloud API, or an external database.

## Overview

```text
Synthetic/anonymized workflow
          |
          v
  app.py (Streamlit UI and session state)
          |
          +--> workflow_parser.py --> evidence_engine.py --> local JSON knowledge
          |                                  |
          |                                  v
          +--> analyzer.py / risk_rules.py / risk_matrix.py
          |                                  |
          |                     +------------+-------------+
          |                     v                          v
          |             controls_engine.py         score_explainability.py
          |                     |                          |
          |                     v                          |
          |             residual_risk.py                  |
          |                     +------------+-------------+
          |                                  v
          +------------------------> report_renderer.py / export_json.py
                                             |
                           explicit save only v
                                repositories.py --> database.py --> data/aiwra.db

Optional boundary: ollama_client.py --> loopback Ollama --> narrative wording only
```

## Main files and responsibilities

- `app.py`: Streamlit page configuration, sidebar controls, session state, six main tabs, export actions, and explicit-save UI.
- `analyzer.py`: deterministic workflow analysis facade that assembles parsing, evidence, factors, controls, risk matrix, and human-validation outputs while preserving compatibility fields.
- `risk_rules.py`: additive factor weights, fixed score thresholds, and score explanations.
- `evidence_engine.py`: matches workflow steps against local structured risk patterns and returns traceable evidence, severity, and deterministic confidence.
- `database.py`: project-local SQLite path, schema, initialization, synthetic seed content, and confirmed reset.
- `repositories.py`: project, workflow, assessment, finding, control, simulation, report, audit-event, and dashboard persistence/query operations.
- `workflow_parser.py`: input cleanup, step extraction, match normalization, and simple language hints.
- `score_explainability.py`: source/meaning/limitation content, score summaries, factor basis, top risks, next actions, and simulation explanations.
- `report_renderer.py`: deterministic Markdown reports and RTL-aware HTML rendering for previews.
- `export_json.py`: stable JSON summary structure and serialization.
- `ui_components.py`: reusable cards, badges, heatmap/matrix builders, evidence panels, timelines, and accessibility/read-only notices.
- `design_tokens.py`: light/dark/system theme constants plus severity and status presentation tokens. System currently resolves to the light palette.
- `locales/`: matching English, French, and Hebrew JSON catalogs; Hebrew is marked RTL through `i18n.py`.
- `knowledge_base/`: local JSON risk patterns, controls, data categories, scenarios, explanations, and templates loaded by `knowledge_loader.py`.
- `tests/`: deterministic unit/integration tests, temporary SQLite tests, export/security checks, locale parity/RTL checks, and UI data-helper tests.

Supporting domain modules include:

- `risk_matrix.py`: likelihood, impact, confidence, raw score, and severity assembly.
- `controls_engine.py`: finding-to-control recommendation mapping.
- `residual_risk.py`: fixed-effect residual-risk simulation.
- `human_validation.py`: checkpoint and responsible-role planning.
- `dashboard.py`: dashboard metric access.
- `report_history.py`: saved report and audit-trail retrieval.
- `ollama_client.py`: optional local status checks, prompt construction, cloud/proxy model rejection, and narrative requests.
- `i18n.py`: locale loading, fallback, translation helpers, and RTL metadata.

## Data flow

1. The user chooses bundled synthetic data or enters an anonymized workflow in `app.py`.
2. `workflow_parser.py` cleans the text and extracts steps.
3. `evidence_engine.py` matches each step to enabled local risk patterns.
4. `analyzer.py` also applies compatibility detectors and assembles a single analysis object.
5. `risk_rules.py` and `risk_matrix.py` calculate deterministic factor and matrix outputs.
6. `controls_engine.py` maps findings to recommended controls; `human_validation.py` proposes review checkpoints.
7. `score_explainability.py` prepares human-readable score, source, meaning, limitation, risk, and action content.
8. `residual_risk.py` optionally simulates selected mapped controls without changing the original analysis.
9. `report_renderer.py` and `export_json.py` create local exports.
10. Only an explicit UI save calls `repositories.py` to write workflow and report records to SQLite.

## Local-first boundary

The authoritative analysis path reads local Python code and JSON files and writes nothing to external services. Workflow text remains in Streamlit session state during analysis. Downloads are generated without report-history persistence. Explicit save actions write to project-local `data/aiwra.db`.

The app implements no telemetry, cloud SDK, remote database, production integration, authentication, authorization, or tenant isolation. The runtime SQLite database is ignored by Git and is not encrypted by the application.

## Optional Ollama boundary

`ollama_client.py` accepts only HTTP(S) URLs whose host is `localhost`, `127.0.0.1`, or `::1`. It rejects non-loopback endpoints and cloud/proxy-like model names or metadata. There is no cloud fallback.

Ollama calls occur only after an explicit user action. Returned text can assist report wording but cannot modify deterministic evidence, scores, controls, or simulations. A local third-party model/service remains part of the user's environment and must be independently trusted.

## Persistence model

`database.py` creates the schema and bundled synthetic seed data. `repositories.py` owns persistence operations. Analysis and downloads do not automatically save a workflow. The saved data model is documented in [Data Model](DATA_MODEL.md).

Resetting the demo database deletes saved local records and recreates synthetic seed content. The UI requires a confirmation checkbox.

## Testing architecture

Tests run without Ollama, cloud credentials, an existing database, or network APIs. Database tests use temporary paths. The suite covers:

- analyzer and fixed scoring behavior;
- evidence rules and knowledge-base loading;
- controls and residual-risk mappings;
- SQLite creation, persistence, and reset;
- report/JSON export and sensitive-output protections;
- localization key parity and Hebrew RTL behavior;
- theme and reusable UI component data helpers.

GitHub Actions uses Python 3.12, runs `pytest` and `compileall`, parses locale/knowledge JSON, and rejects common tracked runtime or sensitive files.

## Architectural limitations

- Keyword and pattern matching cannot fully model business context.
- Confidence and control-effect values are deterministic heuristics.
- Streamlit session state and local SQLite are not hardened multi-user storage.
- SQLite is not encrypted by the application.
- Optional local-model provenance and runtime behavior cannot be attested by this code.
- A future production integration, remote deployment, or multi-user mode would create new trust boundaries and require a separate security/privacy architecture review.
