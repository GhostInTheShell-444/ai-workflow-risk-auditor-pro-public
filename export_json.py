from __future__ import annotations

import json
from typing import Any

from score_explainability import build_explainability_payload


def build_json_summary(
    analysis: dict[str, Any],
    simulation: dict[str, Any] | None = None,
    report_id: int | None = None,
    language: str = "en",
) -> dict[str, Any]:
    risk = analysis.get("risk", {})
    explainability = build_explainability_payload(analysis, simulation, language)
    return {
        "product": "AI Workflow Risk Auditor Pro",
        "report_id": report_id,
        "workflow_type": analysis.get("workflow_type"),
        "valid": bool(analysis.get("valid")),
        "risk": risk,
        "risk_matrix": analysis.get("risk_matrix", {}),
        "finding_count": len(analysis.get("findings", [])),
        "findings": analysis.get("findings", []),
        "recommended_controls": analysis.get("recommended_controls", []),
        "human_validation_plan": analysis.get("human_validation_plan", []),
        "simulation": simulation,
        "score_explanation_simple": explainability["score_explanation_simple"],
        "calculation_basis": explainability["calculation_basis"],
        "detected_evidence_count": explainability["detected_evidence_count"],
        "simulated_fields": explainability["simulation_explanation"]["simulated_fields"],
        "confidence_label": explainability["confidence_label"],
        "limitations": explainability["limitations"],
        "next_actions": explainability["next_actions"],
        "source_of_truth_labels": explainability["source_of_truth_labels"],
        "one_minute_explanation": explainability["one_minute_explanation"],
        "score_disclaimer": explainability["score_disclaimer"],
        "explainability": explainability,
        "privacy_model": {
            "local_first": True,
            "cloud_api_required": False,
            "auto_persist_user_input": False,
            "explicit_save_required": True,
            "workflow_text_never_sent_to_cloud_by_app": True,
            "ollama_optional_localhost_only": True,
        },
    }


def render_json_summary(
    analysis: dict[str, Any],
    simulation: dict[str, Any] | None = None,
    report_id: int | None = None,
    language: str = "en",
) -> str:
    return json.dumps(build_json_summary(analysis, simulation, report_id, language), indent=2, ensure_ascii=False)
