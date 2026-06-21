# Dashboard Components

## Component Inventory

`ui_components.py` provides small Streamlit-compatible helpers:

- `render_metric_card`: KPI card with value, source, meaning, and limit.
- `render_bento_cards`: executive cockpit grid with value, source chip, meaning, and limit.
- `render_severity_badge`: localized severity badge with text.
- `render_status_badge`: localized status badge with text.
- `render_info_card`: compact explanatory card.
- `render_section_header`: titled section with optional status.
- `render_legend`: text legend.
- `render_empty_state`: clean empty state.
- `render_evidence_card`: finding evidence, rule, confidence, action, and limitation.
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

- no saved local reports;
- no current analysis;
- no current evidence;
- no matrix entries;
- no local AI response;
- no saved timeline.

## Accessibility

Cards, badges, heatmap cells, and matrix cells include visible text labels. Color is not the only signal. Heatmap cells include category, severity, count, and description.

## Dashboard Structure

The dashboard is organized around:

- Executive overview.
- Risk posture.
- Findings and evidence.
- Controls and follow-up.
- Local history.

The overview uses bento cards for risk level, findings count, human review required, local-only analysis, report readiness, and residual-risk simulation state.

## I18N

All new visible labels are backed by locale keys in `locales/en.json`, `locales/fr.json`, and `locales/he.json`. Hebrew uses RTL app styling while prompts, JSON, code, model names, and endpoints remain readable LTR.

## Limits

The dashboard is not a BI system. Saved-history views use local SQLite aggregates only. Current matrix details are available after running an audit in the current session.
