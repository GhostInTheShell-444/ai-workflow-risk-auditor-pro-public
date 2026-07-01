# Customer Support Example Report

Synthetic example. No real customer data.

## How to read this report

This tool reads a workflow, detects risk clues, calculates a local rule-based risk score, explains why, recommends protections, and simulates the remaining risk. It does not certify compliance and does not replace human judgment.

This score is a rule-based estimate, not a statistical probability. Score calculated from local deterministic rules. It is an aid, not a certification.

## Simple glossary

- Detected = found in the text
- Calculated = computed by local rules
- Simulated = estimated scenario after protections
- Recommended = proposed action, not an obligation
- Uncertain = needs human review

## What this score means

Raw matrix score: 34, Critical.

Plain meaning: Critical risk estimated from local rules, mainly because the workflow mentions customer-facing support, customer context, policy exceptions, and external communication. This does not mean the workflow is forbidden. It means a human should review evidence and controls before automation.

## What is detected

- 16 evidence findings were detected in the text.
- Examples include customer emails, support tickets, customer-facing response, policy exceptions, and audit log.
- Each detected finding links to a local rule id in the app/report.

## What is calculated

- Compatibility score: 20, Critical.
- Raw matrix score: 34, Critical.
- Severity thresholds: low 0-4, medium 5-9, high 10-15, critical 16+.

## What is simulated

After default selected protections:

- Simulated residual score: 26, Critical.
- Simulated reduction: 8.

Selected controls are hypothetical unless implementation evidence is reviewed. This is not a guarantee.

## What is recommended

- Require human approval before external messages.
- Keep audit logs.
- Minimize data in prompts and reports.
- Display confidence labels.
- Keep recommendations separate from execution.

## Next 3 actions

1. Confirm that every external customer response is reviewed by a support agent.
2. Keep the audit log and retention policy explicit.
3. Use anonymized or minimum necessary customer context.

## Limitations

- Pattern matching can miss context.
- Findings can be false positives.
- Scores are deterministic indicators, not real-world probabilities.
- The report is not legal advice or compliance certification.
