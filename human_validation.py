from __future__ import annotations

import hashlib
from typing import Any


ROLE_RULES = (
    ("soc", "SOC analyst", "before security escalation or incident response recommendation"),
    ("hr", "HR recruiter", "before candidate ranking, interview, rejection, or shortlist use"),
    ("logistics", "Dispatcher", "before route changes or customer delivery notification"),
    ("finance", "Finance approver", "before payment, refund, invoice, or account update"),
    ("legal", "Legal or compliance reviewer", "before legal or compliance-sensitive response"),
    ("medical", "Qualified specialist", "before health-related recommendation is used"),
    ("external", "Support agent or business owner", "before external message is sent"),
)


def _checkpoint_id(role: str, evidence: str) -> str:
    digest = hashlib.sha1(f"{role}|{evidence}".encode("utf-8")).hexdigest()[:10]
    return f"checkpoint_{digest}"


def _role_for_finding(finding: dict[str, Any]) -> tuple[str, str]:
    category = str(finding.get("category", "")).casefold()
    factors = {str(item).casefold() for item in finding.get("risk_factor_mapping", [])}
    if category == "security" or "soc_security_workflow" in factors:
        return "SOC analyst", "before security escalation or incident response recommendation"
    if category == "hr" or "hr_candidate_data" in factors:
        return "HR recruiter", "before candidate ranking, interview, rejection, or shortlist use"
    if category == "logistics" or "location_logistics_data" in factors:
        return "Dispatcher", "before route changes or customer delivery notification"
    if category == "finance" or "financial_data" in factors:
        return "Finance approver", "before payment, refund, invoice, or account update"
    if category == "legal" or "legal_compliance_data" in factors:
        return "Legal or compliance reviewer", "before legal or compliance-sensitive response"
    if category == "medical" or "medical_health_data" in factors:
        return "Qualified specialist", "before health-related recommendation is used"
    if category == "external" or "external_communication" in factors:
        return "Support agent or business owner", "before external message is sent"
    if "decision_affecting_person" in factors:
        return "Responsible manager", "before people-affecting recommendation is used"
    return "Process owner", "before high-impact recommendation leaves advisory review"


def build_human_validation_plan(
    findings: list[dict[str, Any]],
    recommended_controls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    control_by_factor: dict[str, str] = {}
    for control in recommended_controls:
        for factor in control.get("risk_factors", []):
            control_by_factor.setdefault(str(factor), str(control.get("id", "")))

    checkpoints: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for finding in findings:
        factors = [str(item) for item in finding.get("risk_factor_mapping", [])]
        if not factors:
            continue
        role, moment = _role_for_finding(finding)
        evidence = str(finding.get("matched_text_evidence", ""))[:160]
        key = (role, evidence)
        if key in seen:
            continue
        seen.add(key)
        linked_control = next((control_by_factor.get(factor) for factor in factors if control_by_factor.get(factor)), "")
        checkpoints.append(
            {
                "checkpoint_id": _checkpoint_id(role, evidence),
                "responsible_role": role,
                "validation_moment": moment,
                "reason": str(finding.get("explanation", "Review required for detected workflow risk.")),
                "linked_evidence": evidence,
                "linked_control": linked_control,
                "impact_if_omitted": "The workflow may move from advisory support to unreviewed external, sensitive, or high-impact action.",
            }
        )
    return checkpoints[:12]
