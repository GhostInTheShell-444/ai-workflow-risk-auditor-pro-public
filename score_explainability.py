from __future__ import annotations

from typing import Any

from i18n import t, translate_category, translate_severity
from risk_rules import get_risk_level


SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1}

DISCLAIMER_BY_LANGUAGE = {
    "en": (
        "This score is a rule-based estimate, not a statistical probability. "
        "Score calculated from local deterministic rules. It is an aid, not a certification."
    ),
    "fr": (
        "Ce score est une estimation basée sur des règles locales, pas une probabilité statistique. "
        "Score calculé à partir de règles déterministes locales. C’est une aide, pas une certification."
    ),
    "he": (
        "הציון הוא הערכה לפי כללים מקומיים, לא הסתברות סטטיסטית. "
        "הציון מחושב לפי כללים דטרמיניסטיים מקומיים. זו עזרה, לא הסמכה."
    ),
}

ONE_MINUTE_BY_LANGUAGE = {
    "en": (
        "This tool reads a workflow, detects risk clues, calculates a local rule-based risk score, "
        "explains why, recommends protections, and simulates the remaining risk. It does not certify "
        "compliance and does not replace human judgment."
    ),
    "fr": (
        "Cet outil lit un workflow, détecte des indices de risque, calcule un score local basé sur "
        "des règles, explique pourquoi, recommande des protections et simule le risque restant. "
        "Il ne certifie pas la conformité et ne remplace pas le jugement humain."
    ),
    "he": (
        "הכלי קורא תהליך עבודה, מזהה סימני סיכון, מחשב ציון סיכון מקומי לפי כללים, מסביר למה, "
        "ממליץ על הגנות ומדמה את הסיכון שנותר. הוא לא מאשר ציות ולא מחליף שיקול דעת אנושי."
    ),
}

LEGEND_BY_LANGUAGE = {
    "en": {
        "Detected": "found in the text",
        "Calculated": "computed by local rules",
        "Simulated": "estimated scenario after protections",
        "Recommended": "proposed action, not an obligation",
        "Uncertain": "needs human review",
    },
    "fr": {
        "Détecté": "trouvé dans le texte",
        "Calculé": "calculé par règles locales",
        "Simulé": "scénario estimé après protections",
        "Recommandé": "action proposée, pas obligation",
        "Incertain": "à vérifier par un humain",
    },
    "he": {
        "זוהה": "נמצא בטקסט",
        "מחושב": "חושב לפי כללים מקומיים",
        "סימולציה": "תרחיש מוערך אחרי הגנות",
        "מומלץ": "פעולה מוצעת, לא חובה",
        "לא ודאי": "דורש בדיקה אנושית",
    },
}


def score_disclaimer(language: str = "en") -> str:
    return DISCLAIMER_BY_LANGUAGE.get(language, DISCLAIMER_BY_LANGUAGE["en"])


def one_minute_explanation(language: str = "en") -> str:
    return ONE_MINUTE_BY_LANGUAGE.get(language, ONE_MINUTE_BY_LANGUAGE["en"])


def simple_legend(language: str = "en") -> dict[str, str]:
    return LEGEND_BY_LANGUAGE.get(language, LEGEND_BY_LANGUAGE["en"])


def source_of_truth_labels(language: str = "en") -> list[str]:
    legend = simple_legend(language)
    return [f"{label} = {meaning}" for label, meaning in legend.items()]


def confidence_label(value: float, language: str = "en") -> str:
    if value >= 0.85:
        return t("confidence_high_label", language, "High confidence")
    if value >= 0.7:
        return t("confidence_medium_label", language, "Medium confidence")
    return t("confidence_low_label", language, "Low confidence")


def score_scale_explanation(language: str = "en") -> str:
    if language == "fr":
        return "Échelle déterministe: 0-4 faible, 5-9 moyen, 10-15 élevé, 16+ critique. Plus le score est haut, plus il faut vérifier avant d'automatiser."
    if language == "he":
        return "סולם דטרמיניסטי: 0-4 נמוך, 5-9 בינוני, 10-15 גבוה, 16+ קריטי. ככל שהציון גבוה יותר, נדרשת בדיקה חזקה יותר לפני אוטומציה."
    return "Deterministic scale: 0-4 low, 5-9 medium, 10-15 high, 16+ critical. Higher means more review is needed before automation."


def _factor_label(factor: str, language: str) -> str:
    return t(f"factor_{factor}", language, factor.replace("_", " "))


def _risk_dict(analysis: dict[str, Any]) -> dict[str, Any]:
    risk = analysis.get("risk", {})
    return risk if isinstance(risk, dict) else {}


