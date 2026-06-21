# Visual Design System

## Purpose

The local Streamlit design system includes runtime Light, Dark, and System appearance modes, localized dynamic labels, and dense dashboard components. It uses no external fonts, cloud assets, CDN, or heavy UI framework.

## Local Typography

The CSS stack is:

```css
font-family: Lato, Inter, "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
```

Lato and Inter are used only if already available on the user's machine. The app does not download Google Fonts and does not include proprietary font files.

## Palette

The palette is tokenized in `design_tokens.THEMES`.

- Light uses `#F6F8FB`, white surfaces, slate text, blue primary, and clear severity colors.
- Dark uses `#0B1120`, raised slate surfaces, light text, blue primary, and brighter severity colors.
- System resolves to Light to avoid browser-detection JavaScript.

Required CSS variables include `--aiwra-bg`, `--aiwra-surface`, `--aiwra-surface-alt`, `--aiwra-text`, `--aiwra-muted`, `--aiwra-border`, `--aiwra-shadow`, `--aiwra-primary`, `--aiwra-critical`, `--aiwra-high`, `--aiwra-medium`, and `--aiwra-low`.

## Severity Tokens

Severity values are stable technical keys:

- `low`: low review priority from local evidence.
- `medium`: moderate review priority; confirm controls before use.
- `high`: high review priority; human approval expected before production use.
- `critical`: critical review priority; do not automate without strong human governance.
- `unknown`: severity could not be determined from local data.

Each severity has a localized label, short description, foreground color, background color, and badge border.

## Status Tokens

Status values are stable technical keys:

- `detected`
- `calculated`
- `simulated`
- `recommended`
- `uncertain`
- `needs_human_review`
- `read_only`
- `demo`
- `local_only`
- `not_available`

Each status has a localized label, description, color, and intended usage. Statuses are text-first; color is secondary.

## Dashboard Components

- Bento cards: executive cockpit overview with source, meaning, and limit.
- Metric cards: saved local history metrics and local AI status.
- Heatmap: text-first category by severity grid.
- Matrix cards: impact, likelihood, factor count, severity, and limits.
- Evidence cards: source phrase, rule, confidence, recommended action, and limit.
- Issue cards: local follow-up only, never production ticket claims.

## CSS Scope

CSS is local and minimal. It improves cards, badges, section headers, metric cards, bento panels, heatmap cells, workflow graph steps, timeline items, tables, spacing, code blocks, and RTL rendering.

## Non-Goals

- No cloud fonts.
- No SaaS styling.
- No animation.
- No new UI framework.
- No claims that scores are scientific or compliance certification.
- No remediation-applied claims.
