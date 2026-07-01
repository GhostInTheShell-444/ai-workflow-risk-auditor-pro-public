# Theme Selector

## Behavior

The product header/settings area includes compact horizontal controls for interface language and appearance. The visible appearance options are:

- `light`
- `dark`

The selected value is stored in `st.session_state["theme_mode"]`, so it persists during the Streamlit session. The static `.streamlit/config.toml` remains a light local baseline because Streamlit theme config is not changed at runtime.

## System Fallback

`system` remains a supported internal value for compatibility and resolves through the existing token layer, but it is not shown as the primary product choice. Reliable browser or operating-system theme detection would require client JavaScript, which this local-first app does not inject.

## CSS Variables

Runtime styling is controlled by CSS variables generated from `design_tokens.THEMES`:

- `--aiwra-bg`
- `--aiwra-page-bg`
- `--aiwra-shell-bg`
- `--aiwra-sidebar-bg`
- `--aiwra-workbench-bg`
- `--aiwra-surface`
- `--aiwra-surface-alt`
- `--aiwra-panel-bg`
- `--aiwra-card-bg`
- `--aiwra-elevated-card-bg`
- `--aiwra-input-bg`
- `--aiwra-text`
- `--aiwra-text-primary`
- `--aiwra-text-secondary`
- `--aiwra-muted`
- `--aiwra-disabled-text`
- `--aiwra-border`
- `--aiwra-border-soft`
- `--aiwra-shadow`
- `--aiwra-primary`
- `--aiwra-accent`
- `--aiwra-local`
- `--aiwra-advisory`
- `--aiwra-info`
- `--aiwra-success`
- `--aiwra-warning`
- `--aiwra-danger`
- `--aiwra-button-primary-bg`
- `--aiwra-button-secondary-bg`
- `--aiwra-button-ghost-bg`
- `--aiwra-button-danger-bg`
- `--aiwra-button-disabled-bg`
- `--aiwra-button-download-bg`
- `--aiwra-focus-ring`
- `--aiwra-critical`
- `--aiwra-high`
- `--aiwra-medium`
- `--aiwra-low`
- `--aiwra-loading`
- `--aiwra-loading-border`
- `--aiwra-loading-deterministic`
- `--aiwra-loading-local-ai`
- `--aiwra-loading-simulation`
- `--aiwra-loading-export`

The cockpit header, settings bar, start workbench, sidebar control rail, state panels, loading panels, custom cards, bento panels, badges, heatmap cells, matrix cards, timeline items, inputs, buttons, alerts, and code blocks use these variables.

## Streamlit Limits

Native Streamlit widgets do not expose a stable public runtime-theme API. The app therefore applies a local token layer to page and sidebar backgrounds, settings controls, panels, cards, alerts, expanders, tabs, tables, metrics, selectboxes, text inputs, textareas, primary/secondary/ghost/danger/download/disabled buttons, code blocks, and focus states. A future Streamlit upgrade can still require selector review.

Dark mode uses opaque layered navy/graphite surfaces and does not intentionally rely on transparent buttons. Motion honors `prefers-reduced-motion`. The 2026 cockpit palette uses petroleum blue, cyan/green local-first cues, restrained advisory violet/amber, and separate danger/severity colors.

Dark mode must be reviewed visually. The token contract covers sidebar, page, workbench, input, alert, card, button, disabled, and focus states, but Streamlit internals can change between versions.

## Non-Effects

The theme selector does not change deterministic scoring, SQLite storage, exports, local-only behavior, or Ollama guardrails.
