from analyzer import analyze_workflow
from export_json import build_json_summary
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
        "checklist_status_recommended_not_verified",
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


def test_control_checklist_status_is_explicitly_recommended_not_verified():
    assert load_locale("en")["checklist_status_recommended_not_verified"] == "Recommended — not verified"
    assert load_locale("fr")["checklist_status_recommended_not_verified"] == "Recommandé — non vérifié"
    assert load_locale("he")["checklist_status_recommended_not_verified"] == "מומלץ — לא אומת"


def test_dynamic_labels_are_localized():
    assert translate_severity("high", "fr") == "Élevé"
    assert translate_filter_option("all", "fr") == "Tous"
    assert translate_filter_option("all", "he").strip()
    french_results = format_showing_results(5, 12, "fr")
    assert "Showing" not in french_results
    assert "filtered " + "findings" not in french_results


def test_v2_core_ui_keys_exist_in_all_locales():
    required = [
        "home_badge_deterministic",
        "home_badge_human_review",
        "reset_demo_db_warning_v2",
        "delete_project_warning",
        "delete_project_confirm",
        "clear_input_help",
        "clear_session_help",
        "simulation_not_proof_warning",
        "human_review_question_label",
        "simulation_assumption_label",
        "evidence_required_label",
        "implementation_check_label",
        "local_ai_adds_questions",
        "factor_automatic_financial_decision",
        "factor_missing_appeal_process",
        "factor_local_ai_only_present",
    ]
    for language in ("en", "fr", "he"):
        locale = load_locale(language)
        assert all(str(locale[key]).strip() for key in required)


def test_visual_cockpit_and_launcher_keys_exist_in_all_locales():
    required = [
        "risk_cockpit_title",
        "risk_cockpit_subtitle",
        "cockpit_human_note",
        "simulation_assumptions_not_proof",
        "local_ai_brain_title",
        "local_ai_authority_body",
        "sidebar_command_center",
        "sidebar_navigation_label",
        "nav_start_input",
        "nav_risk_cockpit",
        "header_local_first_value",
        "analysis_success_state_body",
        "analysis_error_public_message",
        "workflow_file_uploader",
        "workflow_file_loaded",
        "start_workbench_title",
        "main_example_selector_label",
        "workflow_source_examples",
        "workflow_source_demos",
        "workflow_source_example_picker_title",
        "workflow_source_demo_picker_title",
        "workflow_source_choice_label",
        "workflow_source_choice_help",
        "load_example_button",
        "analyze_button_help",
        "workbench_source_of_truth",
        "workbench_local_ai_boundary",
        "export_state_detail",
        "post_analysis_actions_title",
        "post_action_evidence",
        "post_action_simulation",
        "post_action_reports",
        "post_action_local_ai",
        "simulation_inline_subtitle",
        "desktop_launcher_title",
        "desktop_launcher_local_only",
        "shell_local_first_badge",
        "shell_advisory_ai_badge",
        "command_engine_title",
        "command_local_title",
        "command_session_title",
        "command_review_title",
        "workbench_check_paste_import",
        "workbench_check_local_only",
        "workbench_check_human_review",
        "workbench_check_save_explicit",
        "workbench_status_subtitle",
        "workbench_source_title",
        "workbench_privacy_title",
        "workbench_local_ai_title",
        "analysis_success_state_title",
        "analysis_ready_state_title",
        "analysis_ready_state_body",
        "deterministic_ready_title",
        "deterministic_ready_body",
        "deterministic_ready_detail",
        "pipeline_input",
        "pipeline_local_rules",
        "pipeline_evidence",
        "pipeline_human_review",
        "pipeline_report",
        "pipeline_stage_label",
        "pipeline_ready_label",
        "pipeline_running_label",
        "pipeline_done_label",
        "dynamic_cockpit_local_rules_active",
        "dynamic_cockpit_report_ready",
        "local_ai_unavailable_compact",
        "local_ai_disabled_compact",
        "local_ai_advisory_not_generated",
        "analysis_empty_state_title",
        "control_card_title",
        "why_recommended_label",
        "control_card_limit",
        "controls_recommended_not_applied_caption",
    ]
    for language in ("en", "fr", "he"):
        locale = load_locale(language)
        assert all(str(locale[key]).strip() for key in required)


