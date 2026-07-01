# Dashboard Components

## Component Inventory

`ui_components.py` provides small Streamlit-compatible helpers:

- `render_metric_card`: KPI card with value, source, meaning, and limit.
- `render_bento_cards`: executive cockpit grid with value, source chip, meaning, and limit.
- `render_app_status_header`: escaped app shell header with identity, loopback/local-first badge, project, language/theme, and Local AI status.
- `render_loading_panel` plus deterministic/local-AI/simulation/export wrappers: escaped product loading states that separate deterministic authority from advisory AI wording.
- `render_local_pipeline_strip`: compact local-first progress strip for input, local rules, evidence, human review, and report readiness.
- `render_command_cockpit`: text-first command cards for deterministic authority, local boundary, session state, and human-review gate.
- `render_workbench_frame`: start/input workbench framing for the native Streamlit selector, uploader, textarea, and action row.
- `render_state_panel`: explicit empty/input/error/partial/success/export state panel with text-first status.
- `render_severity_badge`: localized severity badge with text.
- `render_status_badge`: localized status badge with text.
- `render_info_card`: compact explanatory card.
- `render_section_header`: titled section with optional status.
- `render_legend`: text legend.
- `render_empty_state`: clean empty state.
- `render_evidence_card`: finding evidence, rule, confidence, action, and limitation.
- `render_control_card`: recommended control card with status `Recommended - not verified`, technical ID isolation, reason, implementation check, mapped factors, and limitation.
- `render_issue_card`: local follow-up item, not a production ticket.
- `render_timeline`: local audit event timeline.
- `render_heatmap`: category x severity text-first heatmap.
- `render_workflow_graph`: local deterministic pipeline graph.
- `render_ai_output_panel`: prompt/response panel for local AI.
- `render_accessibility_note`: visual accessibility note.
- `render_how_to_read_panel`: page guidance panel.
- `render_source_status_chip`: source/status chip.
- `render_read_only_notice`: Knowledge Base read-only notice.

## Inputs

Components accept ordinary Python dictionaries and lists from existing analysis, SQLite metrics, and Ollama status objects. Missing data should produce empty states or fallback text rather than errors.

## Empty States

Dashboard views now distinguish:

- no workflow loaded in the current session;
- workflow input ready but not analyzed;
- analysis error without public stack trace;
- valid deterministic result with no findings;
- valid deterministic result with no mapped controls;
- no saved local reports;
- no current analysis;
- no current evidence;
- no matrix entries;
- no local AI response;
- no saved timeline.

## Accessibility

Cards, badges, heatmap cells, and matrix cells include visible text labels. Color is not the only signal. Heatmap cells include category, severity, count, and description.

## Dashboard Structure

The cockpit opens on the Start / Input workbench. A compact top settings bar contains interface language and Light/Dark appearance. That main view first shows the command cockpit, then contains the workflow source selector, local import, paste area, Analyze action, secondary clear/load actions, privacy warning, deterministic source-of-truth statement, and Local AI advisory boundary. Mission Pulse appears below the main input/support area, near the Analyze action state, followed by the compact local pipeline strip. The sidebar is a compact control rail for navigation, active project, optional Ollama, guided demo, and separated local data controls. Workflow source, language, and theme are not duplicated in the sidebar.

The main groups are:

- Start / Input.
- Risk cockpit with secondary overview, risk/evidence, controls, and history views.
- Controls / Simulation.
- Exports / Reports.
- Knowledge Base.
- Local AI / Ollama.

The overview uses bento cards for risk level, findings count, human review required, local-only analysis, report readiness, and residual-risk simulation state.

## Action Inventory

Stable command keys used by the UI:

- `analyze_workflow_primary`: primary start action.
- `load_example_secondary`: load selected synthetic example into the main input.
- `clear_input_secondary`: clear only the current text field.
- `clear_session_secondary`: clear unsaved session output after confirmation.
- `simulate_residual_risk_action`: contextual residual simulation.
- `save_simulation_secondary`: save simulation after an analysis is saved.
- `save_report_secondary`: save the current analysis/report into local SQLite.
- `download_markdown_action`: download Markdown without saving history.
- `download_json_action`: download JSON without saving history.
- `delete_project_danger`: confirmed active-project deletion.
- `reset_demo_database_danger`: confirmed database reset.
- `local_ai_generate_action`: optional Local AI narrative for the current report.

Button styling follows the key hierarchy. Cards remain informational surfaces and are not clickable substitutes for buttons.

## I18N

All new visible labels are backed by locale keys in `locales/en.json`, `locales/fr.json`, and `locales/he.json`. Hebrew uses RTL app styling and the start workbench places the primary action on the RTL side of the action row. Prompts, JSON, code, model names, endpoints, IDs, Markdown, SQLite, Ollama, and AIWRA remain readable LTR.

## Loading States

The app uses product loading panels for four explicit paths:

- Deterministic analysis: local rules review evidence, with no cloud call and no final score before completion.
- Local AI: Ollama can draft advisory wording only; scores, findings, controls, and simulation stay deterministic.
- Simulation: selected controls are hypothetical until implementation evidence proves they exist.
- Export/report: Markdown and JSON are generated from deterministic local results.

These panels use escaped HTML, text-first labels, compact motion, the local pipeline strip for deterministic analysis progress, and reduced-motion support.

## Limits

The dashboard is not a BI system. Saved-history views use local SQLite aggregates only. Current matrix details are available after running an audit in the current session.

## Command-center visual layer

The executive overview and audit cockpit are presentation helpers over existing engine and persistence outputs. The risk cockpit exposes current-session score, severity, finding count, human-review requirement, localhost status, save state, and hypothetical simulation state. The live scanline, controlled score glow, and local-only status dot are visual state cues only; they do not recompute, certify, approve, or reinterpret risk. Sidebar navigation changes visibility only; it must not change deterministic output.

Evidence cards, heatmap cells, and matrix cards use severity tokens while preserving explicit labels, source, meaning, and limitations. Saved history remains visually distinct from the current unsaved session.
