from analyzer import analyze_workflow
from examples import EXAMPLES, get_example_text
from ollama_client import check_ollama_status
from report_renderer import markdown_to_html, render_markdown_report


EXPECTED_ANALYSIS_KEYS = {
    "valid",
    "error",
    "workflow_summary",
    "steps",
    "workflow_type",
    "sensitive_data",
    "cybersecurity_risks",
    "privacy_risks",
    "human_checkpoints",
    "automation_opportunities",
    "risk",
    "minimal_architecture",
    "implementation_notes",
    "limitations",
}


def test_empty_input_returns_controlled_result():
    result = analyze_workflow("   ")
    assert result["valid"] is False
    assert result["error"] == "empty_input"
    assert result["risk"]["score"] == 0


def test_customer_support_workflow_detects_customer_data():
    result = analyze_workflow(get_example_text("customer_support"))
    assert result["valid"] is True
    assert result["workflow_type"] == "customer_support"
    assert "customer_data" in result["sensitive_data"]
    assert "approve_external_messages" in result["human_checkpoints"]


def test_hr_workflow_detects_candidate_data_and_human_review():
    result = analyze_workflow(get_example_text("hr_candidate_screening"))
    assert result["workflow_type"] == "hr"
    assert "hr_candidate_data" in result["sensitive_data"]
    assert "review_people_affecting_decisions" in result["human_checkpoints"]


def test_soc_workflow_detects_security_context():
    result = analyze_workflow(get_example_text("soc_alert_triage"))
    assert result["workflow_type"] == "soc"
    assert "security_event_data" in result["sensitive_data"]
    assert "soc_security_workflow" in result["risk"]["factors"]
    assert "analyst_review_security_response" in result["human_checkpoints"]


def test_logistics_workflow_detects_location_and_customer_context():
    result = analyze_workflow(get_example_text("logistics_operations"))
    assert result["workflow_type"] == "logistics"
    assert "customer_data" in result["sensitive_data"]
    assert "location_logistics_data" in result["sensitive_data"]


def test_external_communication_without_review_triggers_missing_validation():
    workflow = "AI drafts and sends customer emails automatically with account details and no review."
    result = analyze_workflow(workflow)
    assert "external_communication" in result["risk"]["factors"]
    assert "missing_human_validation" in result["risk"]["factors"]
    assert "approve_external_messages" in result["human_checkpoints"]


def test_analysis_includes_expected_structure():
    result = analyze_workflow(get_example_text("customer_support"))
    assert EXPECTED_ANALYSIS_KEYS.issubset(result.keys())
    assert {"good_candidates", "requires_approval", "poor_candidates", "guardrails"}.issubset(
        result["automation_opportunities"].keys()
    )


def test_markdown_export_contains_required_sections():
    result = analyze_workflow(get_example_text("customer_support"))
    markdown = render_markdown_report(result, language="en")
    assert "# AI Workflow Risk Audit Report" in markdown
    assert "## Workflow Summary" in markdown
    assert "## Risk Score" in markdown
    assert "## Limitations" in markdown


def test_hebrew_report_html_is_rtl():
    result = analyze_workflow(get_example_text("logistics_operations"))
    markdown = render_markdown_report(result, language="he")
    html = markdown_to_html(markdown, language="he")
    assert 'dir="rtl"' in html
    assert "סיכום התהליך" in html


def test_ollama_unavailable_fallback_is_controlled():
    status = check_ollama_status(base_url="https://example.com")
    assert status["available"] is False
    assert status["models"] == []


def test_all_example_workflows_analyze_successfully():
    for key in EXAMPLES:
        result = analyze_workflow(get_example_text(key))
        assert result["valid"] is True
        assert result["steps"]
        assert result["risk"]["score"] > 0


def test_deterministic_score_repeatability():
    text = get_example_text("soc_alert_triage")
    first = analyze_workflow(text)
    second = analyze_workflow(text)
    assert first["risk"] == second["risk"]
