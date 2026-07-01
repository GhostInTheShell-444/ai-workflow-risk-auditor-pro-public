from __future__ import annotations

from typing import Iterable


RISK_FACTORS: dict[str, dict[str, int | str]] = {
    "synthetic_anonymized_data": {
        "weight": 0,
        "description": "The workflow mentions synthetic, anonymized, masked, or redacted data; this is contextual evidence rather than proof of safety.",
    },
    "personal_data": {
        "weight": 2,
        "description": "Personal data may be involved in the workflow.",
    },
    "customer_data": {
        "weight": 2,
        "description": "Customer or client data may be processed.",
    },
    "hr_candidate_data": {
        "weight": 3,
        "description": "HR, employee, or candidate data may be involved.",
    },
    "employee_data": {
        "weight": 3,
        "description": "Employee records, performance, HR operations, or internal personnel data may be involved.",
    },
    "financial_data": {
        "weight": 3,
        "description": "Financial records or payment-related data may be involved.",
    },
    "refund_payment_data": {
        "weight": 3,
        "description": "Refund, payment, billing, chargeback, or reimbursement data may be involved.",
    },
    "medical_health_data": {
        "weight": 4,
        "description": "Medical or health-related data may be involved.",
    },
    "legal_compliance_data": {
        "weight": 3,
        "description": "Legal, contractual, or compliance-sensitive data may be involved.",
    },
    "business_confidential_data": {
        "weight": 2,
        "description": "Internal confidential, source-code, pricing, roadmap, or private-document context may be involved.",
    },
    "source_code_private_documents": {
        "weight": 3,
        "description": "Source code, private documents, internal repositories, or confidential files may be involved.",
    },
    "external_communication": {
        "weight": 2,
        "description": "The workflow may send information outside the organization.",
    },
    "ai_draft_only": {
        "weight": 0,
        "description": "The workflow frames AI as drafting or summarizing only; this is contextual evidence rather than approval.",
    },
    "human_on_loop_monitoring": {
        "weight": 1,
        "description": "The workflow relies on monitoring rather than explicit approval before action.",
    },
    "automatic_external_action": {
        "weight": 4,
        "description": "The workflow may automatically perform an external action.",
    },
    "automatic_customer_communication": {
        "weight": 4,
        "description": "The workflow may automatically communicate with customers or external users.",
    },
    "customer_facing_automated_output": {
        "weight": 3,
        "description": "Automated output may be visible to customers or external users.",
    },
    "automatic_financial_decision": {
        "weight": 5,
        "description": "The workflow may automatically approve, deny, or execute a financial, refund, or billing decision.",
    },
    "automatic_account_access_decision": {
        "weight": 5,
        "description": "The workflow may automatically approve, deny, close, disable, or change account or access rights.",
    },
    "fully_autonomous_workflow": {
        "weight": 5,
        "description": "The workflow may operate end-to-end without explicit human approval.",
    },
    "emergency_fallback_behavior": {
        "weight": 1,
        "description": "Emergency or fallback behavior is mentioned and should be reviewed for safe-stop boundaries.",
    },
    "decision_affecting_person": {
        "weight": 4,
        "description": "The workflow may influence a decision affecting a person.",
    },
    "irreversible_action": {
        "weight": 4,
        "description": "The workflow may include an irreversible or high-impact action.",
    },
    "data_modification_deletion": {
        "weight": 4,
        "description": "The workflow may modify, close, or delete records.",
    },
    "third_party_integration": {
        "weight": 2,
        "description": "The workflow may depend on a third-party or external integration.",
    },
    "vendor_cloud_exposure": {
        "weight": 3,
        "description": "The workflow may expose data or decisions to a vendor, cloud, proxy, or external destination.",
    },
    "external_destination": {
        "weight": 2,
        "description": "The workflow may send data or outputs to an external destination.",
    },
    "sensitive_system_access": {
        "weight": 3,
        "description": "The workflow may access sensitive internal systems.",
    },
    "account_access_security": {
        "weight": 4,
        "description": "Account, access-control, or security entitlement decisions may be involved.",
    },
    "missing_human_validation": {
        "weight": 3,
        "description": "A high-impact workflow may not include explicit human validation.",
    },
    "missing_audit_trail": {
        "weight": 2,
        "description": "The workflow may lack an explicit audit trail or review log.",
    },
    "missing_reviewer_identity": {
        "weight": 1,
        "description": "The workflow may not identify who is responsible for review or approval.",
    },
    "missing_retention_policy": {
        "weight": 1,
        "description": "The workflow may not define how long local records or workflow data are retained.",
    },
    "missing_appeal_process": {
        "weight": 3,
        "description": "The workflow may not provide appeal, recourse, or exception handling for affected people or customers.",
    },
    "missing_monitoring": {
        "weight": 1,
        "description": "The workflow may not define monitoring for failures, drift, or inappropriate outputs.",
    },
    "missing_fallback_plan": {
        "weight": 1,
        "description": "The workflow may not define fallback, manual queue, rollback, escalation, or safe-stop behavior.",
    },
    "missing_access_control": {
        "weight": 1,
        "description": "The workflow may not define access-control or least-privilege boundaries.",
    },
    "missing_data_minimization": {
        "weight": 1,
        "description": "The workflow may not limit inputs to the minimum data required.",
    },
    "missing_data_masking": {
        "weight": 1,
        "description": "The workflow may not mention masking, redaction, or anonymization for sensitive input.",
    },
    "missing_change_management": {
        "weight": 1,
        "description": "The workflow may not describe change review before production use.",
    },
    "missing_incident_handling": {
        "weight": 1,
        "description": "The workflow may not define incident handling for incorrect or harmful automation behavior.",
    },
    "broad_ai_agent_permissions": {
        "weight": 4,
        "description": "The workflow may grant broad permissions to an AI-driven component.",
    },
    "soc_security_workflow": {
        "weight": 3,
        "description": "The workflow is related to SOC or security operations.",
    },
    "location_logistics_data": {
        "weight": 2,
        "description": "Location, routing, delivery, or logistics data may be involved.",
    },
    "credentials_secrets": {
        "weight": 4,
        "description": "Credential-like or secret-like material may be present.",
    },
    "prompt_injection_exposure": {
        "weight": 2,
        "description": "The workflow may process untrusted submitted text that could manipulate AI instructions.",
    },
    "untrusted_input": {
        "weight": 1,
        "description": "The workflow may process untrusted input from customers, vendors, emails, tickets, forms, or documents.",
    },
    "tool_action_use": {
        "weight": 3,
        "description": "The workflow may let an AI system call tools, APIs, agents, or actions.",
    },
    "hallucination_sensitive_output": {
        "weight": 2,
        "description": "The workflow may produce legal, financial, health, security, or customer-facing output where hallucination can cause harm.",
    },
    "missing_grounding": {
        "weight": 1,
        "description": "The workflow may not require source grounding, retrieved evidence, citations, or verified records.",
    },
    "confidence_score_misuse": {
        "weight": 2,
        "description": "The workflow may use confidence scores as decision authority instead of advisory context.",
    },
    "cloud_proxy_dependency": {
        "weight": 3,
        "description": "The workflow may depend on a cloud, hosted, proxy, or remote model path.",
    },
    "unknown_model_provenance": {
        "weight": 2,
        "description": "The workflow may not identify the local model source, version, or provenance.",
    },
    "model_decision_authority": {
        "weight": 4,
        "description": "The workflow may give the model authority to make or finalize decisions.",
    },
    "opaque_decision_logic": {
        "weight": 2,
        "description": "The workflow may not explain why an automated recommendation or decision was produced.",
    },
    "human_validation_present": {
        "weight": 0,
        "description": "The workflow mentions human validation; this is evidence for controls rather than added risk.",
    },
    "audit_trail_present": {
        "weight": 0,
        "description": "The workflow mentions an audit trail; this is evidence for controls rather than added risk.",
    },
    "fallback_present": {
        "weight": 0,
        "description": "The workflow mentions fallback, rollback, manual queue, or safe-stop behavior; this is evidence for review rather than proof of implementation.",
    },
    "local_ai_only_present": {
        "weight": 0,
        "description": "The workflow mentions local-only AI, Ollama, or no-cloud operation; this is contextual evidence rather than proof of implementation.",
    },
}


