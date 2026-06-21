# Data Model

The local SQLite database is stored at:

```text
data/aiwra.db
```

The directory is kept with `data/.gitkeep`; runtime database files are ignored by `.gitignore`.

## Schema

```text
schema_version
projects
workflows
workflow_steps
assessments
detected_findings
risk_factors
control_library
recommended_controls
simulation_runs
reports
audit_events
knowledge_articles
demo_scenarios
```

## Table Descriptions

- `schema_version`: current local schema version.
- `projects`: local projects, including the seeded synthetic demo project.
- `workflows`: workflow text saved only after explicit user action.
- `workflow_steps`: extracted steps for a saved workflow.
- `assessments`: deterministic assessment summary and risk JSON.
- `detected_findings`: evidence-based findings for a saved assessment.
- `risk_factors`: risk matrix entries and score impact.
- `control_library`: seeded defensive controls from JSON.
- `recommended_controls`: controls mapped to a saved assessment.
- `simulation_runs`: residual-risk simulations saved explicitly.
- `reports`: Markdown reports and JSON summaries.
- `audit_events`: local audit trail of save and reset actions.
- `knowledge_articles`: explanation cards loaded from the local knowledge base.
- `demo_scenarios`: synthetic demo scenarios loaded from JSON.

## Relationships

- A project can have many workflows.
- A workflow can have many workflow steps.
- A project and workflow can have many assessments.
- An assessment can have findings, risk factors, recommended controls, and simulation runs.
- A report belongs to an assessment and a project.
- Audit events reference local entity IDs when relevant.

## Persistence Rules

- User workflow text is not stored automatically by analysis.
- Saving a workflow requires the user to click the save/report action.
- Saving assessments, findings, reports, and simulations is explicit.
- Synthetic seeded scenarios may be persisted by default.
- No telemetry is written.
- No external database is used.

## Seed Strategy

`database.seed_database()` loads:

- control definitions into `control_library`;
- explanation cards into `knowledge_articles`;
- synthetic demo scenarios into `demo_scenarios`;
- a synthetic local demo project into `projects`.

Seed data is idempotent and can be loaded repeatedly.

## Demo Reset Behavior

`database.reset_demo_db()` removes the local SQLite file and recreates the schema with synthetic seed data. It is useful for a clean portfolio demo, but it also deletes saved local workflows, reports, simulations, and audit events. The UI requires explicit confirmation before running it. It does not contact any external service.
