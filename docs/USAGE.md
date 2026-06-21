# Usage

Use synthetic or appropriately anonymized workflow descriptions. The app is a local review aid, not a compliance certification, production approval, or substitute for professional judgment.

## First run

1. Start the app using the command in [Installation](INSTALLATION.md).
2. In the sidebar, select a bundled synthetic scenario such as Customer Support.
3. Open **Audit** and select **Run audit**.
4. Read the score explanation and the Detected / Calculated / Simulated / Recommended / Uncertain labels.
5. Inspect each important finding's evidence phrase, rule identifier, confidence, score impact, and proposed control.
6. Review the top risks and actions.
7. Open **Simulation**, choose controls, and simulate residual risk.
8. Return to **Audit** to download Markdown and JSON reports. Downloads do not create saved history.
9. Select **Save analysis and report locally** only if you want the workflow and report in local SQLite history.
10. Open **Dashboard**, **Reports**, and **Knowledge Base** to inspect current results, intentional saves, and local rule content.
11. Optionally open **Local AI / Ollama** for a synthetic local-model test or narrative wording.
12. Use the language selector to switch between English, French, and Hebrew; Hebrew uses an RTL-aware layout.

## What to paste

Describe the workflow as short steps, including the data used, automated decisions or actions, external destinations, human approvals, logs, and error handling. For example:

```text
An anonymized customer message enters a support queue.
An AI system drafts a response using approved internal guidance.
A support agent reviews the draft before it is sent.
Complex complaints are escalated and the decision is logged.
```

Do not paste real names, contact details, health or payment data, credentials, production secrets, confidential documents, or regulated records. Prefer a synthetic scenario when evaluating the app.

## Reading scores and evidence

The raw matrix score is the sum of fixed weights for locally mapped risk factors. Its thresholds are Low (0–4), Medium (5–9), High (10–15), and Critical (16+). Higher scores indicate more detected reasons for human review; they are not probabilities, calibrated losses, legal conclusions, or compliance results.

Evidence shows the source phrase and deterministic rule behind a finding. Confirm that the phrase is relevant in the real business context. Confidence is a rule-based heuristic, not statistical confidence. See [Score Explainability](SCORE_EXPLAINABILITY.md) and [Score Calculation Trace](SCORE_CALCULATION_TRACE.md).

## Simulating controls

The **Simulation** tab applies predefined control-to-risk mappings to the current score. Compare the original and residual score, then inspect which assumptions produced the reduction. A lower simulated score does not prove that a control is implemented, effective, or sufficient.

## Exporting and saving

- Markdown and JSON downloads are generated locally and are available immediately after an audit.
- Downloading does not save the workflow to app history.
- The explicit save button writes the workflow, findings, report, and related audit events to `data/aiwra.db`.
- Saved reports appear in **Reports** and contribute to saved-history views in **Dashboard**.
- Review exported files before sharing; they can contain the workflow text and evidence you entered.

## Optional Ollama support

Ollama is not required. When enabled, the app accepts only loopback endpoints and blocks models identified as cloud/proxy-like. It can test a bundled synthetic prompt or draft narrative wording after an explicit action. It does not detect deterministic findings, calculate or validate scores, choose controls, change simulations, or certify compliance. Local-model output can still be wrong and requires review.

## Limitations

Pattern matching can miss context or produce false positives. The rule and knowledge collections are finite. Control effects are planning assumptions. Saved SQLite data is unencrypted and intended for one trusted local user. The app has no production integrations, authentication, tenant isolation, vulnerability scanning, automated remediation, or legal/compliance determination.