def normalize_factors(factors: Iterable[str]) -> list[str]:
    requested = {str(factor).strip().lower() for factor in factors}
    return [key for key in RISK_FACTORS if key in requested]


def calculate_score(factors: Iterable[str]) -> int:
    return sum(int(RISK_FACTORS[key]["weight"]) for key in normalize_factors(factors))


def get_risk_level(score: int) -> str:
    if score <= 4:
        return "low"
    if score <= 9:
        return "medium"
    if score <= 15:
        return "high"
    return "critical"


def get_factor_breakdown(factors: Iterable[str]) -> list[dict[str, int | str]]:
    breakdown: list[dict[str, int | str]] = []
    for key in normalize_factors(factors):
        definition = RISK_FACTORS[key]
        breakdown.append(
            {
                "key": key,
                "weight": int(definition["weight"]),
                "description": str(definition["description"]),
            }
        )
    return breakdown


def explain_score(factors: Iterable[str]) -> str:
    normalized = normalize_factors(factors)
    if not normalized:
        return "No weighted risk factors were detected."
    factor_list = ", ".join(normalized)
    return f"Score is based on these triggered factors: {factor_list}."


def calculate_risk(factors: Iterable[str]) -> dict[str, object]:
    normalized = normalize_factors(factors)
    score = calculate_score(normalized)
    return {
        "score": score,
        "level": get_risk_level(score),
        "factors": normalized,
        "breakdown": get_factor_breakdown(normalized),
        "explanation": explain_score(normalized),
    }
