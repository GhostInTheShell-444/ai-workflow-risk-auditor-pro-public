from analyzer import analyze_workflow
from examples import get_example_text
from export_json import build_json_summary, render_json_summary
from ollama_client import (
    build_enrichment_prompt,
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
    assert summary["privacy_model"]["ai_provider_default"] == "disabled"
    assert summary["privacy_model"]["ai_provider_runtime"] == "ollama_loopback_only"
    assert summary["privacy_model"]["ai_provider_output_role"] == "advisory_only"
    assert summary["privacy_model"]["cloud_fallback"] is False
    assert summary["privacy_model"]["api_keys_stored"] is False


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
    def fail_request(*args, **kwargs):
        raise AssertionError("external request should not be attempted")

    monkeypatch.setattr("ollama_client._direct_request", fail_request)
    status = check_ollama_status(base_url="https://example.com")
    assert status["available"] is False


def test_ollama_status_accepts_only_explicit_loopback_hosts(monkeypatch):
    observed_urls = []

    class Response:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {"models": []}

    def fake_request(method, url, **kwargs):
        observed_urls.append(url)
        return Response()

    monkeypatch.setattr("ollama_client._direct_request", fake_request)
    for base_url in [
        "http://localhost:11434",
        "http://127.0.0.1:11434",
        "http://[::1]:11434",
    ]:
        assert check_ollama_status(base_url=base_url)["available"] is True

    assert len(observed_urls) == 3


def test_ollama_status_rejects_loopback_lookalikes_before_request(monkeypatch):
    def fail_request(*args, **kwargs):
        raise AssertionError("non-loopback endpoint should not be called")

    monkeypatch.setattr("ollama_client._direct_request", fail_request)
    for base_url in [
        "http://localhost.example.com:11434",
        "http://127.0.0.2:11434",
        "http://0.0.0.0:11434",
        "https://example.com",
    ]:
        assert check_ollama_status(base_url=base_url)["available"] is False


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

    monkeypatch.setattr("ollama_client._direct_request", lambda *args, **kwargs: Response())
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

    class Session:
        trust_env = True

        def request(self, method, url, **kwargs):
            observed.update({"method": method, "url": url, "trust_env": self.trust_env, **kwargs})
            return Response()

        def close(self):
            observed["closed"] = True

    monkeypatch.setattr("ollama_client.requests.Session", Session)
    assert check_ollama_status()["available"] is True
    assert observed["method"] == "GET"
    assert observed["trust_env"] is False
    assert observed["allow_redirects"] is False
    assert observed["closed"] is True


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

    def fake_request(method, url, **kwargs):
        observed.update({"method": method, "url": url, **kwargs})
        return Response()

    monkeypatch.setattr("ollama_client._direct_request", fake_request)
    assert generate_local_prompt_response("Synthetic prompt.") == "Local synthetic response."
    assert observed["method"] == "POST"
    assert observed["allow_redirects"] is False


def test_ollama_status_rejects_redirect_response(monkeypatch):
    class Response:
        status_code = 302

        def raise_for_status(self):
            return None

        def json(self):
            raise AssertionError("redirect body should not be accepted")

    monkeypatch.setattr("ollama_client._direct_request", lambda *args, **kwargs: Response())
    status = check_ollama_status()
    assert status["available"] is False
    assert status["message"] == "Local model service redirect rejected."


def test_ollama_generation_rejects_redirect_response(monkeypatch):
    class Response:
        status_code = 307

        def raise_for_status(self):
            return None

        def json(self):
            raise AssertionError("redirect body should not be accepted")

    monkeypatch.setattr(
        "ollama_client.check_ollama_status",
        lambda **kwargs: {"available": True, "models": ["llama3"]},
    )
    monkeypatch.setattr("ollama_client._direct_request", lambda *args, **kwargs: Response())
    assert generate_local_prompt_response("Synthetic prompt.") is None


def test_cloud_ollama_model_names_are_rejected():
    assert is_cloud_or_proxy_model("gemma3:cloud") is True
    assert is_cloud_or_proxy_model("gpt-oss:20b-cloud") is True
    assert is_cloud_or_proxy_model("qwen3:8b") is False


def test_generate_enrichment_rejects_non_local_endpoint(monkeypatch):
    def fail_request(*args, **kwargs):
        raise AssertionError("external request should not be attempted")

    monkeypatch.setattr("ollama_client._direct_request", fail_request)
    analysis = analyze_workflow(get_example_text("customer_support"))
    assert generate_enrichment("workflow", analysis, "English", base_url="https://example.com") is None


def test_generate_enrichment_rejects_cloud_model_without_post(monkeypatch):
    def fail_request(*args, **kwargs):
        raise AssertionError("cloud/proxy model should not be posted to")

    monkeypatch.setattr("ollama_client._direct_request", fail_request)
    analysis = analyze_workflow(get_example_text("customer_support"))
    assert generate_enrichment("workflow", analysis, "English", model="gemma3:cloud") is None


def test_generate_enrichment_rejects_model_not_listed_locally(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"models": [{"name": "qwen3:8b", "details": {"format": "gguf"}}]}

    monkeypatch.setattr("ollama_client._direct_request", lambda *args, **kwargs: Response())
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


def test_local_ai_prompt_is_bounded_reviewer_assistance():
    analysis = analyze_workflow(get_example_text("customer_support"))
    prompt = build_enrichment_prompt("Synthetic workflow text.", analysis, "English")
    lowered = prompt.casefold()
    assert "bounded local ai reviewer assistant" in lowered
    assert "deterministic engine is the source of truth" in lowered
    assert "do not change the score" in lowered
    assert "reviewer questions" in lowered
    assert "missing-context questions" in lowered


def test_local_ai_generation_cannot_mutate_deterministic_analysis(monkeypatch):
    import copy

    analysis = analyze_workflow(get_example_text("customer_support"))
    before = copy.deepcopy(analysis)

    monkeypatch.setattr(
        "ollama_client.check_ollama_status",
        lambda **kwargs: {"available": True, "models": ["llama3"]},
    )

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": "Reviewer wording only; score should be 0."}

    monkeypatch.setattr("ollama_client._direct_request", lambda *args, **kwargs: Response())
    output = generate_enrichment("Synthetic workflow.", analysis, "English")
    assert output == "Reviewer wording only; score should be 0."
    assert analysis == before
    assert output not in analysis


def test_user_and_local_ai_html_is_escaped_in_report_preview():
    analysis = analyze_workflow("AI drafts a customer reply containing <script>alert('x')</script> for human review.")
    markdown = render_markdown_report(analysis, enrichment="<img src=x onerror=alert(1)>")
    html = markdown_to_html(markdown)
    assert "<script>" not in html
    assert "<img src=x" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
