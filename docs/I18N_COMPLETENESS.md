# I18N Completeness

## Current Scope

The app supports:

- English (`en`)
- French (`fr`)
- Hebrew (`he`, RTL)

The locale files have strict key parity enforced by tests.

## Localized Interface Coverage

Localized labels cover:

- dashboard subviews;
- heatmap and matrix;
- workflow graph;
- evidence drill-down;
- local follow-up items;
- control checklist;
- Knowledge Base cleaned columns;
- demo scenario badges;
- Local AI / Ollama tab;
- severity descriptions;
- status descriptions;
- accessibility notes.

## Technical Key Policy

JSON export keeps stable technical keys in English. Explanatory values may be localized. This preserves automation compatibility while improving human-facing text.

## RTL Policy

Hebrew uses RTL layout for human-facing UI. Prompt blocks, JSON, code, paths, endpoints, and model names remain LTR for readability.

## Known Limits

- Rule-library source text remains mostly English because it is the local deterministic knowledge source.
- A native Hebrew review remains a recommended, non-blocking language-quality improvement.
- Some existing report helper sentences remain English to avoid broad report regression.
