# Theme Selector

## Behavior

The sidebar includes an `Appearance` selector with stable internal values:

- `light`
- `dark`
- `system`

The selected value is stored in `st.session_state["theme_mode"]`, so it persists during the Streamlit session. The static `.streamlit/config.toml` remains light because Streamlit theme config is not changed at runtime.

## System Fallback

`System` resolves to the light token set. Reliable browser or operating-system theme detection would require client JavaScript, which this local-first app does not inject.

## CSS Variables

Runtime styling is controlled by CSS variables generated from `design_tokens.THEMES`:

- `--aiwra-bg`
- `--aiwra-surface`
- `--aiwra-surface-alt`
- `--aiwra-text`
- `--aiwra-muted`
- `--aiwra-border`
- `--aiwra-shadow`
- `--aiwra-primary`
- `--aiwra-critical`
- `--aiwra-high`
- `--aiwra-medium`
- `--aiwra-low`

Custom cards, bento panels, badges, heatmap cells, matrix cards, timeline items, and code blocks use these variables.

## Streamlit Limits

Native Streamlit widgets do not expose full runtime theme control. The app styles the page background, sidebar, custom HTML components, code blocks, and data containers, while Streamlit selectboxes and buttons may retain some native styling.

## Non-Effects

The theme selector does not change deterministic scoring, SQLite storage, exports, local-only behavior, or Ollama guardrails.
