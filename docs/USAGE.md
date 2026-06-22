# Usage

Use synthetic or appropriately anonymized workflow descriptions. AI Workflow Risk Auditor Pro is a local review aid, not a compliance certification, legal opinion, production approval, or substitute for professional judgment.

## First run

1. Follow [Installation](INSTALLATION.md) and open `http://127.0.0.1:8501`.
2. Keep **Use local Ollama enrichment** disabled unless you intentionally installed a local model.
3. In **Example workflow**, choose a bundled synthetic scenario or **Custom workflow**.
4. Open **Audit**.

## Create or paste a synthetic workflow

Describe the inputs, decisions, external destinations, human approvals, logging, and failure behavior as short steps. For example:

```text
An anonymized support message enters a local review queue.
An AI system drafts a response from approved synthetic guidance.
A support agent reviews and approves the draft before sending.
Complex cases are escalated and the final decision is logged.
```

Do not paste real names, contact details, health or payment records, credentials, private source code, confidential documents, or production secrets. The [examples directory](../examples/README.md) contains safe synthetic workflows.

## Run an audit

1. Select **Analyze Workflow**.
2. Confirm the page shows a raw risk indicator, risk level, and finding count.
3. Read the source, meaning, and limitation on each metric card.
4. Treat findings as attention points for human review, not proof of harm.

Analysis is held in the active Streamlit session. It is not added to report history until you explicitly save it.

## Read the score

The raw score sums fixed local factor weights. Thresholds are Low (0–4), Medium (5–9), High (10–15), and Critical (16+). A higher score indicates more or stronger detected review factors.

The score is not a probability, calibrated loss estimate, legal conclusion, compliance determination, or permission to automate. Open **View calculation basis** to inspect factors and score impact. See [Score Explainability](SCORE_EXPLAINABILITY.md).

## Read evidence, rules, and confidence

Findings are ordered by severity and include:

- the matched workflow phrase;
- the local rule identifier;
- category and severity;
- a deterministic confidence heuristic;
- recommended controls or review actions.

Open a finding and confirm that the evidence matters in the intended business context. Confidence is not statistical confidence and does not remove the need for human review.

## Review recommended controls

Review the **Top 3 actions** and the complete finding list. Recommendations are proposed safeguards, not implemented changes. Confirm ownership, feasibility, evidence of implementation, and applicable legal/security requirements outside this app.

## Run a residual-risk simulation

1. Open **Simulation** after a valid audit.
2. Select proposed controls.
3. Select **Simulate residual risk**.
4. Compare original and residual scores and inspect remaining factors.

Simulation uses fixed control-effect mappings. A lower residual score does not prove a control exists, works, or is sufficient. Saving a simulation to history requires a saved assessment.

## Explore the dashboard

Open **Dashboard** to review current-session evidence or aggregates from reports explicitly saved in local SQLite. Its sub-tabs include overview, risks and evidence, controls, and history. Empty saved-history metrics are expected before the first explicit save.

## Use Reports

The **Reports** tab lists explicitly saved reports and provides Markdown and JSON previews and downloads. To populate it:

1. Run an audit.
2. Use **Save analysis and report locally** in **Audit**.
3. Return to **Reports** and choose the saved item.

Reports can contain the submitted workflow and matched evidence. Review them before sharing.

## Use the Knowledge Base

Open **Knowledge Base** to search and browse read-only local risk patterns, controls, data categories, demo scenarios, and explanation cards. These collections are inspectable aids; their size does not establish completeness or certification.

## Use Local AI / Ollama

Ollama is optional. The **Local AI / Ollama** tab shows availability, loopback endpoint restrictions, installed local models, blocked cloud/proxy-like models, the exact synthetic prompt, and any response.

When a local model is available, you may run the bundled synthetic test or explicitly generate narrative wording for the current report. Local-model output cannot alter findings, scores, controls, or residual-risk simulation and may be inaccurate. See [Ollama Local Diagnostics](OLLAMA_LOCAL_DIAGNOSTICS.md).

## Change language and direction

Use **Language** in the sidebar:

- English: left-to-right.
- Français: left-to-right French catalog.
- עברית: RTL-aware Hebrew catalog.

Technical identifiers, JSON, model names, endpoints, and some source evidence may remain LTR. Changing language changes presentation, not the deterministic authority of the analysis.

## Export without saving

After an audit, use the Markdown and JSON download buttons in **Audit**. Downloads are generated locally and do not create report history. JSON keeps stable technical keys; explanatory values may be localized where supported.

## Save or clear local data

Select **Save analysis and report locally** only when you want local history in `data/aiwra.db`. This SQLite database is not encrypted by the app.

To reset:

1. Back up `data/aiwra.db` if needed.
2. Read the sidebar warning.
3. Select the deletion confirmation.
4. Select **Reset demo database**.

The reset deletes saved local reports and recreates synthetic seed data. Alternatively, stop Streamlit and delete only `data/aiwra.db`; it is recreated on the next launch.

## Safe-use boundaries and limitations

- Use synthetic or appropriately anonymized text only.
- Do not expose the Streamlit server to untrusted networks.
- Do not use the app as multi-user software; it has no authentication, authorization, or tenant isolation.
- SQLite is local and unencrypted unless the surrounding environment adds its own protection.
- Pattern matching can miss context or produce false positives.
- Recommended controls and simulated reductions are planning assumptions.
- Optional local-model output requires review.
- The app does not connect to production systems or perform remediation.
- A qualified human must assess real legal, compliance, privacy, security, and operational obligations.