def test_settings_and_loading_locale_keys_exist_in_all_languages():
    required = [
        "settings_bar_title",
        "settings_bar_body",
        "settings_language_label",
        "settings_theme_label",
        "theme_light_option",
        "theme_dark_option",
        "shutdown_system_help",
        "shutdown_system_caption",
        "shutdown_system_notice",
        "workflow_optional_import_caption",
        "workflow_optional_import_expander",
        "workflow_action_row_hint",
        "workbench_session_compact_title",
        "workbench_trust_details_title",
        "reset_demo_db_danger_title",
        "reset_demo_db_short_warning",
        "loading_deterministic_title",
        "loading_deterministic_body",
        "loading_local_ai_title",
        "loading_local_ai_body",
        "loading_simulation_title",
        "loading_simulation_body",
        "loading_export_title",
        "loading_export_body",
        "loading_report_title",
        "loading_report_body",
        "explanation_local_first_body",
        "explanation_residual_risk_body",
        "explanation_risk_score_body",
        "explanation_auditability_body",
        "explanation_knowledge_base_body",
        "dashboard_scope_details_title",
        "dashboard_secondary_details_title",
    ]
    for language in ("en", "fr", "he"):
        locale = load_locale(language)
        for key in required:
            assert key in locale
            assert str(locale[key]).strip()


def test_theme_toggle_labels_are_short_and_localized():
    expected = {
        "en": ("☀️ Light", "🌙 Dark"),
        "fr": ("☀️ Clair", "🌙 Sombre"),
        "he": ("☀️ בהיר", "🌙 כהה"),
    }
    for language, labels in expected.items():
        locale = load_locale(language)
        assert locale["theme_light_option"] == labels[0]
        assert locale["theme_dark_option"] == labels[1]
        assert "light" not in locale["theme_dark_option"].casefold()
        assert "dark" not in locale["theme_light_option"].casefold()


def test_visual_state_placeholders_match_across_locales():
    for language in ("en", "fr", "he"):
        assert "{count}" in load_locale(language)["analysis_success_state_body"]
        assert "{name}" in load_locale(language)["workflow_file_loaded"]
        assert "{state}" in load_locale(language)["workbench_local_ai_boundary"]


def test_optional_local_ai_wording_is_non_blocking_in_all_locales():
    expected = {
        "en": {
            "ready": "Deterministic analysis ready",
            "report": "deterministic report ready",
            "advisory": "advisory only",
            "not_generated": "Ollama did not provide advisory wording",
        },
        "fr": {
            "ready": "Analyse déterministe prête",
            "report": "rapport déterministe prêt",
            "advisory": "consultative uniquement",
            "not_generated": "Ollama n’a pas fourni de narration consultative",
        },
        "he": {
            "ready": "ניתוח דטרמיניסטי מוכן",
            "report": "הדוח הדטרמיניסטי מוכן",
            "advisory": "מייעץ בלבד",
            "not_generated": "Ollama לא סיפק ניסוח מייעץ",
        },
    }
    blocked_by_language = {
        "en": ["Local narrative enrichment failed", "AI failed"],
        "fr": ["L'enrichissement narratif local a échoué", "erreur IA"],
        "he": ["ההעשרה המקומית נכשלה"],
    }

    for language, phrases in expected.items():
        locale = load_locale(language)
        assert locale["deterministic_ready_title"] == phrases["ready"]
        assert phrases["report"] in locale["local_ai_unavailable_compact"]
        assert phrases["advisory"] in locale["local_ai_disabled_compact"]
        assert phrases["not_generated"] in locale["local_ai_advisory_not_generated"]
        for phrase in blocked_by_language[language]:
            assert phrase not in locale["ollama_enrichment_failed"]
            assert phrase not in locale["local_ai_unavailable_compact"]


def test_known_english_simulation_phrase_is_not_visible_in_french_or_hebrew():
    blocked = [
        "The estimated risk after selected controls are modeled in a local hypothetical simulation",
        "estimated risk after selected controls",
        "local hypothetical simulation",
    ]
    for language in ("fr", "he"):
        locale_text = "\n".join(str(value) for value in load_locale(language).values())
        residual_body = t("explanation_residual_risk_body", language, "")
        for phrase in blocked:
            assert phrase not in locale_text
            assert phrase not in residual_body


def test_rebuild_button_labels_exist_in_all_locales():
    required = [
        "analyze_button",
        "clear_input_button",
        "clear_session_button",
        "load_example_button",
        "save_report_button",
        "download_button",
        "download_json_button",
        "simulate_button",
        "reset_demo_db_button",
        "delete_project_button",
        "local_ai_generate_current",
    ]
    for language in ("en", "fr", "he"):
        locale = load_locale(language)
        for key in required:
            assert str(locale[key]).strip()


def test_deterministic_result_does_not_change_with_ui_language():
    text = "AI drafts a customer reply from anonymized notes. A human reviewer approves before sending."
    baseline = analyze_workflow(text)
    for language in ("en", "fr", "he"):
        summary = build_json_summary(baseline, language=language)
        assert summary["risk"] == baseline["risk"]
        assert summary["risk_matrix"] == baseline["risk_matrix"]


def test_json_technical_keys_remain_stable_across_locales():
    analysis = analyze_workflow("AI automatically approves customer refunds without review.")
    keys = set(build_json_summary(analysis, language="en"))
    assert set(build_json_summary(analysis, language="fr")) == keys
    assert set(build_json_summary(analysis, language="he")) == keys
