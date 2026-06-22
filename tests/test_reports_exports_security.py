from analyzer import analyze_workflow
from examples import get_example_text
from export_json import build_json_summary, render_json_summary
from ollama_client import (
    check_ollama_status,
    generate_enrichment,
    generate_local_prompt_response,
    is_cloud_or_proxy_model,
)
from report_renderer import markdown_to_html, render_markdown_report
from residual_risk import default_control_selection, simulate_residual_risk


def test_enhanced_markdown_report_contains_required_sections():
    analysis = analyze_workflow(get_example_text("customer_support"))
    simulation = simulate_residual_risk(
        analysis["risk_matrix"],
        default_control_selection(analysis["recommended_controls"]),
        analysis["recommended_controls"],
    )
    markdown = render_markdown_report(analysis, simulation=simulation)
    for section in [
        "## Executive Summary",
        "## Workflow Overview",
        "## Detected Evidence",
        "## Risk Matrix",
        "## Raw Risk",
        "## Recommended Controls",
        "## Residual Risk Simulation",
        "## Human Validation Plan",
        "## Implementation Roadmap",
        "## Audit Trail",
        "## Limitations",
    ]:
        assert section in markdown


def test_local_enrichment_does_not_replace_deterministic_summary():
    analysis = analyze_workflow(get_example_text("customer_support"))
    markdown = render_markdown_report(analysis, enrichment="Model wording only.")
    assert "Deterministic local audit result" in markdown
    assert "## Local Narrative Enrichment" in markdown
    assert "Model wording only." in markdown


def test_json_summary_export_contains_privacy_model():
    analysis = analyze_workflow(get_example_text("hr_candidate_screening"))
    summary = build_json_summary(analysis)
    assert summary["privacy_model"]["local_first"] is True
    assert summary["privacy_model"]["cloud_api_required"] is False
    assert summary["privacy_model"]["auto_persist_user_input"] is False


def test_json_summary_renders_valid_json_text():
    analysis = analyze_workflow(get_example_text("soc_alert_triage"))
    rendered = render_json_summary(analysis)
    assert '"AI Workflow Risk Auditor Pro"' in rendered
    assert '"findings"' in rendered


def test_hebrew_markdown_html_preserves_rtl():
    analysis = analyze_workflow(get_example_text("logistics_operations"))
    html = markdown_to_html(render_markdown_report(analysis, language="he"), language="he")
    assert 'dir="rtl"' in html
    assert "סיכום התהליך" in html


def test_french_and_hebrew_reports_localize_main_sections():
    analysis = analyze_workflow(get_example_text("customer_support"))
    french = render_markdown_report(analysis, language="fr")
    hebrew = render_markdown_report(analysis, language="he")
    assert "## Synthèse exécutive" in french
    assert "## Preuves détectées" in french
    assert "## תקציר מנהלים" in hebrew
    assert "## ראיות שזוהו" in hebrew


def test_non_local_ollama_status_does_not_call_requests(monkeypatch):
    def fail_get(*args, **kwargs):
        raise AssertionError("external request should not be attempted")

    monkeypatch.setattr("ollama_client.requests.get", fail_get)
    status = check_ollama_status(base_url="https://example.com")
    assert status["available"] is False


def test_ollama_status_separates_local_and_cloud_models(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "models": [
                    {"name": "gemma3:cloud", "remote_host": "https://ollama.com:443"},
                    {"name": "qwen3:8b", "details": {"format": "gguf"}},
                ]
            }

    monkeypatch.setattr("ollama_client.requests.get", lambda *args, **kwargs: Response())
    status = check_ollama_status()
    assert status["available"] is True
    assert status["models"] == ["qwen3:8b"]
    assert status["cloud_models"] == ["gemma3:cloud"]


def test_ollama_status_disables_redirects_and_environment_proxies(monkeypatch):
    observed = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"models": []}

    def fake_get(*args, **kwargs):
        observed.update(kwargs)
        return Response()

    monkeypatch.setattr("ollama_client.requests.get", fake_get)
    assert check_ollama_status()["available"] is True
    assert observed["allow_redirects"] is False
    assert observed["proxies"] == {"http": None, "https": None, "all": None}


