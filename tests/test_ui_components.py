import ast
from pathlib import Path
import re

from analyzer import analyze_workflow
from design_tokens import FONT_STACK, normalize_severity, normalize_status, severity_token, status_token
from examples import get_example_text
from ollama_client import (
    build_enrichment_prompt,
    build_synthetic_test_prompt,
    generate_local_prompt_response,
)
from ui_components import (
    apply_global_styles,
    build_heatmap_cells,
    build_matrix_cells,
    render_app_status_header,
    render_command_cockpit,
    render_control_card,
    render_deterministic_loading_panel,
    render_evidence_card,
    render_export_loading_panel,
    render_loading_panel,
    render_local_ai_loading_panel,
    render_local_ai_brain_panel,
    render_local_pipeline_strip,
    render_mission_pulse,
    render_risk_cockpit,
    render_simulation_loading_panel,
    render_state_panel,
    render_workbench_frame,
)


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
    def fail_request(*args, **kwargs):
        raise AssertionError("remote endpoint should not be called")

    monkeypatch.setattr("ollama_client._direct_request", fail_request)
    assert generate_local_prompt_response("prompt", base_url="https://example.com") is None


def test_engine_aware_components_escape_dynamic_values(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    render_app_status_header(
        "<script>AIWRA</script>",
        "<b>subtitle</b>",
        [{"label": "<img>", "value": "<iframe>"}],
    )
    render_state_panel("<svg>", "<script>state</script>", "local_only", "<style>bad</style>", "<")
    render_mission_pulse("ready_to_analyze", "<script>mission</script>", "<img src=x>", "en", "<style>bad</style>")
    render_command_cockpit(
        [
            {
                "title": "<script>title</script>",
                "value": "<b>value</b>",
                "body": "<iframe>body</iframe>",
                "status": "calculated",
            }
        ],
        "en",
    )
    render_workbench_frame("<script>workbench</script>", "<img src=x>", ["<svg>"], "en")
    render_local_pipeline_strip("report<script>", "en")
    render_control_card(
        {
            "id": "<script>ctrl</script>",
            "name": "<b>control</b>",
            "description": "<img src=x>",
            "reason": "<iframe>",
            "implementation_guidance": "<style>",
            "risk_factors": ["<svg>"],
        },
        1,
        "en",
    )
    render_evidence_card(
        {
            "severity": "critical",
            "category": "general",
            "matched_text_evidence": "<img src=x onerror=alert(1)>",
            "matched_rule_id": "<script>bad()</script>",
            "confidence": "high",
            "score_impact": 9,
            "why_it_matters": "<b>unsafe</b>",
            "recommended_controls": ["<iframe>"],
            "human_review_question": "<svg onload=alert(1)>",
            "residual_simulation_assumption": "<style>body{display:none}</style>",
            "limitation": "<a href=https://example.com>link</a>",
        },
        1,
        "en",
    )
    render_risk_cockpit("<script>", "critical", 1, True, False, "not_run", "en")

    output = "\n".join(rendered)
    assert "<script>bad()" not in output
    assert "<img src=x" not in output
    assert "<iframe>" not in output
    assert '<div class="aiwra-status-item">' not in output
    assert "&lt;div class=&quot;aiwra-status-item&quot;&gt;" not in output
    assert "<script>AIWRA" not in output
    assert "<script>state" not in output
    assert "<script>mission" not in output
    assert "<script>title" not in output
    assert "<script>workbench" not in output
    assert "<script>ctrl" not in output
    assert "<script" not in output
    assert "onclick=" not in output
    assert "&lt;script&gt;" in output
    assert "&lt;img src=x onerror=alert(1)&gt;" in output
    assert "&lt;img src=x&gt;" in output
    assert "aiwra-mission-pulse" in output


def test_hebrew_rtl_isolates_technical_content_as_ltr(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    apply_global_styles("he")
    render_local_ai_brain_panel(True, "http://127.0.0.1:11434", 1, 0, "he")
    render_evidence_card(
        {
            "severity": "high",
            "category": "security",
            "matched_rule_id": "RULE-RTL-001",
        },
        1,
        "he",
    )
    render_control_card({"id": "ctrl_access_logging", "risk_factors": ["missing_audit_trail"]}, 1, "he")
    render_command_cockpit(
        [{"title": "Local", "value": "127.0.0.1", "body": "Loopback", "status": "local_only", "technical_value": True}],
        "he",
    )
    render_local_pipeline_strip("human_review", "he")

    output = "\n".join(rendered)
    assert ".aiwra-technical" in output
    assert "unicode-bidi: isolate" in output
    assert "white-space: normal" in output
    assert "repeat(auto-fit, minmax(min(100%, 15rem), 1fr))" in output
    assert ".aiwra-command-card .aiwra-technical" in output
    assert '<bdi class="aiwra-technical">http://127.0.0.1:11434 · 127.0.0.1</bdi>' in output
    assert '<bdi class="aiwra-technical">RULE-RTL-001</bdi>' in output
    assert '<bdi class="aiwra-technical">ctrl_access_logging</bdi>' in output
    assert '<bdi class="aiwra-technical">127.0.0.1</bdi>' in output
    assert ".aiwra-pipeline-strip" in output


def test_information_cards_do_not_use_button_like_hover(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    apply_global_styles("en")

    output = "\n".join(rendered)
    assert ".aiwra-card:hover" not in output
    assert ".aiwra-bento-card:hover" not in output
    assert ".aiwra-flow-step:hover" not in output
    assert ".aiwra-shell-header" in output
    assert ".aiwra-command-cockpit" in output
    assert ".aiwra-workbench-frame" in output
    assert '[data-testid="stButton"] button' in output
    assert '[data-testid="stDownloadButton"] button' in output
    assert ".st-key-analyze_workflow_primary button" in output
    assert ".st-key-clear_input_secondary button" in output
    assert ".st-key-reset_demo_database_danger button" in output
    assert ".st-key-download_markdown_action button" in output


def test_streamlit_shell_selectors_are_tag_agnostic_and_cover_dark_mode(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    apply_global_styles("fr", "dark")
    output = "\n".join(rendered)

    assert '[data-testid="stSidebar"]' in output
    assert '[data-testid="stSidebarContent"]' in output
    assert '[data-testid="stSidebarUserContent"]' in output
    assert '[data-testid="stSidebarHeader"]' in output
    assert '[data-testid="stHeader"]' in output
    assert '[data-testid="stToolbar"]' in output
    assert '[data-testid="stMainMenu"]' in output
    assert '[data-testid="stMainMenuButton"]' in output
    assert 'div[data-testid="stSidebar"]' not in output
    assert 'div[data-testid="stHeader"]' not in output
    assert "color: var(--aiwra-text-primary) !important" in output
    assert "background: var(--aiwra-sidebar-bg) !important" in output


def test_streamlit_toolbar_viewer_mode_is_configured():
    config = Path(".streamlit/config.toml").read_text(encoding="utf-8")

    assert "[client]" in config
    assert 'toolbarMode = "viewer"' in config
    assert 'address = "127.0.0.1"' in config
    assert "0.0.0.0" not in config


def test_command_cockpit_and_workbench_are_not_buttons(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    render_command_cockpit(
        [
            {
                "title": "Deterministic engine",
                "value": "Source of truth",
                "body": "Score and evidence come from local rules.",
                "status": "calculated",
            },
            {
                "title": "Local boundary",
                "value": "127.0.0.1",
                "body": "Localhost only.",
                "status": "local_only",
                "technical_value": True,
            },
            {
                "title": "Session",
                "value": "Unsaved",
                "body": "Save explicitly.",
                "status": "local_only",
            },
            {
                "title": "Review",
                "value": "Yes",
                "body": "Human review remains required.",
                "status": "needs_human_review",
            },
        ],
        "en",
    )
    render_workbench_frame(
        "Start local workflow audit",
        "Paste, import, or describe a workflow.",
        ["Local analysis by default", "Human review required"],
        "en",
    )

    output = "\n".join(rendered)
    assert '<div class="aiwra-command-cockpit">' in output
    assert output.count('class="aiwra-command-card"') == 4
    assert '<div class="aiwra-workbench-frame"' in output
    assert "<article" not in output
    assert "<section" not in output
    assert "&lt;div class=&quot;aiwra-command-card" not in output
    assert "&lt;article" not in output
    for fragment in rendered:
        assert fragment == fragment.strip()
        assert all(not line.startswith(("    <", "\t<")) for line in fragment.splitlines())
    assert "<button" not in output
    assert "Analyze Workflow" not in output


def test_rtl_css_does_not_apply_direction_to_streamlit_shell(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    apply_global_styles("he")
    output = "\n".join(rendered)

    for testid in ("stAppViewContainer", "stSidebar"):
        blocks = re.findall(rf'\[data-testid="{testid}"\]\s*\{{[^}}]*\}}', output, flags=re.S)
        assert all("direction: rtl" not in block for block in blocks)
        assert all("text-align: right" not in block for block in blocks)
    assert ".aiwra-loading-panel" in output
    assert ".aiwra-shell-header" in output
    assert "[data-testid=\"stTextArea\"] textarea" in output
    assert "unicode-bidi: plaintext" in output


def test_header_settings_controls_are_not_sidebar_selectboxes():
    app_source = Path("app.py").read_text(encoding="utf-8")
    language_block = re.search(r"def _language_selector\(\).*?(?=\ndef _theme_selector)", app_source, flags=re.S)
    theme_block = re.search(r"def _theme_selector\(language: str\).*?(?=\ndef _scenario_options)", app_source, flags=re.S)

    assert language_block is not None
    assert theme_block is not None
    assert "_render_settings_intro" not in app_source
    assert "aiwra-settings-intro" not in app_source
    assert "settings_bar_body" not in app_source
    assert "st.sidebar" not in language_block.group(0)
    assert "st.sidebar" not in theme_block.group(0)
    assert "st.radio" not in language_block.group(0)
    assert "st.toggle" not in theme_block.group(0)
    assert "st.radio" not in theme_block.group(0)
    assert "LANGUAGE_ACTION_KEYS" in app_source
    assert '"language_action_en"' in app_source
    assert '"language_action_fr"' in app_source
    assert '"language_action_he"' in app_source
    assert 'key="theme_action_toggle_header"' in app_source
    assert 'st.session_state["language_selector_header"]' in app_source
    assert 'key="theme_mode_selector"' not in app_source
    assert 'THEME_MODE_TOGGLE_KEY = "theme_mode_toggle_header"' in app_source
    assert "settings_toolbar_header" in app_source


def test_theme_toggle_uses_stable_bool_state_without_default_conflict():
    app_source = Path("app.py").read_text(encoding="utf-8")
    normalize_block = re.search(r"def _normalize_theme_toggle_state\(.*?(?=\ndef _theme_selector)", app_source, flags=re.S)
    theme_block = re.search(r"def _theme_selector\(language: str\).*?(?=\ndef _scenario_options)", app_source, flags=re.S)

    assert normalize_block is not None
    assert "isinstance(value, bool)" in normalize_block.group(0)
    assert "THEME_DARK_LEGACY_VALUES" in normalize_block.group(0)
    assert "THEME_LIGHT_LEGACY_VALUES" in normalize_block.group(0)

    assert theme_block is not None
    button_call = re.search(r"st\.button\((.*?)\n        \)", theme_block.group(0), flags=re.S)
    assert button_call is not None
    assert 'key="theme_action_toggle_header"' in button_call.group(1)
    assert "on_click=_toggle_theme_header" in button_call.group(1)
    assert "index=" not in button_call.group(1)
    assert "value=" not in button_call.group(1)
    assert "format_func" not in button_call.group(1)
    assert "theme_label" in button_call.group(1)
    assert "_set_theme_state" in app_source
    assert 'st.session_state[THEME_MODE_TOGGLE_KEY]' in app_source
    assert 'st.session_state["theme_mode"]' in app_source


def test_theme_toolbar_css_is_compact_and_offset(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    apply_global_styles("en", "dark")
    output = "\n".join(rendered)

    assert ".st-key-settings_toolbar_header" in output
    assert ".aiwra-settings-toolbar" in output
    assert "margin: 0 0 0.56rem" in output
    assert "direction: ltr !important" in output
    assert ".st-key-language_control_cluster" in output
    assert ".st-key-theme_control_cluster" in output
    assert ".st-key-theme_action_toggle_header button" in output
    assert ".st-key-theme_mode_toggle_header [data-testid=\"stToggle\"]" not in output
    settings_block = re.search(r"\.st-key-settings_toolbar_header,.*?\n        \}", output, flags=re.S)
    assert settings_block is not None
    assert "border: 0" in settings_block.group(0)
    assert "box-shadow" not in settings_block.group(0)
    assert "justify-content: flex-end" not in output
    assert "justify-content: flex-start" not in output


def test_global_styles_are_applied_before_header_toolbar():
    app_source = Path("app.py").read_text(encoding="utf-8")

    assert "apply_global_styles(language, theme_mode)" in app_source
    assert 'with st.container(key="settings_toolbar_header")' in app_source
    assert app_source.index("apply_global_styles(language, theme_mode)") < app_source.index(
        'with st.container(key="settings_toolbar_header")'
    )


def test_start_input_actions_do_not_use_button_help_wrappers():
    app_source = Path("app.py").read_text(encoding="utf-8")
    target_keys = (
        "analyze_workflow_primary",
        "load_example_secondary",
        "clear_input_secondary",
        "clear_session_secondary",
    )

    for key in target_keys:
        button_call = re.search(rf"st\.button\((?:(?!st\.button\().)*?key=\"{key}\".*?\)", app_source, flags=re.S)
        assert button_call is not None
        assert "help=" not in button_call.group(0)


def test_file_uploader_is_secondary_after_textarea():
    app_source = Path("app.py").read_text(encoding="utf-8")
    textarea_index = app_source.index("workflow_text = st.text_area(")
    uploader_index = app_source.index('key="workflow_file_import_control"')
    expander_index = app_source.index('with st.expander(t("workflow_optional_import_expander"')

    assert textarea_index < expander_index < uploader_index
    assert "workflow_optional_import_caption" in app_source
    assert "workflow_import_payload" in app_source


def test_start_support_column_is_compact_and_privacy_not_repeated():
    app_source = Path("app.py").read_text(encoding="utf-8")
    support_block = re.search(r"with support_col:.*?\n\n    if analyze:", app_source, flags=re.S)

    assert support_block is not None
    assert "workbench_session_compact_title" in support_block.group(0)
    assert "workbench_trust_details_title" in support_block.group(0)
    assert support_block.group(0).count("render_state_panel(") == 0
    assert support_block.group(0).count("privacy_warning") == 1
    assert "score_disclaimer(language)" not in support_block.group(0)
    assert "_show_simple_legend(language)" not in support_block.group(0)


def test_sidebar_reset_database_is_inside_closed_danger_expander():
    app_source = Path("app.py").read_text(encoding="utf-8")
    reset_block = re.search(
        r"with st\.sidebar\.expander\(t\(\"reset_demo_db_danger_title\".*?local_data_notice =",
        app_source,
        flags=re.S,
    )

    assert reset_block is not None
    assert "expanded=False" in reset_block.group(0)
    assert 'key="confirm_reset_demo_database_danger"' in reset_block.group(0)
    assert 'key="reset_demo_database_danger"' in reset_block.group(0)
    assert 'st.sidebar.warning(\n    t(\n        "reset_demo_db_warning_v2"' not in app_source


def test_global_style_root_has_no_critical_duplicate_variables(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    apply_global_styles("en", "dark")
    output = "\n".join(rendered)

    for variable in ("--aiwra-border-soft", "--aiwra-radius-sm", "--aiwra-font-mono"):
        assert output.count(f"{variable}:") == 1


def test_sidebar_navigation_uses_stable_ids_and_active_page_state():
    app_source = Path("app.py").read_text(encoding="utf-8")
    nav_ids_match = re.search(r"NAVIGATION_PAGE_IDS = (\([^\n]+\))", app_source)
    navigation_block = re.search(r"def _navigation_options\(.*?(?=\ndef _show_explanation)", app_source, flags=re.S)
    language_block = re.search(r"def _language_selector\(\).*?(?=\ndef _theme_selector)", app_source, flags=re.S)

    assert nav_ids_match is not None
    assert ast.literal_eval(nav_ids_match.group(1)) == (
        "start",
        "risk",
        "controls",
        "exports",
        "knowledge",
        "local_ai",
    )
    assert navigation_block is not None
    assert "NAVIGATION_PAGE_LABEL_KEYS" in navigation_block.group(0)
    assert "options=list(NAVIGATION_PAGE_IDS)" in app_source
    assert 'key="active_page"' in app_source
    assert 'st.session_state["active_page"]' in app_source
    assert "_normalize_active_page" in app_source
    assert language_block is not None
    assert "active_page" not in language_block.group(0)


def test_workflow_source_selector_is_not_duplicated_in_sidebar():
    app_source = Path("app.py").read_text(encoding="utf-8")

    assert 'st.sidebar.selectbox(t("example_selector"' not in app_source
    assert 'key="main_example_selector"' in app_source
    source_block = re.search(r"def _select_workflow_source\(.*?(?=\ndef _navigation_options)", app_source, flags=re.S)
    assert source_block is not None
    assert "st.selectbox" not in source_block.group(0)
    assert "st.radio" in source_block.group(0)
    assert 'key="main_example_selector_mode"' in source_block.group(0)


def test_workflow_source_selector_uses_stable_ids_not_translated_labels():
    app_source = Path("app.py").read_text(encoding="utf-8")
    source_ids_match = re.search(r"WORKFLOW_SOURCE_MODE_IDS = (\([^\n]+\))", app_source)
    source_block = re.search(r"def _select_workflow_source\(.*?(?=\ndef _navigation_options)", app_source, flags=re.S)

    assert source_ids_match is not None
    assert ast.literal_eval(source_ids_match.group(1)) == ("custom", "examples", "demos")
    assert source_block is not None
    assert "mode_keys = list(WORKFLOW_SOURCE_MODE_IDS)" in source_block.group(0)
    assert "format_func=lambda key: mode_labels[key]" in source_block.group(0)
    assert "choice_keys" in source_block.group(0)
    assert "format_func=lambda key: choice_labels[key]" in source_block.group(0)
    assert "choice_labels = [" not in source_block.group(0)
    assert "_scenario_key_from_state" in app_source
    assert "selected_label" not in source_block.group(0)


def test_workflow_source_widgets_are_session_state_driven_without_default_index():
    app_source = Path("app.py").read_text(encoding="utf-8")
    source_block_match = re.search(r"def _select_workflow_source\(.*?(?=\ndef _navigation_options)", app_source, flags=re.S)

    assert source_block_match is not None
    source_block = source_block_match.group(0)
    mode_call = re.search(r"selected_mode = st\.radio\((.*?)\n    \)", source_block, flags=re.S)
    choice_call = re.search(r"selected_choice_key = st\.radio\((.*?)\n        \)", source_block, flags=re.S)

    assert mode_call is not None
    assert 'key="main_example_selector_mode"' in mode_call.group(1)
    assert "index=" not in mode_call.group(1)
    assert "value=" not in mode_call.group(1)
    assert 'st.session_state["main_example_selector_mode"] = selected_mode' not in source_block
    after_mode_widget = source_block.split('key="main_example_selector_mode"', 1)[1]
    assert 'st.session_state["main_example_selector_mode"]' not in after_mode_widget

    assert choice_call is not None
    assert 'key="main_example_selector"' in choice_call.group(1)
    assert "index=" not in choice_call.group(1)
    assert "value=" not in choice_call.group(1)


def test_workflow_textarea_avoids_value_when_callbacks_write_widget_state():
    app_source = Path("app.py").read_text(encoding="utf-8")
    textarea_block = re.search(r"workflow_text = st\.text_area\(.*?\n        \)", app_source, flags=re.S)

    assert textarea_block is not None
    assert "key=workflow_widget_key" in textarea_block.group(0)
    assert "value=default_text" not in textarea_block.group(0)
    assert "st.session_state[workflow_widget_key] = default_text" in app_source


def test_empty_workflow_state_is_not_rendered_as_bottom_state_panel():
    app_source = Path("app.py").read_text(encoding="utf-8")
    ready_block = re.search(r"elif workflow_text\.strip\(\):.*?render_local_pipeline_strip\(\"input\", language\)", app_source, flags=re.S)

    assert ready_block is not None
    assert "analysis_ready_state_title" in ready_block.group(0)
    assert "analysis_empty_state_title" not in ready_block.group(0)
    assert 'render_state_panel(\n            t("analysis_empty_state_title"' not in app_source
    assert "no_workflow_loaded" not in app_source


def test_start_input_dynamic_pulse_and_pipeline_are_single_and_ordered():
    app_source = Path("app.py").read_text(encoding="utf-8")
    ready_block = re.search(r"elif workflow_text\.strip\(\):.*?if analysis and analysis\.get\(\"valid\"\):", app_source, flags=re.S)
    report_block = re.search(r"elif isinstance\(analysis, dict\) and analysis\.get\(\"valid\"\):.*?elif workflow_text\.strip\(\):", app_source, flags=re.S)

    assert ready_block is not None
    assert ready_block.group(0).count("render_mission_pulse(") == 1
    assert ready_block.group(0).count('render_local_pipeline_strip("input", language)') == 1
    assert ready_block.group(0).index("render_mission_pulse(") < ready_block.group(0).index('render_local_pipeline_strip("input", language)')

    assert report_block is not None
    assert report_block.group(0).count("render_mission_pulse(") == 1
    assert report_block.group(0).count('render_local_pipeline_strip("report", language)') == 1
    assert report_block.group(0).index("render_mission_pulse(") < report_block.group(0).index('render_local_pipeline_strip("report", language)')


def test_textarea_css_forces_theme_safe_input_colors(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    apply_global_styles("en", "dark")
    output = "\n".join(rendered)

    assert '[data-testid="stTextArea"] textarea' in output
    assert '[data-testid="stTextAreaRootElement"] textarea' in output
    assert "color: var(--aiwra-text-primary) !important" in output
    assert "-webkit-text-fill-color: var(--aiwra-text-primary) !important" in output
    assert "caret-color: var(--aiwra-primary) !important" in output
    assert "background: var(--aiwra-input-bg) !important" in output
    assert "textarea::placeholder" in output
    assert "color: var(--aiwra-muted) !important" in output
    assert "textarea::selection" in output
    assert "background: color-mix(in srgb, var(--aiwra-primary) 34%, transparent) !important" in output


def test_lato_and_hebrew_fallback_are_in_font_stack():
    assert '"Lato"' in FONT_STACK
    assert '"Noto Sans Hebrew"' in FONT_STACK
    assert '"Rubik"' in FONT_STACK
    assert "system-ui" in FONT_STACK


def test_loading_panel_renderers_exist_and_escape_html(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    render_loading_panel("<script>x</script>", "<img src=x>", "advisory", "<style>bad</style>", "en")
    render_deterministic_loading_panel("en")
    render_local_ai_loading_panel("en")
    render_simulation_loading_panel("en")
    render_export_loading_panel("en")

    output = "\n".join(rendered)
    assert "aiwra-loading-panel" in output
    assert "aiwra-loading-orb" in output
    assert "<script>x</script>" not in output
    assert "<img src=x>" not in output
    assert "<style>bad</style>" not in output
    assert "&lt;script&gt;x&lt;/script&gt;" in output
    assert "&lt;img src=x&gt;" in output
    assert "&lt;style&gt;bad&lt;/style&gt;" in output
    assert "<article" not in output
    assert "<section" not in output
    assert "Local AI can draft wording only" in output
    assert "Scores, findings, controls and simulation stay deterministic" in output


def test_loading_css_supports_reduced_motion(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    apply_global_styles("en")
    output = "\n".join(rendered)

    assert ".aiwra-loading-panel" in output
    assert ".aiwra-loading-orb" in output
    assert ".aiwra-mission-pulse" in output
    assert ".aiwra-mission-rocket" in output
    assert ".aiwra-mission-flame" in output
    assert ".aiwra-mission-orbit" in output
    assert ".aiwra-mission-core" in output
    assert ".aiwra-mission-status" in output
    assert ".aiwra-pipeline-strip" in output
    assert ".aiwra-pipeline-orb" in output
    assert ".aiwra-shell-heartbeat" in output
    assert ".aiwra-status-dot" in output
    assert ".aiwra-cockpit-scan" in output
    assert ".aiwra-cockpit-score-glow" in output
    assert "@keyframes aiwra-spin" in output
    assert "@keyframes aiwra-local-heartbeat" in output
    assert "@keyframes aiwra-mission-orbit" in output
    assert "@keyframes aiwra-mission-flame" in output
    assert "@keyframes aiwra-pipeline-orb" in output
    assert "@keyframes aiwra-cockpit-scan" in output
    assert "@keyframes aiwra-score-glow" in output
    assert "animation: aiwra-score-glow" in output
    assert "@media (prefers-reduced-motion: reduce)" in output
    assert "animation: none" in output
    reduced_motion_block = output.split("@media (prefers-reduced-motion: reduce)", 1)[1]
    for selector in (
        "aiwra-mission",
        "aiwra-pipeline",
        "aiwra-shell-heartbeat",
        "aiwra-status-dot",
        "aiwra-loading-orb",
        "aiwra-cockpit-scan",
        "aiwra-cockpit-score-glow",
    ):
        assert selector in reduced_motion_block


def test_mission_pulse_component_is_safe_and_dynamic(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    render_mission_pulse("analyzing", "Local analysis in progress", "Deterministic engine only.", "en")
    render_mission_pulse("deterministic_ready", "Deterministic analysis ready", "Evidence-linked findings are available.", "en")
    render_mission_pulse("advisory_unavailable", "Local AI unavailable", "Deterministic report ready.", "en")
    render_mission_pulse("onclick=<script>", "<script>x</script>", "<img src=x>", "en")

    output = "\n".join(rendered)
    assert "aiwra-mission-pulse--analyzing" in output
    assert "aiwra-mission-pulse--deterministic_ready" in output
    assert "aiwra-mission-pulse--advisory_unavailable" in output
    assert "aiwra-mission-pulse--idle" in output
    assert "<script" not in output
    assert "onclick=" not in output
    assert "&lt;script&gt;x&lt;/script&gt;" in output
    assert "&lt;img src=x&gt;" in output


def test_mission_pulse_uses_render_html_not_raw_markdown():
    source = Path("ui_components.py").read_text(encoding="utf-8")
    component_block = re.search(r"def render_mission_pulse\(.*?(?=\ndef render_loading_panel)", source, flags=re.S)

    assert component_block is not None
    assert "render_html(" in component_block.group(0)
    assert "st.markdown(" not in component_block.group(0)
    assert "unsafe_allow_html=True" not in component_block.group(0)


def test_local_pipeline_strip_component_is_safe_dynamic_and_i18n(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    render_local_pipeline_strip("evidence", "fr")

    output = "\n".join(rendered)
    assert "aiwra-pipeline-strip" in output
    assert "aiwra-pipeline-step" in output
    assert "aiwra-pipeline-step--active" in output
    assert "aiwra-pipeline-step--done" in output
    assert "aiwra-pipeline-connector" in output
    assert "aiwra-pipeline-orb" in output
    assert "Saisie" in output
    assert "Règles locales" in output
    assert "Preuves" in output
    assert "<script" not in output
    assert "onclick=" not in output


def test_local_pipeline_strip_uses_render_html_not_raw_markdown():
    source = Path("ui_components.py").read_text(encoding="utf-8")
    component_block = re.search(r"def render_local_pipeline_strip\(.*?(?=\ndef render_loading_panel)", source, flags=re.S)

    assert component_block is not None
    assert "render_html(" in component_block.group(0)
    assert "st.markdown(" not in component_block.group(0)
    assert "_escape(" in component_block.group(0)


def test_loading_states_are_used_for_deterministic_and_local_ai_paths():
    app_source = Path("app.py").read_text(encoding="utf-8")

    assert "render_deterministic_loading_panel(language, target=analysis_loader)" in app_source
    assert "render_local_ai_loading_panel(language, target=local_ai_loader)" in app_source
    assert "render_simulation_loading_panel(language, target=simulation_loader)" in app_source
    assert "render_export_loading_panel(language, target=export_loader)" in app_source
    assert ".empty()" in app_source
    assert "st.spinner(" not in app_source


def test_optional_local_ai_unavailable_is_not_rendered_as_primary_failure():
    app_source = Path("app.py").read_text(encoding="utf-8")
    locale_text = "\n".join(Path(path).read_text(encoding="utf-8") for path in ("locales/en.json", "locales/fr.json", "locales/he.json"))

    assert 'st.info(t("ollama_enrichment_failed"' not in app_source
    assert 'st.warning(t("ollama_cloud_model_blocked"' not in app_source
    assert "local_ai_unavailable_compact" in app_source
    assert "local_ai_advisory_not_generated" in app_source
    assert app_source.count("_render_local_ai_compact_note(language)") == 1
    assert "Local narrative enrichment failed" not in locale_text
    assert "L'enrichissement narratif local a échoué" not in locale_text


def test_risk_cockpit_live_effects_are_css_only_and_escaped(monkeypatch):
    rendered = []
    monkeypatch.setattr("ui_components.st.markdown", lambda body, **kwargs: rendered.append(body))

    apply_global_styles("en")
    render_risk_cockpit("<script>", "high", 2, True, False, "not_run", "en")

    output = "\n".join(rendered)
    assert "aiwra-cockpit--live" in output
    assert "aiwra-cockpit-scan" in output
    assert "aiwra-cockpit-score-glow" in output
    assert "aiwra-status-dot" in output
    assert "<script>" not in output
    assert "onclick=" not in output
