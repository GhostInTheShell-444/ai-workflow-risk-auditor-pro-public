# AI Workflow Risk Audit Report

## Workflow Summary
SOC alert triage workflow for anonymized alert intake, severity classification, internal context summarization, escalation recommendation, and analyst review before security action.

## Detected Workflow Steps
- Receive anonymized security alert details from an internal queue.
- Classify severity and summarize safe internal context.
- Draft internal triage notes and suggested questions.
- Recommend escalation priority for analyst review.
- Require analyst approval before escalation, closure, or response.
- Keep an audit log of classification, review, escalation decision, and final status.

## Automation Opportunities
### Good candidates for AI assistance
- Alert summarization.
- Triage question suggestions.
- Internal note drafting.
- Escalation priority suggestions for analyst review.

### Candidates requiring human approval
- Incident escalation.
- Alert closure.
- Any response recommendation that affects security operations.

### Poor candidates for automation
- Autonomous incident containment.
- Blocking, deletion, or production changes.
- Unreviewed alert closure or escalation.

### Guardrail recommendations
- Keep the tool advisory.
- Require analyst review for every security recommendation.
- Maintain audit logs.
- Keep permissions narrow and separate from execution.

## Sensitive Data Involved
- Potentially involved: security event data.
- Potentially involved: business confidential data.

## Cybersecurity Risks
- Incorrect alert prioritization.
- Over-automation of incident response.
- Sensitive security context exposure.
- Excessive permissions if connected to security systems.

## Privacy Risks
- Security events may contain user, device, or account context.
- Retention and access policies should be reviewed.
- Third-party or cross-system processing should be assessed before integration.

## Human-in-the-loop Checkpoints
- Analyst review before escalation, closure, or response.
- Approval before any record change.
- Security review before connecting to operational tools.

## Risk Score
- Risk score: 20
- Risk level: Critical

## Score Explanation
- Decision affecting a person: +4
- Irreversible action: +4
- Data modification or deletion: +4
- Third-party integration: +2
- Sensitive system access: +3
- SOC / security workflow: +3

## Recommended Safe Automation
- Use AI assistance for summaries, checklists, and triage questions.
- Keep containment and response actions outside the MVP.
- Require analyst approval for all operational decisions.

## Minimal Architecture
- Local Streamlit interface.
- Deterministic analyzer and transparent risk rules.
- Markdown report export.
- Optional local LLM wording enrichment only.

## Implementation Notes
- Do not connect to SIEM or SOAR tools in the MVP.
- Do not execute containment or blocking actions.
- Use anonymized alert examples only.

## Limitations
- Keyword-based findings may miss context.
- This report is advisory and not a production SOC platform.
- The MVP analyzes and recommends only.
