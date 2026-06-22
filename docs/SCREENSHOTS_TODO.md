# Screenshot Capture Specification

The current ten screenshots are published in the README gallery and must remain synthetic and privacy-reviewed. Follow [Screenshot Guidelines](SCREENSHOT_GUIDELINES.md) for privacy, naming, gallery structure, string scans, and public-polish rules before replacing them.

| Filename | Purpose | What must be visible | What must not be visible | Privacy checks | README placement |
|---|---|---|---|---|---|
| `01_home_audit.png` | Establish the main workflow review experience. | Product title, local-first message, synthetic scenario selector, anonymized input, run button. | Browser profile, local path, real workflow, terminal, notifications. | Confirm the selected scenario is marked synthetic and contains no identifiers. | After “In one minute.” |
| `02_score_explainability.png` | Show why the score is understandable. | Score, severity, finding count, source/meaning/limit copy, calculation basis, disclaimer. | Naked numbers, clipped disclaimers, real report history. | Verify all evidence is synthetic and no hidden expander reveals real input. | “How scoring works.” |
| `03_dashboard_overview.png` | Present the visual product surface. | Executive KPI cards, local-only status, workflow graph, saved synthetic sample basis. | Personal timestamps if identifying, real projects, debug output. | Reset to seeded demo data; inspect card values and timestamps. | Primary README hero screenshot. |
| `04_risk_heatmap.png` | Demonstrate risk visualization. | Category/severity labels, counts, legend, explanatory subtitle. | Unlabeled colors, real evidence text, clipped RTL layout. | Use current synthetic audit or seeded aggregate data only. | Key features / dashboard section. |
| `05_evidence_drilldown.png` | Prove traceability from text to rule. | Synthetic source phrase, rule ID, severity, confidence, control, limitation. | Full real workflow, secrets, email addresses, tokens, hidden metadata. | Read the complete evidence phrase and rule before capture. | Score explainability section. |
| `06_local_ai_ollama.png` | Explain the optional local model boundary. | Endpoint, local status, blocked model count, deterministic guardrail, synthetic test panel. | Machine-specific model names if sensitive, real workflow prompt, remote host, model response with personal data. | Prefer Ollama unavailable or a synthetic-only response; verify loopback endpoint. | Optional Local AI section. |
| `07_reports_preview.png` | Show auditable output and history. | Markdown/JSON tabs, explicit-save wording, synthetic report title. | Local IDs that reveal prior use, real report text, filesystem paths. | Use a newly reset synthetic database and review both previews. | Sample reports section. |
| `08_knowledge_base.png` | Show inspectable local content. | Counts, search, read-only notice, one local rule/control view. | Internal file paths, irrelevant browser UI, user-created content. | Confirm only bundled JSON/seed content is displayed. | Key features section. |
| `09_french_ui.png` | Demonstrate French localization. | French labels across a complete audit or dashboard section. | Mixed English UI fragments except stable technical identifiers. | Review visible French wording and synthetic content manually. | Localization note. |
| `10_hebrew_rtl_ui.png` | Demonstrate RTL support. | Hebrew navigation, cards, labels, and right-to-left layout; technical blocks readable LTR. | Misaligned/clipped text, reversed endpoints, real data. | Review at desktop width and inspect code/model/endpoint direction. | Localization note. |

## Final image review

- Confirm dimensions and readable text at GitHub display width.
- Inspect metadata and remove location/device metadata if present.
- Search visible text for personal names, usernames, machine names, paths, credentials, and real identifiers.
- Confirm every input and report is synthetic.
- Confirm light and dark contrast where each theme is promoted.
- Obtain a final human visual approval before any public launch.
