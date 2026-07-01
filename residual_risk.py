from __future__ import annotations

from typing import Any

from knowledge_loader import get_control_map
from risk_rules import get_risk_level


def _control_assumption(control: dict[str, Any]) -> str:
    name = str(control.get("name", control.get("id", "Selected control")))
    return (
        f"{name} is treated as hypothetical unless a reviewer can show implementation evidence. "
        "The simulation assumes it is correctly designed, active, and used for this workflow."
    )


def _evidence_required(control: dict[str, Any]) -> str:
    category = str(control.get("category", "control")).replace("_", " ")
    guidance = str(control.get("implementation_guidance", "")).strip()
    if guidance:
        return f"Evidence should show {guidance[:180]}"
    return f"Evidence should show the {category} control exists, is assigned to an owner, and is used before production action."


def _implementation_check(control: dict[str, Any], applied_effects: dict[str, int]) -> str:
    if not applied_effects:
        return "No mapped current factor was reduced; confirm this control is relevant before relying on it."
    factors = ", ".join(sorted(applied_effects))
    return f"Check that this control directly addresses mapped factor(s): {factors}."


def _human_review_required(score: int, selected_ids: list[str]) -> bool:
    return get_risk_level(score) in {"high", "critical"} or bool(selected_ids)


def simulate_residual_risk(
    risk_matrix: dict[str, Any],
    selected_control_ids: list[str] | None = None,
    controls: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    selected_ids = selected_control_ids or []
    control_map = {str(control.get("id")): control for control in controls or []}
    fallback_map = get_control_map()
    entries = list(risk_matrix.get("entries", []))
    raw_score = int(risk_matrix.get("raw_risk_score", 0))

    residual_by_factor = {str(entry["factor"]): int(entry["score_impact"]) for entry in entries}
    applied_controls: list[dict[str, Any]] = []

    for control_id in selected_ids:
        control = control_map.get(control_id) or fallback_map.get(control_id)
        if not control:
            continue
        reductions = control.get("reduced_risk_factors", {})
        applied_effects: dict[str, int] = {}
        mapped_factors: list[str] = []
        if isinstance(reductions, dict):
            for factor, amount in reductions.items():
                mapped_factors.append(str(factor))
                if factor not in residual_by_factor:
                    continue
                reduction = max(int(amount), 0)
                before = residual_by_factor[factor]
                residual_by_factor[factor] = max(0, before - reduction)
                if before != residual_by_factor[factor]:
                    applied_effects[factor] = before - residual_by_factor[factor]
        applied_controls.append(
            {
                "id": control_id,
                "name": str(control.get("name", control_id)),
                "applied_effects": applied_effects,
                "mapped_factors": sorted(mapped_factors),
                "estimated_reduction": sum(applied_effects.values()),
                "assumption": _control_assumption(control),
                "evidence_required": _evidence_required(control),
                "implementation_check": _implementation_check(control, applied_effects),
                "limitation": "Reduction applies only to factors explicitly mapped to this control and cannot prove real-world risk reduction.",
                "not_proof_warning": "Selected controls are hypothetical in this simulation unless implementation evidence proves otherwise.",
            }
        )

    residual_score = sum(residual_by_factor.values())
    reduction = raw_score - residual_score
    remaining_risks = [
        {"factor": factor, "remaining_score": score}
        for factor, score in sorted(residual_by_factor.items())
        if score > 0
    ]

    return {
        "raw_risk": {"score": raw_score, "severity": get_risk_level(raw_score)},
        "selected_controls": applied_controls,
        "selected_hypothetical_controls": applied_controls,
        "residual_risk": {"score": residual_score, "severity": get_risk_level(residual_score)},
        "score_reduction": reduction,
        "remaining_risks": remaining_risks,
        "remaining_factors": remaining_risks,
        "human_review_required": _human_review_required(residual_score, selected_ids),
        "assumptions": [control["assumption"] for control in applied_controls],
        "limitations": [
            "Selected controls are hypothetical unless independently evidenced.",
            "Only mapped factors are reduced; unrelated factors remain unchanged.",
            "High or critical residual risk still requires responsible human review.",
            "This is not a guarantee, certification, production approval, or proof of implementation.",
        ],
        "not_proof_warning": "This simulation is not proof of implementation or assurance.",
        "not_guarantee_disclaimer": "Residual score is a local planning estimate, not a guarantee of real-world safety.",
        "explanation": (
            "Residual risk is a local simulation based on mapped control effects. "
            "Selected controls are hypothetical unless evidence proves implementation. "
            "It does not execute actions or guarantee production risk reduction."
            if selected_ids
            else "No controls selected, so residual risk equals raw risk."
        ),
    }


def default_control_selection(recommended_controls: list[dict[str, Any]], limit: int = 4) -> list[str]:
    sorted_controls = sorted(
        recommended_controls,
        key=lambda item: (int(item.get("effectiveness", 0)), str(item.get("name", ""))),
        reverse=True,
    )
    return [str(control["id"]) for control in sorted_controls[:limit]]
