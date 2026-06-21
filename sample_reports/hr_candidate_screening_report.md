# AI Workflow Risk Audit Report

## Workflow Summary
HR candidate screening workflow for anonymized application intake, qualification summarization, interview planning support, and human review before candidate-impacting decisions.

## Detected Workflow Steps
- Receive anonymized CV and application material.
- Summarize qualifications, skills, and interview availability.
- Prepare internal shortlist suggestions and interview checklists.
- Require HR review before ranking, scheduling, rejection, or other candidate-impacting decisions.
- Minimize candidate personal data and limit access.
- Keep an audit log of review decisions and final HR actions.

## Automation Opportunities
### Good candidates for AI assistance
- Summarize candidate material.
- Extract non-sensitive qualification signals.
- Prepare interview checklists and follow-up questions.

### Candidates requiring human approval
- Candidate ranking.
- Interview scheduling decisions.
- Rejection or advancement decisions.

### Poor candidates for automation
- Unreviewed HR decisions.
- Final candidate ranking without documented review.
- Any workflow that stores unnecessary candidate data.

### Guardrail recommendations
- Require HR approval for candidate-impacting outputs.
- Minimize personal data.
- Document review decisions.
- Keep access limited to the hiring team.

## Sensitive Data Involved
- Potentially involved: personal data.
- Potentially involved: HR / candidate data.

## Cybersecurity Risks
- Sensitive data exposure in prompts, summaries, or logs.
- Excessive access to candidate files.
- Weak auditability if review decisions are not documented.

## Privacy Risks
- Candidate and employee data may require stricter controls.
- Automated decisions affecting people need human oversight.
- Transparency, retention, and data minimization should be reviewed.

## Human-in-the-loop Checkpoints
- Review decisions that affect candidates.
- Validate sensitive data use.
- Approve any ranking, rejection, or scheduling decision.

## Risk Score
- Risk score: 9
- Risk level: Medium

## Score Explanation
- Personal data: +2
- HR / candidate data: +3
- Decision affecting a person: +4

## Recommended Safe Automation
- Use AI assistance for summarization, checklists, and internal preparation.
- Keep final candidate decisions with HR.
- Log review decisions for accountability.

## Minimal Architecture
- Local Streamlit interface.
- Deterministic analyzer and transparent risk rules.
- Markdown report export.
- Optional local LLM wording enrichment only.

## Implementation Notes
- Do not connect to HR systems in the MVP.
- Avoid persistent storage of submitted candidate text.
- Use anonymized examples only.

## Limitations
- Keyword-based findings may miss context.
- This report is advisory and not legal or compliance advice.
- The MVP analyzes and recommends only.
