from __future__ import annotations

from typing import Any

from knowledge_loader import get_control_map
from risk_rules import get_risk_level


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
        if isinstance(reductions, dict):
            for factor, amount in reductions.items():
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
        "residual_risk": {"score": residual_score, "severity": get_risk_level(residual_score)},
        "score_reduction": reduction,
        "remaining_risks": remaining_risks,
        "explanation": (
            "Residual risk is a local simulation based on mapped control effects. "
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
