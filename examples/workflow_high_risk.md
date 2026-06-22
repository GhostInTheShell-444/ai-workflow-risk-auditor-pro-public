# High-Risk Teaching Example: Synthetic Eligibility Automation

This scenario is intentionally unsafe and entirely fictional. Every identifier is a placeholder. `EXAMPLE_NOT_A_SECRET` is not a usable credential.

## Workflow

```text
A fictional applicant record labeled DEMO_ONLY_APPLICANT_001 contains synthetic age, income, health, and location fields.
An AI model assigns an eligibility score and automatically approves or rejects a high-impact benefit.
The decision is sent to a fictional external endpoint using the placeholder EXAMPLE_NOT_A_SECRET.
No human reviews the decision before it takes effect.
The applicant cannot appeal, and the workflow does not record model inputs, evidence, policy version, or decision rationale.
Administrators can overwrite records without role separation or an audit trail.
```

## Review focus

- The workflow combines synthetic sensitive data with a high-impact automated decision.
- It intentionally lacks meaningful human review, appeal, traceability, and access separation.
- The external action and credential placeholder are demonstrations only; do not substitute real endpoints or secrets.
- A qualified legal, privacy, security, and domain review would be mandatory before any real implementation.
