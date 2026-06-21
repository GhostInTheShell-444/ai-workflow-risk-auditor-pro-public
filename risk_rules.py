from __future__ import annotations

from typing import Iterable


RISK_FACTORS: dict[str, dict[str, int | str]] = {
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
    "financial_data": {
        "weight": 3,
        "description": "Financial records or payment-related data may be involved.",
    },
    "medical_health_data": {
        "weight": 4,
        "description": "Medical or health-related data may be involved.",
    },
    "legal_compliance_data": {
        "weight": 3,
        "description": "Legal, contractual, or compliance-sensitive data may be involved.",
    },
    "external_communication": {
        "weight": 2,
        "description": "The workflow may send information outside the organization.",
    },
    "customer_facing_automated_output": {
        "weight": 3,
        "description": "Automated output may be visible to customers or external users.",
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
    "sensitive_system_access": {
        "weight": 3,
        "description": "The workflow may access sensitive internal systems.",
    },
    "missing_human_validation": {
        "weight": 3,
        "description": "A high-impact workflow may not include explicit human validation.",
    },
    "missing_audit_trail": {
        "weight": 2,
        "description": "The workflow may lack an explicit audit trail or review log.",
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
    "human_validation_present": {
        "weight": 0,
        "description": "The workflow mentions human validation; this is evidence for controls rather than added risk.",
    },
    "audit_trail_present": {
        "weight": 0,
        "description": "The workflow mentions an audit trail; this is evidence for controls rather than added risk.",
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
