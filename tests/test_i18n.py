from i18n import (
    available_languages,
    format_showing_results,
    is_rtl,
    load_locale,
    t,
    translate_filter_option,
    translate_severity,
)


def test_locales_have_same_keys_as_english():
    english_keys = set(load_locale("en"))
    for language in ("fr", "he"):
        assert set(load_locale(language)) == english_keys


def test_english_loads():
    locale = load_locale("en")
    assert locale["app_title"] == "AI Workflow Risk Auditor"


def test_french_loads():
    locale = load_locale("fr")
    assert locale["risk_level_high"] == "Élevé"


def test_hebrew_loads():
    locale = load_locale("he")
    assert locale["risk_level_critical"] == "קריטי"


def test_missing_key_falls_back_to_english():
    assert t("app_title", "unknown") == "AI Workflow Risk Auditor"
    assert t("missing.translation.key", "fr", default="fallback") == "fallback"


def test_language_metadata_and_rtl_flags():
    languages = available_languages()
    assert languages["he"]["rtl"] is True
    assert is_rtl("he") is True
    assert is_rtl("en") is False
    assert is_rtl("fr") is False


def test_visual_critical_locale_keys_are_present_and_non_empty():
    required = [
        "tab_local_ai",
        "dashboard_heatmap_title",
        "dashboard_workflow_graph_title",
        "dashboard_evidence_title",
        "issue_tracker_title",
        "control_checklist_title",
        "kb_read_only_title",
        "demo_scenarios_explainer_title",
        "local_ai_prompt_sent",
        "local_ai_exact_response",
        "accessibility_note_title",
        "status_needs_human_review_label",
        "severity_critical_description",
        "column_rule_id",
        "workflow_graph_required_note",
    ]
    for language in ("en", "fr", "he"):
        locale = load_locale(language)
        for key in required:
            assert key in locale
            assert str(locale[key]).strip()


def test_dynamic_labels_are_localized():
    assert translate_severity("high", "fr") == "Élevé"
    assert translate_filter_option("all", "fr") == "Tous"
    assert translate_filter_option("all", "he").strip()
    french_results = format_showing_results(5, 12, "fr")
    assert "Showing" not in french_results
    assert "filtered " + "findings" not in french_results