def test_ollama_generation_disables_redirects_and_environment_proxies(monkeypatch):
    observed = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": "Local synthetic response."}

    monkeypatch.setattr(
        "ollama_client.check_ollama_status",
        lambda **kwargs: {"available": True, "models": ["llama3"]},
    )

    def fake_post(*args, **kwargs):
        observed.update(kwargs)
        return Response()

    monkeypatch.setattr("ollama_client.requests.post", fake_post)
    assert generate_local_prompt_response("Synthetic prompt.") == "Local synthetic response."
    assert observed["allow_redirects"] is False
    assert observed["proxies"] == {"http": None, "https": None, "all": None}


def test_cloud_ollama_model_names_are_rejected():
    assert is_cloud_or_proxy_model("gemma3:cloud") is True
    assert is_cloud_or_proxy_model("gpt-oss:20b-cloud") is True
    assert is_cloud_or_proxy_model("qwen3:8b") is False


def test_generate_enrichment_rejects_non_local_endpoint(monkeypatch):
    def fail_post(*args, **kwargs):
        raise AssertionError("external request should not be attempted")

    monkeypatch.setattr("ollama_client.requests.post", fail_post)
    analysis = analyze_workflow(get_example_text("customer_support"))
    assert generate_enrichment("workflow", analysis, "English", base_url="https://example.com") is None


def test_generate_enrichment_rejects_cloud_model_without_post(monkeypatch):
    def fail_post(*args, **kwargs):
        raise AssertionError("cloud/proxy model should not be posted to")

    monkeypatch.setattr("ollama_client.requests.post", fail_post)
    analysis = analyze_workflow(get_example_text("customer_support"))
    assert generate_enrichment("workflow", analysis, "English", model="gemma3:cloud") is None


def test_generate_enrichment_rejects_model_not_listed_locally(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"models": [{"name": "qwen3:8b", "details": {"format": "gguf"}}]}

    def fail_post(*args, **kwargs):
        raise AssertionError("missing model should not be posted to")

    monkeypatch.setattr("ollama_client.requests.get", lambda *args, **kwargs: Response())
    monkeypatch.setattr("ollama_client.requests.post", fail_post)
    analysis = analyze_workflow(get_example_text("customer_support"))
    assert generate_enrichment("workflow", analysis, "English", model="llama3") is None


def test_requirements_do_not_add_cloud_sdk_dependencies():
    with open("requirements.txt", encoding="utf-8") as handle:
        requirements = handle.read().casefold()
    for forbidden in ["openai", "boto3", "google-cloud", "azure"]:
        assert forbidden not in requirements


def test_report_states_persistence_is_explicit():
    analysis = analyze_workflow(get_example_text("customer_support"))
    markdown = render_markdown_report(analysis)
    assert "Persistence occurs only after explicit save actions" in markdown


def test_explainability_markdown_explains_score_and_limits():
    analysis = analyze_workflow(get_example_text("customer_support"))
    simulation = simulate_residual_risk(
        analysis["risk_matrix"],
        default_control_selection(analysis["recommended_controls"]),
        analysis["recommended_controls"],
    )
    markdown = render_markdown_report(analysis, simulation=simulation)
    lowered = markdown.casefold()
    for concept in [
        "what this score means",
        "rule-based estimate",
        "not a certification",
        "detected = found in the text",
        "calculated = computed by local rules",
        "simulated = estimated scenario after protections",
        "recommended = proposed action",
        "human",
        "local",
    ]:
        assert concept in lowered


def test_explainability_json_contains_explainability_fields():
    analysis = analyze_workflow(get_example_text("hr_candidate_screening"))
    simulation = simulate_residual_risk(
        analysis["risk_matrix"],
        default_control_selection(analysis["recommended_controls"]),
        analysis["recommended_controls"],
    )
    summary = build_json_summary(analysis, simulation)
    for key in [
        "score_explanation_simple",
        "calculation_basis",
        "detected_evidence_count",
        "simulated_fields",
        "confidence_label",
        "limitations",
        "next_actions",
        "source_of_truth_labels",
    ]:
        assert key in summary
    assert "rule-based estimate" in summary["score_disclaimer"]
    assert summary["privacy_model"]["workflow_text_never_sent_to_cloud_by_app"] is True
    assert summary["simulated_fields"]
