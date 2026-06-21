# AI Workflow Risk Audit Report

## Workflow Summary
Customer support workflow for anonymized email intake, request classification, response drafting, escalation, and human approval before customer-facing communication.

## Detected Workflow Steps
- Receive anonymized customer emails and support tickets.
- Classify requests by topic, urgency, and required department.
- Draft suggested responses from approved knowledge base content.
- Review customer account context before approving a reply.
- Escalate complaints, refunds, or policy exceptions to a manager.
- Keep an audit log of classification, review, approval, and final response.

## Automation Opportunities
### Good candidates for AI assistance
- Request classification by topic and urgency.
- Internal draft notes and response suggestions.
- Escalation category suggestions.

### Candidates requiring human approval
- Customer-facing replies.
- Refund or policy exception recommendations.
- Escalations that change customer treatment.

### Poor candidates for automation
- Unreviewed customer-facing messages.
- Final policy exception decisions.
- Any action that modifies customer records without approval.

### Guardrail recommendations
- Use approved source content only.
- Require human approval before sending.
- Keep audit logs for drafts, reviews, and final decisions.
- Minimize customer data in prompts and notes.

## Sensitive Data Involved
- Potentially involved: customer data.
- Potentially involved: legal / compliance data for refunds or policy exceptions.

## Cybersecurity Risks
- Sensitive data exposure through drafts, prompts, or logs.
- Unreviewed external communication.
- Prompt injection risk in customer-submitted email content.
- Weak auditability if review decisions are not logged.

## Privacy Risks
- Customer data may appear in workflow inputs and outgoing messages.
- External communication increases privacy exposure.
- Data minimization and retention expectations should be defined.

## Human-in-the-loop Checkpoints
- Approve all customer-facing messages before sending.
- Review refunds, complaints, and policy exceptions.
- Validate sensitive data use before including context in a draft.

## Risk Score
- Risk score: 10
- Risk level: High

## Score Explanation
- Customer data: +2
- Legal / compliance data: +3
- External communication: +2
- Customer-facing automated output: +3

## Recommended Safe Automation
- Use AI assistance for classification, summarization, internal notes, and draft suggestions.
- Keep the final reply decision with a support agent.
- Separate recommendation from message sending.

## Minimal Architecture
- Local Streamlit interface.
- Deterministic analyzer and transparent risk rules.
- Markdown report export.
- Optional local LLM wording enrichment only.

## Implementation Notes
- Do not connect directly to email or ticketing systems in the MVP.
- Use anonymized examples.
- Keep review logs for demo decisions.

## Limitations
- Keyword-based findings may miss context.
- This report is advisory and not compliance certification.
- The MVP analyzes and recommends only.
