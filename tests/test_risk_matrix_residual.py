from analyzer import analyze_workflow
from controls_engine import recommend_controls
from examples import get_example_text
from human_validation import build_human_validation_plan
from residual_risk import default_control_selection, simulate_residual_risk
from risk_matrix import calculate_risk_matrix


def test_risk_matrix_contains_required_attributes():
    analysis = analyze_workflow(get_example_text("customer_support"))
    matrix = analysis["risk_matrix"]
    for key in ["likelihood", "impact", "confidence", "raw_risk_score", "severity", "explanation", "entries"]:
        assert key in matrix
    assert matrix["raw_risk_score"] >= analysis["risk"]["score"]


def test_risk_matrix_is_deterministic():
    first = analyze_workflow(get_example_text("soc_alert_triage"))["risk_matrix"]
    second = analyze_workflow(get_example_text("soc_alert_triage"))["risk_matrix"]
    assert first == second


def test_control_recommendation_mapping_uses_findings():
    analysis = analyze_workflow(get_example_text("hr_candidate_screening"))
    controls = recommend_controls(analysis["findings"])
    assert controls
    assert any(control["id"] == "ctrl_hr_recruiter_review" for control in controls)


def test_residual_risk_without_controls_keeps_raw_score():
    analysis = analyze_workflow(get_example_text("customer_support"))
    simulation = simulate_residual_risk(analysis["risk_matrix"], [], analysis["recommended_controls"])
    assert simulation["raw_risk"]["score"] == simulation["residual_risk"]["score"]
    assert simulation["score_reduction"] == 0


def test_residual_risk_with_controls_reduces_or_preserves_score():
    analysis = analyze_workflow(get_example_text("customer_support"))
    selected = default_control_selection(analysis["recommended_controls"])
    simulation = simulate_residual_risk(analysis["risk_matrix"], selected, analysis["recommended_controls"])
    assert simulation["residual_risk"]["score"] <= simulation["raw_risk"]["score"]
    assert simulation["score_reduction"] >= 0


def test_default_control_selection_is_bounded():
    analysis = analyze_workflow(get_example_text("logistics_operations"))
    selected = default_control_selection(analysis["recommended_controls"], limit=3)
    assert 0 < len(selected) <= 3


def test_human_validation_plan_has_required_fields():
    analysis = analyze_workflow(get_example_text("soc_alert_triage"))
    plan = build_human_validation_plan(analysis["findings"], analysis["recommended_controls"])
    checkpoint = plan[0]
    for key in [
        "checkpoint_id",
        "responsible_role",
        "validation_moment",
        "reason",
        "linked_evidence",
        "linked_control",
        "impact_if_omitted",
    ]:
        assert key in checkpoint


def test_simulation_explanation_is_local_and_non_executing():
    analysis = analyze_workflow(get_example_text("soc_alert_triage"))
    selected = default_control_selection(analysis["recommended_controls"])
    simulation = simulate_residual_risk(analysis["risk_matrix"], selected, analysis["recommended_controls"])
    explanation = simulation["explanation"].casefold()
    assert "local simulation" in explanation
    assert "does not execute" in explanation


def test_calculate_risk_matrix_accepts_compatibility_factors():
    matrix = calculate_risk_matrix([], ["personal_data", "customer_data"])
    assert matrix["raw_risk_score"] == 4
    assert len(matrix["entries"]) == 2


def test_v1_risk_score_remains_repeatable_with_new_fields():
    first = analyze_workflow(get_example_text("customer_support"))
    second = analyze_workflow(get_example_text("customer_support"))
    assert first["risk"] == second["risk"]
    assert first["risk_matrix"] == second["risk_matrix"]