def _matrix_dict(analysis: dict[str, Any]) -> dict[str, Any]:
    matrix = analysis.get("risk_matrix", {})
    return matrix if isinstance(matrix, dict) else {}


def _matrix_entries(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in _matrix_dict(analysis).get("entries", []) if isinstance(item, dict)]


def sorted_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        findings,
        key=lambda item: (
            SEVERITY_ORDER.get(str(item.get("severity", "low")), 0),
            float(item.get("confidence", 0)),
            len(str(item.get("matched_text_evidence", ""))),
        ),
        reverse=True,
    )


def _main_factors(analysis: dict[str, Any], language: str, limit: int = 3) -> list[dict[str, Any]]:
    entries = sorted(
        _matrix_entries(analysis),
        key=lambda item: (
            int(item.get("score_impact", 0)),
            int(item.get("evidence_count", 0)),
            float(item.get("confidence", 0)),
        ),
        reverse=True,
    )
    factors: list[dict[str, Any]] = []
    for entry in entries[:limit]:
        factor = str(entry.get("factor", ""))
        factors.append(
            {
                "factor": factor,
                "label": _factor_label(factor, language),
                "score_impact": int(entry.get("score_impact", 0)),
                "evidence_count": int(entry.get("evidence_count", 0)),
                "confidence": float(entry.get("confidence", 0)),
                "explanation": str(entry.get("description", "")),
            }
        )
    return factors


def score_label(score: int) -> str:
    return get_risk_level(score).title()


def score_summary(analysis: dict[str, Any], language: str = "en") -> dict[str, Any]:
    risk = _risk_dict(analysis)
    matrix = _matrix_dict(analysis)
    compatibility_score = int(risk.get("score", 0))
    raw_score = int(matrix.get("raw_risk_score", compatibility_score))
    level_key = str(matrix.get("severity", risk.get("level", get_risk_level(raw_score))))
    level_label = translate_severity(level_key, language)
    factors = _main_factors(analysis, language)

    if factors:
        factor_text = ", ".join(factor["label"] for factor in factors[:2])
        sentence_level = level_label.casefold() if language == "fr" else level_label
        simple = t(
            "score_simple_with_factors",
            language,
            "{level} estimated risk from local rules, mainly because {categories} were detected in the workflow text.",
        ).format(level=sentence_level, categories=factor_text)
    else:
        simple = t(
            "score_simple_without_factors",
            language,
            "Low estimated risk because no weighted risk factors were detected in the workflow text.",
        )

    return {
        "score": raw_score,
        "compatibility_score": compatibility_score,
        "level": level_key,
        "level_label": level_label,
        "simple": simple,
        "scale": score_scale_explanation(language),
        "main_factors": factors,
        "certainty": t("score_certainty_label", language, "Indicative only; not calibrated as a real-world probability."),
    }


def calculation_basis(analysis: dict[str, Any], language: str = "en") -> dict[str, Any]:
    risk = _risk_dict(analysis)
    matrix = _matrix_dict(analysis)
    entries = _matrix_entries(analysis)
    return {
        "source": t("calculation_source_local_rules", language, "local deterministic rules"),
        "compatibility_score": int(risk.get("score", 0)),
        "raw_matrix_score": int(matrix.get("raw_risk_score", risk.get("score", 0))),
        "severity_thresholds": {
            "low": "0-4",
            "medium": "5-9",
            "high": "10-15",
            "critical": "16+",
        },
        "formula": t(
            "calculation_formula",
            language,
            "Raw matrix score = sum of mapped local risk-factor weights. Residual risk = raw score minus simulated selected-control reductions.",
        ),
        "factors": [
            {
                "factor": str(entry.get("factor", "")),
                "label": _factor_label(str(entry.get("factor", "")), language),
                "weight": int(entry.get("score_impact", 0)),
                "evidence_count": int(entry.get("evidence_count", 0)),
                "confidence": float(entry.get("confidence", 0)),
            }
            for entry in entries
        ],
    }


