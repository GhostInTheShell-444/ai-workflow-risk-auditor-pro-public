# Case Study: Customer Support AI Automation Review

## Context

A support team wants to use AI to help with customer email triage and draft suggested responses. The team needs a clear boundary between useful assistance and unsafe automation.

## Initial Workflow

```text
A customer support inbox receives anonymized customer emails and support tickets.
The team classifies each request by topic, urgency, and required department.
An AI workflow may draft a suggested answer using approved knowledge base content.
A support agent reviews the draft, checks customer account context, and approves any customer-facing response before sending.
Complex complaints, refunds, or policy exceptions are escalated to a manager.
The process keeps an audit log of classification, review, approval, and final message decisions.
```

## Detected Risks

- Customer data may be processed.
- External communication may expose incorrect or sensitive content.
- Automated drafts may become customer-facing without approval if controls are weak.
- Refunds or policy exceptions require manager review.
- User-submitted messages may contain misleading instructions.

## Evidence

Representative evidence:

- `customer emails and support tickets`
- `AI workflow may draft a suggested answer`
- `approves any customer-facing response before sending`
- `refunds, or policy exceptions`
- `audit log of classification, review, approval`

## Controls

Recommended controls include:

- Human approval before external message.
- Audit trail.
- Data minimization.
- Disable autonomous sending.
- Approved output templates.
- Manager review for exceptions.

## Before / After Simulation

Example local simulation:

```text
Raw risk: High / 13
Selected controls:
- Human approval before external message
- Audit trail
- Data minimization
- Disable autonomous sending
Residual risk: Medium / 6
Reduction: -7
```

The numbers are deterministic planning estimates based on local control mappings. They are not production assurance.

## Human Validation Plan

- Support agent approves customer-facing drafts before sending.
- Manager approves refunds and policy exceptions.
- Process owner validates data minimization and retention assumptions.
- Reviewer confirms audit trail entries are sufficient for later review.

## Final Report

The final report includes:

- Executive Summary.
- Workflow Overview.
- Detected Evidence.
- Risk Matrix.
- Raw Risk.
- Recommended Controls.
- Residual Risk Simulation.
- Human Validation Plan.
- Implementation Roadmap.
- Audit Trail.
- Limitations.

## Product and Security Lessons

- AI assistance is safest when it drafts, summarizes, or classifies rather than executes.
- Human checkpoints should be tied to specific evidence and roles.
- Local-first design reduces exposure during early workflow review.
- Deterministic scoring makes the result testable and repeatable.
- Residual risk should be presented as simulation, not a guarantee.
