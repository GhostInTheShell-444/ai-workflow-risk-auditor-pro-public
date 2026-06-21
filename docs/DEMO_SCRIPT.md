# Demo Script

## 90-Second Demo

1. Open with: "This is AI Workflow Risk Auditor Pro, a local-first tool for reviewing AI-assisted workflow risk before production integration."
2. Show the Audit tab and select the customer support demo.
3. Run the audit.
4. Point to the score, top evidence, and recommended next action.
5. Open the risk matrix expander and explain that scoring is deterministic.
6. Open Simulation, select the default controls, and simulate residual risk.
7. Save the report explicitly.
8. Open Reports and download Markdown or JSON.
9. Open Dashboard to show local SQLite metrics.
10. Open Knowledge Base to show the rules and controls are local JSON.

## 5-Minute Demo

1. Start the app with `streamlit run app.py --server.address 127.0.0.1`.
2. Explain the privacy warning: use anonymized text only.
3. Select or create a local project.
4. Select the Customer Support Email Workflow.
5. Click Analyze Workflow.
6. Show Detected Evidence and explain the evidence chain.
7. Show the Risk Matrix and explain raw score, likelihood, impact, and confidence.
8. Show recommended controls and the human validation plan.
9. Open Simulation, select controls, and run residual-risk simulation.
10. Save the analysis/report intentionally.
11. Open Reports and show history, Markdown, JSON, and audit trail.
12. Open Dashboard and show saved metrics.
13. Open Knowledge Base and search for `human approval` or `données clients`.

## Interview Talking Points

- Local-first privacy: no cloud API, no telemetry, no external database.
- Explicit persistence: user workflow text is not saved automatically.
- Evidence-based detection: every finding has a matched rule and evidence string.
- Deterministic scoring: Ollama cannot change findings or risk.
- SQLite architecture: simple local persistence with schema versioning.
- Residual risk: simulated planning output, not production assurance.
- Defensive scope: no integrations, no actions, no scanning, no incident response execution.
- Test coverage: automated pytest coverage for deterministic analysis, persistence, exports, localization, UI helpers, and local-model guardrails.

## Probable Questions

### Why not use an LLM for detection?

The product needs repeatable and testable audit behavior. A local model may improve wording, but risk decisions come from deterministic evidence and rule mappings.

### Why SQLite?

It fits the local-first requirement, avoids external services, supports report history and dashboarding, and keeps the architecture simple.

### How is privacy handled?

The app warns users not to paste real sensitive data, does not autosave workflow text, and only persists user text after explicit save actions.

### What does residual risk mean?

It is a local simulation of selected control effects against mapped risk factors. It helps planning but does not guarantee production risk reduction.

### What would you add next?

PDF export, richer Hebrew detection, control profiles, compliance mapping, and more dashboard filters.

### Reset warning

The reset control recreates the local SQLite demo database and deletes saved local reports. Use it only at the start or end of a demo after confirming that no saved report needs to be kept.