def top_risks(analysis: dict[str, Any], language: str = "en", limit: int = 3) -> list[dict[str, Any]]:
    findings = [item for item in analysis.get("findings", []) if isinstance(item, dict)]
    risks: list[dict[str, Any]] = []
    for finding in sorted_findings(findings)[:limit]:
        severity = str(finding.get("severity", "medium"))
        category = str(finding.get("category", "general"))
        category_label = translate_category(category, language)
        severity_label = translate_severity(severity, language)
        evidence = str(finding.get("matched_text_evidence", ""))
        confidence = float(finding.get("confidence", 0))
        risks.append(
            {
                "label": t(
                    "top_risk_label_template",
                    language,
                    "{severity} {category} finding",
                ).format(severity=severity_label, category=category_label),
                "plain_language": t(
                    "top_risk_plain_template",
                    language,
                    "The workflow may be risky because the text contains evidence related to {category}. A human should check whether this finding is relevant.",
                ).format(category=category_label),
                "evidence": evidence,
                "rule": str(finding.get("matched_rule_id", "")),
                "severity": severity,
                "confidence": confidence,
                "confidence_label": confidence_label(confidence, language),
                "source_type": t("badge_detected", language, "Detected in text"),
                "calculation_type": t("top_risk_calculation_type", language, "Mapped to local risk factors"),
            }
        )
    return risks


def next_actions(analysis: dict[str, Any], language: str = "en", limit: int = 3) -> list[dict[str, Any]]:
    controls = [item for item in analysis.get("recommended_controls", []) if isinstance(item, dict)]
    actions: list[dict[str, Any]] = []
    for control in controls[:limit]:
        factors = [str(factor) for factor in control.get("risk_factors", [])]
        factor_labels = [_factor_label(factor, language) for factor in factors[:3]]
        actions.append(
            {
                "name": str(control.get("name", control.get("id", ""))),
                "why": str(control.get("reason", t("control_reason_fallback", language, "Recommended because a local risk rule matched the workflow."))),
                "risk_reduced": ", ".join(factor_labels) if factor_labels else t("mapped_risk_factors_label", language, "Mapped risk factors"),
                "required_or_advised": t("recommended_not_mandatory_label", language, "Recommended, not mandatory"),
                "expected_effect": t("control_expected_effect", language, "May reduce the simulated residual score if selected; not a guarantee."),
                "implementation": str(control.get("implementation_guidance", "")),
            }
        )
    return actions


def simulation_explanation(simulation: dict[str, Any] | None, language: str = "en") -> dict[str, Any]:
    if not simulation:
        return {
            "available": False,
            "summary": t("simulation_not_run_summary", language, "No residual-risk simulation was run. Any residual risk number would be simulated, not detected."),
            "simulated_fields": [],
        }
    raw = simulation.get("raw_risk", {})
    residual = simulation.get("residual_risk", {})
    reduction = int(simulation.get("score_reduction", 0))
    return {
        "available": True,
        "summary": t(
            "simulation_run_summary",
            language,
            "Raw risk {raw_score} becomes simulated residual risk {residual_score} after selected protections, for a simulated reduction of {reduction}. This is not a guarantee.",
        ).format(raw_score=raw.get("score", 0), residual_score=residual.get("score", 0), reduction=reduction),
        "simulated_fields": ["residual_risk.score", "residual_risk.severity", "score_reduction", "remaining_risks"],
    }


def build_explainability_payload(
    analysis: dict[str, Any],
    simulation: dict[str, Any] | None = None,
    language: str = "en",
) -> dict[str, Any]:
    matrix = _matrix_dict(analysis)
    findings = [item for item in analysis.get("findings", []) if isinstance(item, dict)]
    confidence_values = [float(item.get("confidence", 0)) for item in findings]
    average_confidence = round(sum(confidence_values) / len(confidence_values), 2) if confidence_values else 0
    score = score_summary(analysis, language)
    return {
        "one_minute_explanation": one_minute_explanation(language),
        "score_disclaimer": score_disclaimer(language),
        "score_explanation_simple": score["simple"],
        "score_scale": score["scale"],
        "score_summary": score,
        "calculation_basis": calculation_basis(analysis, language),
        "detected_evidence_count": len(findings),
        "top_risks": top_risks(analysis, language),
        "next_actions": next_actions(analysis, language),
        "confidence_label": confidence_label(average_confidence, language),
        "average_finding_confidence": average_confidence,
        "limitations": [
            t("limitation_false_positive_context", language, "Keyword and regex findings can produce false positives or miss context."),
            t("limitation_score_not_probability", language, "Scores are deterministic indicators, not measured real-world probabilities."),
            t("limitation_residual_not_assurance", language, "Residual risk is simulated planning output, not production assurance."),
            t("limitation_human_review_required", language, "A responsible human must review evidence, recommendations, and decisions."),
        ],
        "source_of_truth_labels": source_of_truth_labels(language),
        "simulation_explanation": simulation_explanation(simulation, language),
        "raw_matrix_explanation": str(
            matrix.get(
                "explanation",
                t("raw_matrix_explanation_fallback", language, "Raw risk is calculated from local rule weights mapped to detected evidence."),
            )
        ),
    }
