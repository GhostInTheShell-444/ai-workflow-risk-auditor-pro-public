# AI Workflow Risk Audit Report

## Workflow Summary
Logistics and transport operations workflow for anonymized delivery intake, route or dispatch planning support, customer notification drafting, exception handling, and dispatcher approval.

## Detected Workflow Steps
- Receive anonymized delivery requests with customer contact, location, schedule, and shipment constraints.
- Summarize delivery requirements.
- Suggest route or dispatch planning options.
- Draft customer updates for delay, ETA, or exception handling.
- Require dispatcher approval before customer communication or dispatch-impacting change.
- Keep an audit log of recommendations, approvals, messages, and final operational status.

## Automation Opportunities
### Good candidates for AI assistance
- Delivery request summarization.
- Route option comparison for dispatcher review.
- Customer update drafting.
- Exception flagging.

### Candidates requiring human approval
- External customer notifications.
- Dispatch-impacting changes.
- Exception handling that affects delivery commitments.

### Poor candidates for automation
- Unreviewed dispatch changes.
- Autonomous customer notifications.
- Any action that changes operational records without approval.

### Guardrail recommendations
- Require dispatcher review before action.
- Minimize location and contact data in prompts.
- Log route suggestions, approvals, and customer messages.
- Keep integrations outside the MVP.

## Sensitive Data Involved
- Potentially involved: personal data.
- Potentially involved: customer data.
- Potentially involved: location / logistics data.

## Cybersecurity Risks
- Sensitive data exposure through drafts or logs.
- Unreviewed external communication.
- Prompt injection risk in customer-submitted delivery notes.
- Weak auditability if dispatch decisions are not logged.

## Privacy Risks
- Customer, contact, and location data may be involved.
- External messaging increases privacy exposure.
- Retention and data minimization rules should be defined.

## Human-in-the-loop Checkpoints
- Approve customer-facing updates before sending.
- Review dispatch-impacting changes.
- Validate sensitive data use.

## Risk Score
- Risk score: 9
- Risk level: Medium

## Score Explanation
- Personal data: +2
- Customer data: +2
- External communication: +2
- Customer-facing automated output: +3

## Recommended Safe Automation
- Use AI assistance for summaries, draft updates, and exception flags.
- Keep dispatch decisions with a human dispatcher.
- Separate recommendation from operational execution.

## Minimal Architecture
- Local Streamlit interface.
- Deterministic analyzer and transparent risk rules.
- Markdown report export.
- Optional local LLM wording enrichment only.

## Implementation Notes
- Do not connect to transport, CRM, or notification systems in the MVP.
- Use anonymized delivery examples only.
- Keep audit logs for recommendations and approvals.

## Limitations
- Keyword-based findings may miss context.
- This report is advisory and not a production dispatch system.
- The MVP analyzes and recommends only.
