# Accessibility Visual Notes

## Measures Implemented

- Colors are never the only source of meaning.
- Badges include text labels such as severity, status, and source.
- Heatmap cells include category, severity, count, and explanatory text.
- Matrix cells include impact, likelihood, count, severity, factors, and limit.
- KPI cards include source, meaning, and limit.
- Executive bento cards include localized title, value, source, meaning, and limit.
- Empty, warning, and unavailable states use explicit text.
- Knowledge Base views replace confusing booleans with readable badges and labels.
- Hebrew RTL receives layout styling, while code/prompt blocks remain LTR.
- Light and dark tokens are checked for contrast by design review, with manual screenshot review still required.
- Code, JSON, prompt, and report preview blocks use theme-aware surfaces.

## Visual Impairment Readiness

The UI is designed to remain understandable if colors are removed. Users can read counts, labels, source, status, and limits directly.

## Manual Checks Still Required

- Browser zoom at 125%, 150%, and 200%.
- Color-blindness simulation or grayscale review.
- Desktop and mobile viewport screenshots.
- Native Hebrew speaker review for long RTL text.
- Keyboard navigation through Streamlit controls.

## Limits

Streamlit component internals limit precise ARIA control. The app compensates with visible text labels, explicit headings, and reduced reliance on color.

System theme detection falls back to the light token set because the app avoids client-side JavaScript.
