# Visual Design System

## Purpose

The local Streamlit design system presents the deterministic engine as a serious audit command center. Runtime Light, Dark, and System modes share localized, engine-aware components and use no external fonts, cloud assets, CDN, remote image, script, telemetry, or heavy UI framework.

## Local Typography

The CSS stack is:

```css
font-family: "Lato", "Noto Sans Hebrew", "Rubik", "Segoe UI Variable", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
```

The app does not download fonts or include proprietary font files. The stack is local/offline-first and gives Hebrew a deliberate fallback path. Code, JSON, paths, model names, endpoints, prompts, and reports remain monospace/LTR where appropriate.

## Palette

The palette is tokenized in `design_tokens.THEMES`.

- Light uses a restrained cockpit canvas, opaque white/elevated cards, dark neutral text, blue primary, teal accent, and distinct severity colors.
- Dark uses opaque layered local surfaces, high-contrast text, blue/teal controls, and brighter severity colors.
- System remains an internal compatibility mode. The visible product control prioritizes Light and Dark.

Required variables include page/shell/sidebar/workbench backgrounds, panel/card/elevated-card/input surfaces, border and soft-border roles, primary/secondary/muted/disabled text, primary, accent, local, advisory, info, success, warning, danger, Low/Medium/High/Critical, detected/calculated/simulated/recommended/uncertain, primary/secondary/ghost/danger/disabled/download button states, focus ring, loading roles, state backgrounds, shadow, and gradient tokens.

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

## First Viewport

The first visible audit screen is a start/analyze workbench, not a marketing hero. It shows:

- AIWRA product name and local-first deterministic identity.
- Active project, top-bar language/theme, and Local AI advisory state.
- Main workflow source selector, local text/Markdown import, paste area, and `Analyze Workflow`.
- Secondary `Load example`, `Clear input only`, and confirmed `Clear current session` actions.
- Privacy warning, deterministic source-of-truth statement, score disclaimer, and Local AI boundary.

The workflow path is available in the main content. The sidebar is a control rail, not the only way to understand or start the product.

## Action System

Buttons are differentiated by meaning:

- Primary: `Analyze Workflow`, the only forward primary action in the start/input view.
- Secondary: save report, load example, clear input, save simulation, create project.
- Tertiary/ghost: post-analysis shortcuts to evidence, simulation, reports, and Local AI.
- Download: Markdown and JSON downloads, distinct from local SQLite save.
- Danger: delete active project and reset demo database, both separated and confirmed.
- Disabled: visible text remains readable and the nearby explanation gives the reason.

Cards are informational by default. A card that contains an action must contain an explicit Streamlit button; cards are not styled as clickable buttons.

## Dashboard Components

- App shell header: controlled escaped HTML component with AIWRA identity, loopback/local-first badge, active project, language/theme, and optional Local AI status.
- Workspace settings bar: compact top-bar controls for language and Light/Dark appearance. These are display settings only and never affect deterministic analysis.
- Command cockpit: four text-first cards for deterministic authority, local boundary, project/session, and human-review gate.
- Start/analyze workbench: source selector, import, paste area, Analyze, secondary actions, privacy/source-of-truth support, and Local AI boundary.
- Mission Pulse and local pipeline strip: one primary state pulse near the Start/Input action area, followed by a compact strip for input, local rules, evidence, human review, and report readiness.
- State panels and loading panels: empty, input-ready, deterministic-running, local-AI-running, simulation-running, export/report, partial, success, and unavailable states with explicit next action.
- Risk cockpit: raw score, severity, finding count, human-review requirement, local-only status, explicit-save state, and simulation state, with subtle scan/glow cues that never imply certification.
- Bento cards: executive cockpit overview with source, meaning, and limit.
- Metric cards: saved local history metrics and local AI status.
- Heatmap: text-first category by severity grid.
- Matrix cards: impact, likelihood, factor count, severity, and limits.
- Evidence cards: source phrase, rule, confidence, score impact, why it matters, review question, simulation assumption, recommended action, and limit.
- Control cards: recommended-not-verified status, technical ID, reason, implementation check, mapped factors, and limitation.
- Simulation cockpit and table: before/after score, hypothetical reduction, selected controls, remaining factors, assumption warning, evidence required, implementation check, and limitation.
- Local AI reviewer module: deterministic authority, loopback boundary, allowed role, local inventory, prompt preview, and response panel.
- Issue cards: local follow-up only, never production ticket claims.

## CSS Scope

CSS is local and scoped around stable Streamlit test IDs, widget keys, and AIWRA classes. It harmonizes the native header, settings bar, workbench, sidebar control rail, cards, badges, state panels, loading panels, primary/secondary/ghost/danger/disabled/download buttons, inputs, selectboxes, textareas, secondary tabs, expanders, alerts, tables, metrics, code blocks, spacing, responsive layout, and RTL rendering.

The first viewport uses local product surfaces only. No remote image, external font, CDN, or script is loaded. Decorative radial/orb backgrounds are avoided. Streamlit app chrome is mitigated through `.streamlit/config.toml` with `[client] toolbarMode = "viewer"` and cautious toolbar de-emphasis; screenshots still require human review.

## Motion and accessibility

Motion is limited to short hover elevation, focus transitions, Mission Pulse, local pipeline orb, local-status dot, and subtle cockpit scan cues. Warnings do not blink. `@media (prefers-reduced-motion: reduce)` disables animations and transitions.

Loading states use a text label, explanatory copy, and a small spinner that is disabled under reduced motion. Severity always includes a text label and symbol or explicit context. Focus-visible controls receive a high-contrast ring. Technical endpoints, prompts, responses, and code remain LTR in Hebrew mode.

## Unsafe HTML boundary

`unsafe_allow_html=True` is used only for controlled component templates and static CSS. The product header, command cockpit, state panels, evidence cards, and workbench frame escape dynamic component values. Raw workflow text is never inserted as uncontrolled HTML, and user values cannot inject CSS.

## Human Review Gate

These visual rules do not certify the UI. Light, dark, desktop, mobile, and Hebrew RTL screenshots must be reviewed by Eric before any acceptance or publication decision.

## Non-Goals

- No cloud fonts.
- No SaaS styling.
- No heavy or continuous animation.
- No new UI framework.
- No claims that scores are scientific or compliance certification.
- No remediation-applied claims.
