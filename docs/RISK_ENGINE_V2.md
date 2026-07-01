# Risk Engine v2

## Purpose

Risk Engine v2 is a local deterministic review-priority engine. It is designed to make workflow risks inspectable and reproducible without claiming probability, certification, legal authority, or production approval.

## Detection dimensions

- Data sensitivity: synthetic/anonymized, personal, customer, employee, candidate, financial, refund/payment, health, legal/compliance, confidential, credentials, source code, and private documents.
- Automation autonomy: draft-only, human review, monitoring, automatic communication/action, financial decisions, account/access decisions, full autonomy, and fallback behavior.
- Impact areas: customer communication, finance, access/security, legal, HR, health, operations, internal productivity, and vendor/cloud exposure.
- Governance controls: approval, escalation, audit trail, reviewer identity, retention, appeal, monitoring, rollback/fallback, access control, minimization, masking, change management, and incident handling.
- AI-specific risk: prompt injection, untrusted input, tool/action use, hallucination-sensitive output, grounding, confidence misuse, cloud/proxy dependency, model provenance, model authority, external destination, and opaque logic.

## Finding contract

Each runtime finding exposes:

- evidence;
- rule id;
- category;
- severity;
- confidence heuristic;
- score impact;
- why it matters;
- recommended control text and mapped control IDs;
- human review question;
- residual-simulation assumption;
- limitation.

Direct findings come from local rules. Gap findings are generated when the submitted description indicates sensitive or high-impact context but omits expected control wording. A gap finding means “not evidenced in this text,” not “proven absent in production.”

## Scoring

`risk_rules.py` contains fixed factor weights. `risk_matrix.py` sums each normalized factor once. Severity thresholds remain:

- 0–4: Low
- 5–9: Medium
- 10–15: High
- 16+: Critical

Strong weights are reserved for automatic financial decisions, automatic account/access decisions, full autonomy, irreversible actions, model decision authority, and sensitive health or credential contexts. Governance gaps remain visible but use lower individual weights to reduce double counting.

## Control evidence

Positive wording such as audit logs, fallback queues, redaction, or local-only Ollama is contextual evidence. It prevents some missing-control factors but does not subtract risk directly or prove implementation.

Negated wording such as “without fallback” is treated as missing control evidence, not a positive control.

## Local knowledge files

- `knowledge_base/risk_factors_v2.json`
- `knowledge_base/control_effects_v2.json`
- `knowledge_base/framework_mappings_v2.json`
- `knowledge_base/review_questions_v2.json`

Framework mappings are framework-inspired review categories only. They do not establish compliance, conformity, or certification.

## Human responsibility

High-impact and High/Critical workflows require qualified human review. The engine cannot know full business context, contractual duties, jurisdiction, control effectiveness, deployment architecture, or real operating evidence.
