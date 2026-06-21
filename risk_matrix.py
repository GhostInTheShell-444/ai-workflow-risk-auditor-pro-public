from __future__ import annotations

from statistics import mean
from typing import Any

from risk_rules import RISK_FACTORS, calculate_score, get_risk_level, normalize_factors


def _impact_from_weight(weight: int) -> int:
    if weight >= 4:
        return 5
    if weight == 3:
        return 4
    if weight == 2:
        return 3
    return 2


def _likelihood_from_count(count: int) -> int:
    return min(5, max(1, count + 1))


def calculate_risk_matrix(
    findings: list[dict[str, Any]],
    compatibility_factors: list[str] | None = None,
) -> dict[str, Any]:
    factor_counts: dict[str, int] = {}
    confidence_values: dict[str, list[float]] = {}

    for finding in findings:
        confidence = float(finding.get("confidence", 0.7))
        for factor in finding.get("risk_factor_mapping", []):
            if factor not in RISK_FACTORS:
                continue
            factor_counts[factor] = factor_counts.get(factor, 0) + 1
            confidence_values.setdefault(factor, []).append(confidence)

    for factor in normalize_factors(compatibility_factors or []):
        factor_counts.setdefault(factor, 1)
        confidence_values.setdefault(factor, [0.78])

    ordered_factors = normalize_factors(factor_counts.keys())
    raw_score = calculate_score(ordered_factors)
    entries: list[dict[str, Any]] = []

    for factor in ordered_factors:
        definition = RISK_FACTORS[factor]
        weight = int(definition["weight"])
        if weight <= 0:
            continue
        count = factor_counts[factor]
        confidence = round(mean(confidence_values.get(factor, [0.7])), 2)
        entries.append(
            {
                "factor": factor,
                "description": str(definition["description"]),
                "likelihood": _likelihood_from_count(count),
                "impact": _impact_from_weight(weight),
                "confidence": confidence,
                "score_impact": weight,
                "evidence_count": count,
            }
        )

    level = get_risk_level(raw_score)
    return {
        "likelihood": round(mean([entry["likelihood"] for entry in entries]), 2) if entries else 0,
        "impact": round(mean([entry["impact"] for entry in entries]), 2) if entries else 0,
        "confidence": round(mean([entry["confidence"] for entry in entries]), 2) if entries else 0,
        "raw_risk_score": raw_score,
        "severity": level,
        "explanation": (
            "Raw risk is the deterministic sum of mapped factor weights. "
            "Likelihood and impact are explainable matrix attributes derived from evidence counts and factor weights."
        ),
        "mapped_controls": [],
        "entries": entries,
    }
