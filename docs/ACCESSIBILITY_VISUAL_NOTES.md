# Accessibility Visual Notes

## Measures Implemented

- Colors are never the only source of meaning.
- Badges include text labels such as severity, status, and source.
- Heatmap cells include category, severity, count, and explanatory text.
- Matrix cells include impact, likelihood, count, severity, factors, and limit.
- KPI cards include source, meaning, and limit.
- Executive bento cards include localized title, value, source, meaning, and limit.
- The app shell exposes project, language/theme, local-first, and Local AI status through escaped text-first HTML.
- The top settings bar exposes language and Light/Dark appearance as display-only controls outside the sidebar.
- The command cockpit summarizes deterministic authority, local boundary, session state, and human-review gate before the input controls.
- The first viewport exposes workflow source, import, paste area, and Analyze Workflow in the main content.
- Mission Pulse appears once in the Start/Input view and the local pipeline strip stays compact, text-labeled, and secondary to the deterministic state.
- Sidebar navigation uses a visible active state and stable labels, but language/theme and the main workflow source do not depend on sidebar recall.
- Buttons use distinct primary, secondary, ghost, danger, download, and disabled styling with visible text labels.
- State panels explicitly label empty, input-ready, error, partial, success, and export/report states.
- Loading panels explicitly distinguish deterministic analysis, advisory Local AI wording, hypothetical simulation, and local export/report preparation. The deterministic loading state may show the local pipeline strip but Local AI is not a primary pipeline stage.
- Empty, warning, and unavailable states use explicit text.
- Knowledge Base views replace confusing booleans with readable badges and labels.
- Hebrew RTL receives layout styling and deliberate primary-action placement in the workbench, while code/prompt blocks remain LTR.
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
- Verification that the sidebar active state and destructive-action confirmations remain readable in light and dark modes.
- Verification that the settings bar remains compact and readable in EN/FR/HE.
- Verification that deterministic, Local AI, simulation, export loading states, Mission Pulse, pipeline, and live cockpit cues do not imply LLM score authority or certification.
- Verification that no literal HTML tags, CSS fragments, or escaped component markup are visible in EN/FR/HE.
- Verification that Streamlit Deploy/developer affordances are hidden or mitigated by viewer toolbar mode.

## Limits

Streamlit component internals limit precise ARIA control. The app compensates with visible text labels, explicit headings, product loading copy, and reduced reliance on color.

System theme compatibility uses the local token layer and requires no client-side JavaScript. Non-essential transitions, Mission Pulse, pipeline orb, cockpit scan, loading orb, and status-dot animation are disabled through `prefers-reduced-motion`.

High-contrast focus-visible rings are applied to buttons, inputs, textareas, tabs, and combobox controls. Severity, local-only, save, review, destructive, download, disabled, and simulation states retain text labels and symbols so animation and color are never required to understand status.

Human visual review remains mandatory. These notes are implementation targets, not WCAG certification or publication acceptance.
