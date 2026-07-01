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


def test_automatic_refund_without_review_is_higher_than_reviewed_drafting():
    automatic = analyze_workflow(
        "AI automatically approves and issues customer refunds from billing data without human review, "
        "appeal, audit logs, masking, or fallback."
    )
    reviewed = analyze_workflow(
        "AI drafts a customer support reply from anonymized ticket notes. A named human reviewer approves "
        "before sending. Audit log, retention policy, data minimization, redaction, monitoring, and manual "
        "fallback are documented."
    )
    assert automatic["risk"]["score"] > reviewed["risk"]["score"]
    assert automatic["risk"]["level"] == "critical"
    assert "automatic_financial_decision" in automatic["risk"]["factors"]
    assert "missing_human_validation" in automatic["risk"]["factors"]
    assert "ai_draft_only" in reviewed["risk"]["factors"]
    assert "missing_human_validation" not in reviewed["risk"]["factors"]


def test_sensitive_customer_data_without_masking_or_retention_creates_gaps():
    result = analyze_workflow("AI summarizes customer data and email addresses for support.")
    assert "missing_data_masking" in result["risk"]["factors"]
    assert "missing_retention_policy" in result["risk"]["factors"]
    assert any(finding["matched_rule_id"] == "gap_missing_data_masking" for finding in result["findings"])
    assert any(finding["matched_rule_id"] == "gap_missing_retention_policy" for finding in result["findings"])


def test_decision_workflow_without_appeal_creates_recourse_gap():
    result = analyze_workflow("AI ranks candidates and rejects low-scoring applicants after automatic screening.")
    assert "missing_appeal_process" in result["risk"]["factors"]
    assert any(finding["matched_rule_id"] == "gap_missing_appeal_process" for finding in result["findings"])


def test_logs_and_fallback_are_contextual_controls_not_proof_of_safety():
    result = analyze_workflow(
        "AI proposes an account access change. A human approves it. The workflow keeps an audit log and "
        "uses a manual fallback queue with failure logging."
    )
    assert "audit_trail_present" in {
        factor for finding in result["findings"] for factor in finding["risk_factor_mapping"]
    }
    assert "fallback_present" in result["risk"]["factors"]
    assert "missing_audit_trail" not in result["risk"]["factors"]
    assert "missing_fallback_plan" not in result["risk"]["factors"]


def test_local_only_ollama_wording_does_not_create_cloud_dependency():
    result = analyze_workflow(
        "Ollama runs as local-only AI on localhost with no cloud fallback. It drafts an internal summary "
        "for human review."
    )
    assert "local_ai_only_present" in result["risk"]["factors"]
    assert "cloud_proxy_dependency" not in result["risk"]["factors"]
    assert "third_party_integration" not in result["risk"]["factors"]


def test_explicit_controls_reduce_gap_score_but_not_human_responsibility():
    uncontrolled = analyze_workflow(
        "AI automatically sends customer refund decisions from customer billing data without human review."
    )
    controlled = analyze_workflow(
        "AI drafts a refund recommendation from redacted minimum-necessary customer billing data. "
        "A named finance reviewer approves it, records an audit log, applies a retention policy, offers appeal, "
        "monitors outcomes, and routes failures to a manual fallback queue."
    )
    assert controlled["risk"]["score"] < uncontrolled["risk"]["score"]
    assert controlled["human_validation_plan"]


def test_evidence_chain_preserves_source_vs_hypothesis_provenance():
    result = analyze_workflow("AI automatically approves customer refunds from billing data.")
    inferred = [item for item in result["evidence_chain"] if item["is_hypothesis"]]
    sourced = [item for item in result["evidence_chain"] if not item["is_hypothesis"]]
    assert inferred
    assert all(item["evidence_type"] == "inferred_gap" for item in inferred)
    assert all(item["source_excerpt"] is None for item in inferred)
    assert all(item["inference_basis"] for item in inferred)
    assert sourced
    assert all(item["evidence_type"] == "source_excerpt" for item in sourced)
    assert all(item["source_excerpt"] for item in sourced)
