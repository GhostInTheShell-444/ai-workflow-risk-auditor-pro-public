from __future__ import annotations

from typing import Any

from knowledge_loader import get_control_map


def recommend_controls(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    controls_by_id = get_control_map()
    reasons: dict[str, list[str]] = {}
    factors_by_control: dict[str, set[str]] = {}

    for finding in findings:
        for control_id in finding.get("recommended_controls", []):
            if control_id not in controls_by_id:
                continue
            reasons.setdefault(control_id, []).append(str(finding.get("matched_rule_id", "")))
            factors_by_control.setdefault(control_id, set()).update(
                str(factor) for factor in finding.get("risk_factor_mapping", [])
            )

    recommended: list[dict[str, Any]] = []
    for control_id in sorted(reasons):
        control = controls_by_id[control_id]
        recommended.append(
            {
                "id": control_id,
                "name": str(control["name"]),
                "category": str(control["category"]),
                "effectiveness": int(control.get("effectiveness", 0)),
                "description": str(control.get("description", "")),
                "implementation_guidance": str(control.get("implementation_guidance", "")),
                "human_role_if_relevant": str(control.get("human_role_if_relevant", "")),
                "reduced_risk_factors": dict(control.get("reduced_risk_factors", {})),
                "reason": "Triggered by rule(s): " + ", ".join(sorted(set(reasons[control_id]))[:5]),
                "risk_factors": sorted(factors_by_control.get(control_id, set())),
            }
        )
    return recommended


def controls_for_export(controls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": str(control.get("id")),
            "name": str(control.get("name")),
            "category": str(control.get("category")),
            "effectiveness": int(control.get("effectiveness", 0)),
            "risk_factors": list(control.get("risk_factors", [])),
        }
        for control in controls
    ]
