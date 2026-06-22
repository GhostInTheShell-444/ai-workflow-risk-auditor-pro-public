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
6. reports and exports;
7. read-only knowledge base;
8. optional localhost Ollama boundary.

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

## Recommended recaptures

- `03_dashboard_overview.png`: show populated executive metrics or widgets, clearly indicating whether signals are current-session or explicitly saved local data.
- `06_local_ai_ollama.png`: show localhost endpoint restrictions, availability, score guardrail, or synthetic test content.
- `07_reports_preview.png`: show a synthetic Markdown or JSON preview and export controls.
- `08_knowledge_base.png`: show rule/control/category counts and representative read-only rows.

Keep the current images for private iteration until improved captures pass human review.

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
