# Frequently Asked Questions

## Does the app send my data to the cloud?

The deterministic audit does not. It runs in the local Streamlit process using Python and local JSON files. Workflow text is not automatically transmitted or saved. Optional Ollama calls are restricted by the app to loopback hosts and occur only after an explicit action. A locally installed model/service still must be trusted independently.

## Is Ollama required?

No. Auditing, evidence, scoring, controls, simulation, dashboard, knowledge base, Markdown/JSON exports, and SQLite history work without Ollama. Ollama only provides optional narrative wording and cannot change deterministic results.

## Where is my data stored?

Current analysis is held in Streamlit session state. When you explicitly save a report, the workflow, assessment, findings, controls, report, and related events are written to project-local `data/aiwra.db`. Downloads do not create report history.

## Is the SQLite database encrypted?

No. The application does not encrypt `data/aiwra.db`. Use it only on a trusted machine with appropriate operating-system access controls and storage protection. Do not save sensitive production data.

## Can I use real production workflows?

Use bundled synthetic workflows or carefully anonymized descriptions. Do not paste credentials, personal data, regulated records, confidential text, or production secrets. The tool is not a data-loss-prevention control and cannot guarantee that input was anonymized correctly.

## Can this replace legal or compliance review?

No. Scores and confidence values are deterministic heuristics. The app does not certify compliance, provide legal advice, approve production use, or know every contextual obligation. Qualified humans remain responsible.

## Does selecting a control prove it exists?

No. Simulation controls are hypothetical unless a reviewer provides implementation evidence. The app shows mapped factors, assumptions, evidence required, implementation checks, limitations, and remaining factors. Unrelated factors are not reduced.

## What does optional local AI add?

Local AI can draft wording, summarize deterministic evidence, identify missing context, and propose reviewer or challenge questions. It cannot change findings, scores, controls, or residual-risk math.

## Can I expose the Streamlit app on the internet?

Do not expose this build to untrusted networks. It has no user authentication, authorization, tenant isolation, encrypted database, or hardened remote-deployment boundary. Run it on a trusted machine bound to `127.0.0.1`.

## Why is there a Hebrew RTL screenshot?

The application includes English, French, and Hebrew locale catalogs. The screenshot demonstrates RTL-aware Hebrew layout and belongs in the internationalization section rather than the primary English product flow. Technical identifiers and some evidence remain LTR by design.

## Why are scores deterministic?

Fixed rules and factor weights make the same input reproducible and let reviewers inspect why points were added. This improves traceability, but deterministic does not mean complete, objectively correct, or statistically calibrated.

## What should I do if GitHub screenshots do not render?

Confirm the file exists, is tracked in the viewed branch, matches path capitalization, is a non-empty PNG, and is referenced with repository-relative Markdown such as `![Description](../screenshots/01_home_audit.png)`. Confirm the image commit is present on the public branch being viewed. See [Screenshot Guidelines](SCREENSHOT_GUIDELINES.md).

## How do I run tests?

Activate the Python 3.12 virtual environment, then run:

```bash
python -m pytest
python -m compileall app.py analyzer.py database.py repositories.py workflow_parser.py report_renderer.py export_json.py score_explainability.py design_tokens.py ui_components.py tests locales
```

Ollama and cloud credentials are not required.

## How do I reset local data?

Back up `data/aiwra.db` if needed. In the sidebar, read the warning and details, select the deletion confirmation, and select **Reset demo database**. This deletes saved projects, workflows, assessments, findings, simulations, reports, and audit events from that database, then recreates synthetic seed data. It does not delete code, docs, screenshots, tests, examples, knowledge-base JSON, or exports outside the database.

Use the narrower action when appropriate: **Clear input only** preserves the current analysis and saved history; **Clear current session** preserves saved history; **Delete active project** removes only the selected non-demo project and its related records. The bundled synthetic demo project cannot be deleted.

## Can I launch AIWRA from the desktop?

Yes. Linux has a user-local `.desktop` installer, and Windows/macOS helper scripts are provided. The launcher still runs the project’s `.venv`, binds only to `127.0.0.1:8501`, and requires no administrator privileges. See [Desktop Launcher](DESKTOP_LAUNCHER.md).

## Where are launcher logs stored?

Linux writes to `${XDG_STATE_HOME:-$HOME/.local/state}/aiwra/aiwra-launch.log`. macOS writes to `~/Library/Logs/AIWRA/aiwra-launch.log`. The Windows helper keeps a PowerShell window open so startup output remains visible. The Linux helper does not intentionally log the project path or workflow content, but Streamlit and dependency diagnostics may expose local environment details. Treat logs as private runtime artifacts, review them before sharing, and remove them when no longer needed.

## Does Dark mode change risk results?

No. Theme selection changes CSS tokens and presentation only. Risk factors, weights, thresholds, evidence semantics, and residual-risk calculations are unchanged.

## Why does motion stop on some systems?

The UI respects `prefers-reduced-motion`. Status pulses and transitions are disabled when the operating system or browser requests reduced motion.
