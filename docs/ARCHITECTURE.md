# Architecture

AI Workflow Risk Auditor Pro is a local-first Streamlit application. It is intentionally simple: no microservices, no external database, no cloud API, and no production integrations.

## Logical Architecture

```text
UI layer
  app.py
  Audit, Simulation, Dashboard, Reports, Knowledge Base tabs

Application/domain layer
  analyzer.py
  workflow_parser.py
  evidence_engine.py
  risk_matrix.py
  controls_engine.py
  residual_risk.py
  human_validation.py

Data layer
  database.py
  repositories.py
  knowledge_base/*.json
  data/aiwra.db

Output layer
  report_renderer.py
  export_json.py
```

## Data Flow

1. User selects a synthetic scenario or enters anonymized workflow text.
2. `analyzer.py` preserves the V1 deterministic analyzer behavior.
3. `workflow_parser.py` extracts workflow steps and detects a simple language hint.
4. `evidence_engine.py` matches local JSON risk patterns against each step.
5. `risk_matrix.py` maps findings to deterministic factor scores.
6. `controls_engine.py` maps findings to defensive controls.
7. `human_validation.py` generates checkpoints with responsible roles.
8. `residual_risk.py` simulates selected control effects.
9. `report_renderer.py` renders Markdown.
10. `export_json.py` renders a JSON summary.
11. `repositories.py` writes to SQLite only after explicit save actions.

## Module Responsibilities

- `app.py`: Streamlit presentation, tab layout, local user actions.
- `analyzer.py`: Compatibility facade and V1 fields.
- `risk_rules.py`: Deterministic additive scoring weights.
- `workflow_parser.py`: Text cleaning, step extraction, simple language detection.
- `evidence_engine.py`: Evidence extraction from structured local rules.
- `risk_matrix.py`: Likelihood, impact, confidence, raw score, severity.
- `controls_engine.py`: Recommended control mapping.
- `residual_risk.py`: Before/after local simulation.
- `human_validation.py`: Checkpoint plan generation.
- `database.py`: SQLite schema, versioning, seed, reset.
- `repositories.py`: Persistence operations and dashboard queries.
- `knowledge_loader.py`: JSON knowledge-base loading and validation.
- `report_renderer.py`: Markdown and RTL-aware HTML rendering.
- `export_json.py`: JSON summary export.
- `ollama_client.py`: Optional localhost-only narrative enrichment.

## Technical Decisions

- SQLite is used because the product is local-first and portfolio-safe.
- JSON knowledge files make rules and controls inspectable.
- Deterministic scoring is independent from Ollama.
- Ollama is optional and restricted to localhost.
- Persistence is explicit to protect user workflow text.
- Tests use temporary SQLite files.

## Boundaries

The app does not connect to real systems, execute actions, send messages, block users, delete records, perform vulnerability scanning, or modify production data. Any future production integration would require a separate security review and change-management process.
