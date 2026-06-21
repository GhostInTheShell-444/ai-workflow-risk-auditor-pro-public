from analyzer import analyze_workflow
from design_tokens import normalize_severity, normalize_status, severity_token, status_token
from examples import get_example_text
from ollama_client import (
    build_enrichment_prompt,
    build_synthetic_test_prompt,
    generate_local_prompt_response,
)
from ui_components import build_heatmap_cells, build_matrix_cells


def test_severity_and_status_tokens_have_accessible_text():
    critical = severity_token("critical", "en")
    assert critical["label"] == "Critical"
    assert "review" in critical["description"].casefold()
    assert normalize_severity("missing") == "unknown"

    status = status_token("needs-human-review", "en")
    assert status["label"] == "Needs human review"
    assert "human" in status["description"].casefold()
    assert normalize_status("not a status") == "uncertain"


def test_heatmap_cells_count_current_findings_and_saved_aggregates():
    findings = [
        {"category": "privacy", "severity": "high"},
        {"category": "privacy", "severity": "high"},
        {"category": "security", "severity": "medium"},
        {"category": "privacy", "severity": "critical", "count": 3},
    ]
    cells = build_heatmap_cells(findings)
    counts = {(cell["category"], cell["severity"]): cell["count"] for cell in cells}
    assert counts[("privacy", "high")] == 2
    assert counts[("privacy", "critical")] == 3
    assert counts[("security", "medium")] == 1


def test_matrix_cells_group_impact_and_likelihood():
    cells = build_matrix_cells(
        [
            {"factor": "external_communication", "impact": 4, "likelihood": 3},
            {"factor": "customer_data", "impact": 4, "likelihood": 3},
            {"factor": "missing_human_validation", "impact": 5, "likelihood": 4},
        ]
    )
    grouped = {(cell["impact"], cell["likelihood"]): cell for cell in cells}
    assert grouped[(4, 3)]["count"] == 2
    assert grouped[(5, 4)]["severity"] == "critical"


def test_local_ai_prompts_are_visible_and_do_not_claim_score_authority():
    analysis = analyze_workflow(get_example_text("customer_support"))
    prompt = build_enrichment_prompt("workflow text", analysis, "English")
    assert "Do not change the score" in prompt
    assert "deterministic score remains authoritative" in prompt
    assert "workflow text" in prompt

    synthetic = build_synthetic_test_prompt("English")
    assert "Synthetic workflow" in synthetic
    assert "not a real workflow audit" in synthetic


def test_local_prompt_generation_rejects_remote_endpoint_without_post(monkeypatch):
    def fail_post(*args, **kwargs):
        raise AssertionError("remote endpoint should not be called")

    monkeypatch.setattr("ollama_client.requests.post", fail_post)
    assert generate_local_prompt_response("prompt", base_url="https://example.com") is None
