# Screenshot Guidelines

Screenshots are release artifacts. Capture only synthetic data and review every image for privacy, accuracy, and visual quality before publication.

## Naming convention

Use two-digit sequence numbers and descriptive lowercase names:

```text
screenshots/01_home_audit.png
screenshots/02_score_explainability.png
```

Keep stable names when replacing an approved view so README links do not break. Use PNG for UI captures.

## Gallery structure

The primary English gallery should tell a compact product story:

1. local-first home/audit input;
2. score explainability;
3. dashboard metrics;
4. risk heatmap;
5. evidence drill-down;
6. optional localhost Ollama boundary;
7. reports and exports;
8. read-only knowledge base.

Place French and Hebrew RTL screenshots in a separate internationalization section. This demonstrates localization without interrupting the primary English flow.

## Capture rules

- Use only bundled synthetic scenarios or clearly synthetic placeholders.
- Avoid browser bars, desktop panels, terminals, debug consoles, and notification overlays.
- Avoid local paths, emails, account names, machine names, IPs other than documented loopback addresses, tokens, and credentials.
- Do not show real report history, organization data, personal notes, or model output derived from real content.
- Prefer a clean light or dark theme with consistent viewport size and zoom.
- Capture the relevant tab content, not only the repeated page header.
- Keep important labels and values readable at GitHub README width.
- If feasible, hide or crop the Streamlit **Deploy** button for public polish without obscuring product content.
- Give every README image meaningful alt text that describes the feature, not the filename.

## Current public gallery checks

The current public gallery uses the ten stable README filenames:

- `03_dashboard_overview.png`: shows populated executive metrics or widgets and distinguishes current-session signals from saved local data.
- `06_local_ai_ollama.png`: shows localhost endpoint restrictions, availability, score guardrail, or synthetic test content.
- `07_reports_preview.png`: shows synthetic report/export content.
- `08_knowledge_base.png`: shows read-only local knowledge-base counts and representative content.

Keep privacy-reviewed images until improved captures pass the same review. Visual recaptures that do not address a privacy defect are non-blocking polish.

## Validation

Confirm all expected images exist and are non-empty:

```bash
for img in screenshots/*.png; do test -s "$img" || echo "BROKEN_IMAGE: $img"; done
```

Scan embedded printable strings before review:

```bash
strings -a -n 8 screenshots/*.png | grep -Ei "(/(Users|home)/|token|secret|password|api[_-]?key|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|github\.com)" || true
```

Also inspect pixels manually; a string scan cannot detect visible text rendered into the image.

## Visual redesign review gate

Do not replace the gallery until a human has reviewed both Light and Dark modes at desktop and narrow widths. The review must include the risk cockpit, a High or Critical evidence card, the simulation assumptions banner, the Local AI authority boundary, the integrated sidebar, disabled reset button, and Hebrew RTL behavior.

Temporary automated captures, if created, belong under `.aiwra-audit-output/visual-smoke/` and must not be added to Git.
