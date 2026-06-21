from __future__ import annotations

import os
from collections import Counter

os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

import streamlit as st

from analyzer import analyze_workflow
from dashboard import load_dashboard_metrics
from database import init_db, reset_demo_db
from design_tokens import THEME_OPTIONS, normalize_theme, resolved_theme, theme_label
from demo_mode import get_demo_scenario_options, get_demo_steps
from examples import EXAMPLES, get_example_label, get_example_text
from export_json import render_json_summary
from i18n import (
    available_languages,
    format_count,
    format_showing_results,
    is_rtl,
    t,
    translate_category,
    translate_filter_option,
    translate_severity,
    translate_status,
)
from knowledge_loader import (
    get_explanation_card,
    knowledge_counts,
    load_control_library,
    load_data_categories,
    load_demo_scenarios,
    load_explanation_cards,
    load_risk_patterns,
)
from ollama_client import (
    DEFAULT_BASE_URL,
    build_enrichment_prompt,
    build_synthetic_test_prompt,
    check_ollama_status,
    generate_enrichment,
    generate_local_prompt_response,
    is_cloud_or_proxy_model,
)
from report_history import load_audit_trail, load_report_history, open_report
from report_renderer import markdown_to_html, render_markdown_report
from repositories import (
    create_project,
    list_projects,
    save_assessment,
    save_findings,
    save_recommended_controls,
    save_report,
    save_simulation_run,
    save_workflow,
    save_workflow_steps,
)
from residual_risk import default_control_selection, simulate_residual_risk
from risk_rules import get_risk_level
from score_explainability import (
    build_explainability_payload,
    one_minute_explanation,
    score_disclaimer,
    sorted_findings,
    source_of_truth_labels,
)
from ui_components import (
    apply_global_styles,
    humanize_key,
    render_accessibility_note,
    render_ai_output_panel,
    render_bento_cards,
    render_empty_state,
    render_evidence_card,
    render_heatmap,
    render_how_to_read_panel,
    render_info_card,
    render_issue_card,
    render_metric_card,
    render_read_only_notice,
    render_risk_matrix,
    render_section_header,
    render_status_badge,
    render_timeline,
    render_workflow_graph,
)


st.set_page_config(page_title="AI Workflow Risk Auditor Pro", layout="wide")
init_db()


def _language_selector() -> str:
    languages = list(available_languages().keys())
    current = str(st.session_state.get("language", "en"))
    if current not in languages:
        current = "en"
    labels = {str(available_languages()[code]["native"]): code for code in languages}
    selected_label = st.sidebar.selectbox(
        t("language_selector", current, "Language"),
        list(labels.keys()),
        index=languages.index(current),
    )
    selected = labels[selected_label]
    st.session_state["language"] = selected
    return selected


def _theme_selector(language: str) -> str:
    st.session_state.setdefault("theme_mode", "system")
    current = normalize_theme(st.session_state.get("theme_mode"))
    selected = st.sidebar.selectbox(
        t("appearance_label", language, "Appearance"),
        options=list(THEME_OPTIONS),
        index=list(THEME_OPTIONS).index(current),
        format_func=lambda value: theme_label(value, language),
        key="theme_mode_selector",
    )
    selected = normalize_theme(selected)
    st.session_state["theme_mode"] = selected
    if selected == "system":
        st.sidebar.caption(t("theme_system_fallback_note", language, "System uses the light theme in this local Streamlit build."))
    return selected


def _scenario_options(language: str) -> list[tuple[str, str, str]]:
    options = [("custom", t("custom_workflow", language), "")]
    for key in EXAMPLES:
        options.append((f"example:{key}", get_example_label(key, language), get_example_text(key)))
    for scenario in get_demo_scenario_options():
        options.append((f"demo:{scenario['id']}", str(scenario["name"]), str(scenario["workflow_text"])))
    return options


def _show_explanation(topic: str, fallback: str = "") -> None:
    card = get_explanation_card(topic)
    if card:
        st.info(f"{card['short_explanation']} {card['why_it_matters']}")
    elif fallback:
        st.info(fallback)


def _show_simple_legend(language: str) -> None:
    st.caption(" | ".join(source_of_truth_labels(language)))


def _finding_filter_options(findings: list[dict[str, object]], key: str) -> list[str]:
    values = sorted({str(finding.get(key, "unknown")) for finding in findings})
    return ["all"] + values


def _translate_column_map(language: str) -> dict[str, str]:
    return {
        "id": t("column_rule_id", language, "Rule ID"),
        "name": t("column_name", language, "Name"),
        "category": t("category_label", language, "Category"),
        "severity": t("severity_label", language, "Severity"),
        "status": t("status_label", language, "Status"),
        "evidence": t("evidence_label", language, "Evidence"),
        "rule": t("rule_used_label", language, "Rule used"),
        "confidence": t("confidence_label", language, "Confidence"),
        "recommended_control": t("recommended_action_label", language, "Recommended action"),
        "source": t("source_label", language, "Source"),
        "meaning": t("meaning_label", language, "Meaning"),
        "limit": t("limit_label", language, "Limit"),
        "topics": t("column_topics", language, "Topics"),
        "active": t("column_active", language, "Active"),
        "synthetic": t("column_synthetic", language, "Synthetic"),
        "notes": t("column_notes", language, "Notes"),
    }


def _category_label(value: object, language: str) -> str:
    return translate_category(value, language)


def _status_text(status: str, language: str) -> str:
    return translate_status(status, language)


def _current_findings() -> list[dict[str, object]]:
    analysis = st.session_state.get("analysis")
    if not analysis or not isinstance(analysis, dict) or not analysis.get("valid"):
        return []
    return [item for item in analysis.get("findings", []) if isinstance(item, dict)]


def _build_local_issues(findings: list[dict[str, object]], language: str) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    for finding in sorted_findings(findings)[:8]:
        severity = str(finding.get("severity", "unknown"))
        controls = finding.get("recommended_controls", [])
        control = ""
        if isinstance(controls, list) and controls:
            control = str(controls[0])
        elif controls:
            control = str(controls)
        issues.append(
            {
                "title": t(
                    "issue_review_title",
                    language,
                    "{category} review",
                ).format(category=translate_category(finding.get("category"), language)),
                "severity": severity,
                "status": "needs_human_review" if severity in {"high", "critical"} else "recommended",
                "evidence": str(finding.get("matched_text_evidence", "")),
                "control": control or t("issue_control_fallback", language, "Review the finding and decide whether a control is needed."),
                "human_review": t("yes_label", language, "Yes"),
            }
        )
    return issues


def _build_control_checklist(analysis: dict[str, object] | None, language: str) -> list[dict[str, str]]:
    findings = [item for item in (analysis or {}).get("findings", []) if isinstance(item, dict)]
    controls = [item for item in (analysis or {}).get("recommended_controls", []) if isinstance(item, dict)]
    factors = set()
    for finding in findings:
        for factor in finding.get("risk_factor_mapping", []):
            factors.add(str(factor))
    control_names = " ".join(str(control.get("name", "")) for control in controls).casefold()
    checkpoints = set(str(item) for item in (analysis or {}).get("human_checkpoints", []))
    items = [
        (
            "checklist_human_validation",
            bool(checkpoints) or "missing_human_validation" not in factors,
            t("checklist_human_validation_evidence", language, "Human checkpoints or missing-validation factors from local rules."),
        ),
        (
            "checklist_audit_trail",
            "missing_audit_trail" not in factors,
            t("checklist_audit_trail_evidence", language, "Audit trail wording or missing-audit factor from the deterministic analysis."),
        ),
        (
            "checklist_data_minimization",
            "data minimization" in control_names or any("data" in factor for factor in factors),
            t("checklist_data_minimization_evidence", language, "Recommended controls and detected sensitive data categories."),
        ),
        (
            "checklist_sensitive_data",
            bool((analysis or {}).get("sensitive_data")),
            t("checklist_sensitive_data_evidence", language, "Sensitive data categories detected from local workflow text."),
        ),
        (
            "checklist_external_review",
            "external_communication" in factors or "customer_facing_automated_output" in factors,
            t("checklist_external_review_evidence", language, "External communication factors detected or not detected."),
        ),
        (
            "checklist_ollama_local_only",
            True,
            t("checklist_ollama_local_only_evidence", language, "Ollama is optional and constrained to localhost."),
        ),
        (
            "checklist_no_cloud_required",
            True,
            t("checklist_no_cloud_required_evidence", language, "No cloud API is required for deterministic analysis."),
        ),
        (
            "checklist_residual_risk_explained",
            bool(st.session_state.get("simulation")),
            t("checklist_residual_risk_explained_evidence", language, "Residual risk is shown only after a local simulation."),
        ),
        (
            "checklist_report_export",
            True,
            t("checklist_report_export_evidence", language, "Markdown and JSON exports remain available."),
        ),
        (
            "checklist_human_review_before_production",
            True,
            t("checklist_human_review_before_production_evidence", language, "The app is advisory and not connected to production systems."),
        ),
    ]
    rows: list[dict[str, str]] = []
    columns = _translate_column_map(language)
    for key, present, evidence in items:
        status = "recommended" if present else "needs_human_review"
        rows.append(
            {
                columns["name"]: t(key, language, key.replace("_", " ").title()),
                columns["status"]: _status_text(status, language),
                columns["evidence"]: evidence,
                columns["limit"]: t(
                    "checklist_limit",
                    language,
                    "Checklist status is advisory and does not prove implementation.",
                ),
            }
        )
    return rows


def _saved_finding_total(metrics: dict[str, object]) -> int:
    heatmap = metrics.get("finding_heatmap", [])
    if not isinstance(heatmap, list):
        return 0
    total = 0
    for item in heatmap:
        if isinstance(item, dict):
            total += int(item.get("count") or 0)
    return total


def _needs_human_review(findings: list[dict[str, object]], level: str = "unknown") -> bool:
    if level in {"critical", "high"}:
        return True
    return any(str(finding.get("severity", "unknown")) in {"critical", "high"} for finding in findings)


def _render_dashboard_executive_overview(
    metrics: dict[str, object],
    current_analysis: object,
    current_findings: list[dict[str, object]],
    language: str,
) -> None:
    has_current_analysis = isinstance(current_analysis, dict) and bool(current_analysis.get("valid"))
    simulation = st.session_state.get("simulation")

    if has_current_analysis:
        explainability = build_explainability_payload(current_analysis, simulation, language)
        score_summary = explainability["score_summary"]
        risk_level = str(score_summary["level"])
        risk_value = f"{score_summary['level_label']} / {score_summary['score']}"
        finding_total = len(current_findings)
        risk_source = t("dashboard_exec_current_source", language, "Current deterministic session analysis.")
    else:
        saved_count = int(metrics.get("saved_analyses") or 0)
        average_risk = int(metrics.get("average_risk") or 0)
        risk_level = get_risk_level(average_risk) if saved_count else "unknown"
        risk_value = (
            f"{translate_severity(risk_level, language)} / {average_risk}"
            if saved_count
            else t("not_available_label", language, "Not available")
        )
        finding_total = _saved_finding_total(metrics)
        risk_source = t("dashboard_exec_saved_source", language, "Saved local SQLite reports.")

    human_review_required = _needs_human_review(current_findings, risk_level)
    report_ready = bool(st.session_state.get("report_markdown"))
    if isinstance(simulation, dict) and simulation.get("residual_risk"):
        residual = simulation["residual_risk"]
        residual_value = f"{translate_severity(residual.get('severity', 'unknown'), language)} / {residual.get('score', 0)}"
        residual_status = "simulated"
    else:
        residual_value = t("not_run_label", language, "Not run")
        residual_status = "uncertain"

    cards = [
        {
            "title": t("exec_risk_level_title", language, "Risk level"),
            "value": risk_value,
            "source": risk_source,
            "meaning": t("exec_risk_level_meaning", language, "Highest visible review priority for the current cockpit view."),
            "limit": t("exec_risk_level_limit", language, "Advisory priority only; not a compliance decision."),
            "status": "calculated" if risk_level != "unknown" else "uncertain",
            "severity": risk_level,
        },
        {
            "title": t("exec_findings_count_title", language, "Findings count"),
            "value": format_count("finding", finding_total, language),
            "source": t("exec_findings_count_source", language, "Detected text evidence and saved aggregate counts."),
            "meaning": t("exec_findings_count_meaning", language, "Shows how many attention points need review."),
            "limit": t("exec_findings_count_limit", language, "A finding is a signal, not proof by itself."),
            "status": "detected",
        },
        {
            "title": t("exec_human_review_title", language, "Human review required"),
            "value": t("yes_label", language, "Yes") if human_review_required else t("no_label", language, "No"),
            "source": t("exec_human_review_source", language, "Derived from severity and current evidence."),
            "meaning": t("exec_human_review_meaning", language, "Flags whether a responsible reviewer should inspect context before use."),
            "limit": t("exec_human_review_limit", language, "The app cannot approve or reject production use."),
            "status": "needs_human_review" if human_review_required else "recommended",
        },
        {
            "title": t("exec_local_only_title", language, "Local-only analysis"),
            "value": t("yes_label", language, "Yes"),
            "source": t("exec_local_only_source", language, "Deterministic rules, local files, and local SQLite."),
            "meaning": t("exec_local_only_meaning", language, "The core audit runs on this machine without a cloud API."),
            "limit": t("exec_local_only_limit", language, "Only explicit optional Ollama calls can use localhost models."),
            "status": "local_only",
        },
        {
            "title": t("exec_report_readiness_title", language, "Report readiness"),
            "value": t("ready_label", language, "Ready") if report_ready else t("not_ready_label", language, "Not ready"),
            "source": t("exec_report_readiness_source", language, "Current generated Markdown and JSON export state."),
            "meaning": t("exec_report_readiness_meaning", language, "Shows whether the current analysis has a report preview/export prepared."),
            "limit": t("exec_report_readiness_limit", language, "Local history is created only after explicit save."),
            "status": "calculated" if report_ready else "uncertain",
        },
        {
            "title": t("exec_residual_simulation_title", language, "Residual risk simulation"),
            "value": residual_value,
            "source": t("exec_residual_simulation_source", language, "Local simulation from selected mapped controls."),
            "meaning": t("exec_residual_simulation_meaning", language, "Shows planning impact after selected safeguards when available."),
            "limit": t("exec_residual_simulation_limit", language, "Simulation does not prove controls were implemented."),
            "status": residual_status,
            "severity": residual.get("severity", "unknown") if isinstance(simulation, dict) and isinstance(simulation.get("residual_risk"), dict) else "unknown",
        },
    ]
    render_bento_cards(cards, language)


def _render_product_hero(language: str) -> None:
    st.markdown(
        f"""
        <div class="aiwra-hero">
            <h2>{t("home_hero_title", language, "Local-first AI workflow risk auditor")}</h2>
            <p>{t("home_hero_body", language, "Audit AI-assisted business workflows with deterministic local rules, evidence, controls, reports, and optional localhost-only Ollama narrative support.")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    hero_cols = st.columns(4)
    cards = [
        ("home_card_no_cloud_title", "home_card_no_cloud_body", "local_only"),
        ("home_card_explainable_title", "home_card_explainable_body", "calculated"),
        ("home_card_evidence_title", "home_card_evidence_body", "detected"),
        ("home_card_exports_title", "home_card_exports_body", "recommended"),
    ]
    for column, (title_key, body_key, status) in zip(hero_cols, cards):
        with column:
            render_info_card(t(title_key, language), t(body_key, language), status=status, language=language)


def _render_findings(findings: list[dict[str, object]], language: str) -> None:
    if not findings:
        st.info(t("no_findings_explained", language, "No evidence findings were detected from the submitted workflow. This does not prove the workflow is safe."))
        return

    st.subheader(t("top_risks_title", language, "Top risks first"))
    st.caption(t("top_risks_caption", language, "The highest-severity findings are shown first. Each one includes evidence, the local rule, confidence, and a recommended action."))
    filter_col, category_col = st.columns(2)
    severity_choice = filter_col.selectbox(
        t("severity_filter", language, "Filter by severity"),
        _finding_filter_options(findings, "severity"),
        format_func=lambda value: translate_filter_option(value, language),
    )
    category_choice = category_col.selectbox(
        t("category_filter", language, "Filter by category"),
        _finding_filter_options(findings, "category"),
        format_func=lambda value: translate_filter_option(value, language),
    )
    filtered = [
        finding
        for finding in sorted_findings(findings)
        if (severity_choice == "all" or str(finding.get("severity", "unknown")) == severity_choice)
        and (category_choice == "all" or str(finding.get("category", "unknown")) == category_choice)
    ]
    st.caption(
        t(
            "findings_count_explained",
            language,
            "Findings are attention points detected in the text. They are not proof by themselves.",
        )
        + " "
        + format_showing_results(min(len(filtered), 5), len(filtered), language)
    )
    for index, finding in enumerate(filtered[:5], start=1):
        severity = translate_severity(finding.get("severity", "medium"), language)
        category = translate_category(finding.get("category", "general"), language)
        evidence = str(finding.get("matched_text_evidence", ""))
        controls = ", ".join(str(item) for item in finding.get("recommended_controls", [])[:3])
        with st.expander(f"{index}. {severity} {category} - {t('badge_detected', language, 'Detected in text')}", expanded=index <= 3):
            st.write(
                t(
                    "finding_plain_sentence",
                    language,
                    "The workflow may be risky because this evidence matched a local rule. A human should confirm whether it matters.",
                )
            )
            st.markdown(f"**{t('evidence_label', language, 'Evidence')}**: {evidence}")
            st.markdown(f"**{t('rule_used_label', language, 'Rule used')}**: `{finding.get('matched_rule_id', '')}`")
            st.markdown(f"**{t('severity_label', language, 'Severity')}**: {severity}")
            st.markdown(f"**{t('confidence_label', language, 'Confidence')}**: {finding.get('confidence', '')} ({t('badge_uncertain', language, 'Uncertain until human review')})")
            if controls:
                st.markdown(f"**{t('recommended_action_label', language, 'Recommended action')}**: {controls}")
    with st.expander(t("all_findings_table_title", language, "View matching findings"), expanded=False):
        st.dataframe(
            [
                {
                    t("severity_label", language, "Severity"): translate_severity(item.get("severity"), language),
                    t("category_label", language, "Category"): translate_category(item.get("category"), language),
                    t("evidence_label", language, "Evidence"): item.get("matched_text_evidence"),
                    t("rule_used_label", language, "Rule used"): item.get("matched_rule_id"),
                    t("confidence_label", language, "Confidence"): item.get("confidence"),
                }
                for item in filtered
            ],
            width="stretch",
            hide_index=True,
        )


def _current_project_id(language: str) -> int:
    projects = list_projects()
    project_options = {f"{project['name']} #{project['id']}": int(project["id"]) for project in projects}
    project_options[t("new_project_option", language, "New local project")] = 0
    selected = st.sidebar.selectbox(t("project_selector", language, "Project"), list(project_options.keys()))
    selected_id = project_options[selected]
    if selected_id:
        return selected_id
    name = st.sidebar.text_input(t("new_project_name", language, "New project name"), value="Local Workflow Review")
    if st.sidebar.button(t("create_project_button", language, "Create Project")):
        return create_project(name, "User-created local project.", is_demo=False)
    return int(projects[0]["id"]) if projects else create_project("Local Workflow Review")


def _run_enrichment(workflow_text: str, analysis: dict[str, object], language: str, model_name: str) -> str | None:
    status = check_ollama_status()
    if not status["available"]:
        st.info(f"{t('ollama_fallback_used', language)} {status.get('message', '')}")
        return None

    local_models = [str(name) for name in status.get("models", [])]
    cloud_models = [str(name) for name in status.get("cloud_models", [])]
    selected_model = model_name.strip() or "llama3"
    if is_cloud_or_proxy_model(selected_model) or selected_model in cloud_models:
        st.warning(t("ollama_cloud_model_blocked", language, "Cloud/proxy-like model names were detected. Local-only deterministic fallback was used."))
        return None
    if not local_models:
        st.info(t("ollama_no_local_models", language, "Ollama is reachable, but no local-only models were listed. Deterministic report was used."))
        return None
    if selected_model not in local_models:
        st.info(t("ollama_model_missing", language, "Ollama is reachable, but the selected model is not installed. Deterministic report was used."))
        return None

    enrichment = generate_enrichment(
        workflow_text=workflow_text,
        analysis=analysis,
        language_name=str(available_languages()[language]["name"]),
        model=selected_model,
    )
    if enrichment:
        st.info(t("ollama_enrichment_used", language))
    else:
        st.info(t("ollama_enrichment_failed", language))
    return enrichment


def _save_current_report(language: str, project_id: int, workflow_text: str, scenario_label: str, source: str) -> None:
    analysis = st.session_state.get("analysis")
    if not analysis or not analysis.get("valid"):
        st.warning(t("empty_input_warning", language))
        return

    workflow_id = save_workflow(
        project_id=project_id,
        name=scenario_label,
        workflow_text=workflow_text,
        source=source,
        is_demo=source != "user",
    )
    save_workflow_steps(workflow_id, [str(step) for step in analysis.get("steps", [])])
    assessment_id = save_assessment(project_id, workflow_id, analysis)
    save_findings(assessment_id, list(analysis.get("findings", [])))
    save_recommended_controls(assessment_id, list(analysis.get("recommended_controls", [])))

    simulation = st.session_state.get("simulation")
    if simulation:
        save_simulation_run(assessment_id, simulation)

    audit_trail = load_audit_trail(limit=10)
    markdown = render_markdown_report(
        analysis,
        language=language,
        enrichment=st.session_state.get("enrichment"),
        simulation=simulation,
        audit_trail=audit_trail,
    )
    json_summary = render_json_summary(analysis, simulation, language=language)
    report_id = save_report(
        assessment_id=assessment_id,
        project_id=project_id,
        title="AI Workflow Risk Auditor Pro Report",
        markdown=markdown,
        json_summary=json_summary,
    )
    st.session_state["assessment_id"] = assessment_id
    st.session_state["report_id"] = report_id
    st.session_state["report_markdown"] = markdown
    st.success(f"{t('report_saved_success', language, 'Report saved locally.')} #{report_id}")


language = _language_selector()
theme_mode = _theme_selector(language)
rtl = is_rtl(language)
apply_global_styles(language, resolved_theme(theme_mode))

if rtl:
    st.markdown(
        """
        <style>
        textarea, input { direction: rtl; text-align: right; }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.sidebar.header(t("sidebar_title", language))
project_id = _current_project_id(language)
demo_guidance = st.sidebar.toggle(t("guided_demo_toggle", language, "Guided demo mode"), value=False)

scenario_options = _scenario_options(language)
scenario_labels = [label for _, label, _ in scenario_options]
selected_label = st.sidebar.selectbox(t("example_selector", language), scenario_labels)
selected_key, scenario_label, selected_text = scenario_options[scenario_labels.index(selected_label)]
source = "user"
if selected_key.startswith("example:"):
    source = "v1_example"
elif selected_key.startswith("demo:"):
    source = "demo"

use_ollama = st.sidebar.toggle(t("ollama_toggle", language), value=False)
model_name = "llama3"

if use_ollama:
    status = check_ollama_status()
    if status["available"]:
        local_models = [str(name) for name in status.get("models", [])]
        cloud_models = [str(name) for name in status.get("cloud_models", [])]
        if local_models:
            default_index = local_models.index("llama3") if "llama3" in local_models else 0
            model_name = st.sidebar.selectbox(
                t("ollama_model", language),
                local_models,
                index=default_index,
            )
            st.sidebar.success(f"{t('ollama_available', language)} {', '.join(local_models[:5])}")
        else:
            model_name = st.sidebar.text_input(t("ollama_model", language), value="llama3")
            st.sidebar.info(t("ollama_no_local_models", language, "Ollama is reachable, but no local-only models were listed."))
        if cloud_models:
            st.sidebar.warning(
                t(
                    "ollama_cloud_models_detected",
                    language,
                    "Cloud/proxy-like Ollama models were detected and are blocked for local-only enrichment.",
                )
            )
    else:
        st.sidebar.info(f"{t('ollama_unavailable', language)} {status.get('message', '')}")
else:
    st.sidebar.caption(t("ollama_disabled", language))

st.sidebar.caption(t("reset_demo_db_warning", language, "Reset deletes saved local reports and recreates synthetic seed data."))
confirm_reset = st.sidebar.checkbox(t("reset_demo_db_confirm", language, "I understand this deletes saved local reports."))
if st.sidebar.button(t("reset_demo_db_button", language, "Reset demo database"), disabled=not confirm_reset):
    reset_demo_db()
    st.sidebar.success(t("demo_db_reset_success", language, "Demo database reset with synthetic seed data."))

st.sidebar.caption(t("project_status", language))

st.title(t("product_title", language, "AI Workflow Risk Auditor Pro"))
_render_product_hero(language)
st.write(t("app_pitch", language))
st.warning(t("privacy_warning", language))
st.info(one_minute_explanation(language))
st.caption(score_disclaimer(language))
_show_simple_legend(language)

start_col, local_col, next_col = st.columns(3)
with start_col:
    st.markdown(f"#### {t('start_here_title', language, 'Start here')}")
    st.caption(t("start_here_body", language, "Choose a synthetic example or paste an anonymized workflow, then run the audit."))
with local_col:
    st.markdown(f"#### {t('local_privacy_title', language, 'What stays local')}")
    st.caption(t("local_privacy_body", language, "Analysis runs locally. User workflow text is saved only when you click the local save button."))
with next_col:
    st.markdown(f"#### {t('next_after_analysis_title', language, 'After analysis')}")
    st.caption(t("next_after_analysis_body", language, "Review evidence, simulate controls, save intentionally, then download Markdown or JSON."))

if demo_guidance:
    with st.sidebar.expander(t("demo_steps_title", language, "5-minute demo flow"), expanded=False):
        for step in get_demo_steps():
            st.caption(step)

tab_audit, tab_simulation, tab_dashboard, tab_reports, tab_kb, tab_local_ai = st.tabs(
    [
        t("tab_audit", language, "Audit"),
        t("tab_simulation", language, "Simulation"),
        t("tab_dashboard", language, "Dashboard"),
        t("tab_reports", language, "Reports"),
        t("tab_knowledge_base", language, "Knowledge Base"),
        t("tab_local_ai", language, "Local AI / Ollama"),
    ]
)

with tab_audit:
    if demo_guidance:
        _show_explanation("local_first")

    default_text = "" if selected_key == "custom" else selected_text
    st.caption(t("workflow_input_help", language, "Use synthetic or anonymized text. Analysis does not save this workflow until you explicitly save a report."))
    workflow_text = st.text_area(
        t("workflow_input_label", language),
        value=default_text,
        height=240,
        placeholder=t("workflow_input_placeholder", language),
        key=f"workflow_text_{language}_{selected_key}",
    )
    st.session_state["last_workflow_text"] = workflow_text

    analyze = st.button(t("analyze_button", language), type="primary")
    if analyze:
        analysis = analyze_workflow(workflow_text)
        if not analysis["valid"]:
            st.warning(t("empty_input_warning", language))
        else:
            enrichment = _run_enrichment(workflow_text, analysis, language, model_name) if use_ollama else None
            st.session_state["analysis"] = analysis
            st.session_state["enrichment"] = enrichment
            st.session_state["simulation"] = None
            st.session_state["report_markdown"] = render_markdown_report(
                analysis,
                language=language,
                enrichment=enrichment,
            )

    analysis = st.session_state.get("analysis")
    if analysis and analysis.get("valid"):
        risk = analysis["risk"]
        matrix = analysis.get("risk_matrix", {})
        explainability = build_explainability_payload(analysis, st.session_state.get("simulation"), language)
        score_summary = explainability["score_summary"]
        score_col, level_col, finding_col = st.columns(3)
        with score_col:
            render_metric_card(
                t("residual_indicator_label", language, "Raw risk indicator"),
                f"{score_summary['score']} {t('score_point_unit', language, 'score point(s)')}",
                t("score_metric_source", language, "Calculated from local deterministic rules and detected workflow evidence."),
                explainability["score_explanation_simple"],
                score_disclaimer(language),
                status="calculated",
                language=language,
            )
        with level_col:
            render_metric_card(
                t("label_risk_level", language),
                score_summary["level_label"],
                t("risk_level_metric_source", language, "Mapped from fixed local score thresholds."),
                score_summary["scale"],
                t("risk_level_metric_limit", language, "Severity is an advisory review priority, not a compliance result."),
                status="calculated",
                language=language,
            )
        with finding_col:
            render_metric_card(
                t("finding_count_label", language, "Findings"),
                f"{len(analysis.get('findings', []))} {t('finding_count_unit', language, 'detected item(s)')}",
                t("finding_metric_source", language, "Detected from local text evidence and rule matches."),
                t("finding_metric_explanation", language, "Attention points detected in the text; not proof by themselves."),
                t("finding_metric_limit", language, "A human must confirm whether each finding matters."),
                status="detected",
                language=language,
            )

        st.info(t("after_analysis_summary", language, "The score and findings came from local deterministic rules. Review the evidence, simulate controls, then save only if you want local history."))
        st.caption(score_disclaimer(language))
        st.caption(
            f"{t('raw_matrix_caption', language, 'Raw matrix risk')}: "
            f"{matrix.get('raw_risk_score', risk['score'])} / {translate_severity(matrix.get('severity', risk['level']), language)}. "
            f"{t('raw_matrix_explanation_ui', language, 'Calculated by summing local risk-factor weights mapped from evidence.')}"
        )
        all_findings = list(analysis.get("findings", []))
        severity_counts = Counter(str(item.get("severity", "unknown")) for item in all_findings)
        if severity_counts:
            summary = ", ".join(
                f"{translate_severity(severity, language)}: {count}"
                for severity, count in sorted(severity_counts.items())
            )
            st.caption(f"{t('findings_summary_label', language, 'Findings summary')}: {summary}")

        simple_col, why_col = st.columns(2)
        with simple_col:
            st.subheader(t("simple_words_title", language, "In very simple words"))
            st.write(explainability["one_minute_explanation"])
            if explainability["top_risks"]:
                st.markdown(f"**{t('main_risk_label', language, 'Main risk')}**")
                st.write(explainability["top_risks"][0]["plain_language"])
        with why_col:
            st.subheader(t("what_score_means_title", language, "What this score means"))
            st.write(explainability["score_explanation_simple"])
            st.markdown(f"**{t('why_score_title', language, 'Why this score?')}**")
            for factor in score_summary["main_factors"]:
                st.caption(
                    f"{t('badge_calculated', language, 'Calculated by local rules')}: "
                    f"{factor['label']} +{factor['score_impact']} "
                    f"{format_count('evidence', factor['evidence_count'], language)}."
                )

        with st.expander(t("explain_like_12_title", language, "Simple explanation"), expanded=False):
            st.write(
                t(
                    "explain_like_12_body",
                    language,
                    "The app reviews the workflow against a deterministic local checklist. When it detects evidence such as customer data, external messages, or missing review, it adds local rule points. More points mean stronger human review is needed before automation.",
                )
            )
            st.write(t("human_responsibility_note", language, "A human remains responsible because the app can miss context and cannot know your real business obligations."))

        with st.expander(t("calculation_basis_title", language, "View calculation basis"), expanded=False):
            st.write(explainability["calculation_basis"]["formula"])
            st.write(score_summary["scale"])
            st.dataframe(explainability["calculation_basis"]["factors"], width="stretch", hide_index=True)

        _render_findings(all_findings, language)

        recommended = list(analysis.get("recommended_controls", []))
        if recommended:
            st.subheader(t("next_actions_title", language, "Top 3 actions"))
            for action in explainability["next_actions"]:
                st.markdown(f"**{t('badge_recommended', language, 'Recommended')}: {action['name']}**")
                st.caption(
                    f"{action['implementation']} "
                    f"{t('expected_effect_label', language, 'Expected effect')}: {action['expected_effect']}"
                )

        with st.expander(t("risk_matrix_title", language, "Risk Matrix")):
            st.dataframe(matrix.get("entries", []), width="stretch", hide_index=True)

        st.caption(t("export_save_hint", language, "Downloads are available immediately. Local history is created only after you click Save."))
        st.download_button(
            label=t("download_button", language),
            data=st.session_state["report_markdown"],
            file_name="ai_workflow_risk_auditor_pro_report.md",
            mime="text/markdown",
        )
        st.download_button(
            label=t("download_json_button", language, "Download JSON summary"),
            data=render_json_summary(analysis, st.session_state.get("simulation"), language=language),
            file_name="ai_workflow_risk_auditor_pro_summary.json",
            mime="application/json",
        )
        if st.button(t("save_report_button", language, "Save analysis and report locally")):
            _save_current_report(language, project_id, workflow_text, scenario_label, source)
    else:
        st.caption(t("ready_hint", language))

with tab_simulation:
    _show_explanation("residual_risk")
    analysis = st.session_state.get("analysis")
    if not analysis or not analysis.get("valid"):
        st.info(t("run_audit_first", language, "Run an audit before simulating residual risk."))
    else:
        controls = list(analysis.get("recommended_controls", []))
        if not controls:
            st.info(t("no_controls_for_simulation", language, "No controls were mapped from the current evidence."))
        else:
            names_by_id = {control["id"]: control["name"] for control in controls}
            default_ids = default_control_selection(controls)
            selected_names = st.multiselect(
                t("control_selector", language, "Select controls to simulate"),
                options=[control["name"] for control in controls],
                default=[names_by_id[control_id] for control_id in default_ids if control_id in names_by_id],
            )
            selected_ids = [control["id"] for control in controls if control["name"] in selected_names]
            if st.button(t("simulate_button", language, "Simulate residual risk"), type="primary"):
                st.session_state["simulation"] = simulate_residual_risk(
                    analysis["risk_matrix"],
                    selected_control_ids=selected_ids,
                    controls=controls,
                )
                st.session_state["report_markdown"] = render_markdown_report(
                    analysis,
                    language=language,
                    enrichment=st.session_state.get("enrichment"),
                    simulation=st.session_state["simulation"],
                )
            simulation = st.session_state.get("simulation")
            if simulation:
                simulation_explainability = build_explainability_payload(analysis, simulation, language)
                raw_col, residual_col, reduction_col = st.columns(3)
                raw_col.metric(
                    t("raw_risk_metric", language, "Raw risk"),
                    f"{simulation['raw_risk']['score']} / {translate_severity(simulation['raw_risk']['severity'], language)}",
                )
                raw_col.caption(t("raw_risk_metric_help", language, "Calculated local rule score before selected protections."))
                residual_col.metric(
                    t("residual_risk_metric", language, "Residual risk"),
                    f"{simulation['residual_risk']['score']} / {translate_severity(simulation['residual_risk']['severity'], language)}",
                )
                residual_col.caption(t("residual_risk_metric_help", language, "Simulated remaining score after selected protections. Not a guarantee."))
                reduction_col.metric(t("reduction_metric", language, "Reduction"), f"-{simulation['score_reduction']}")
                reduction_col.caption(t("reduction_metric_help", language, "Simulated reduction from mapped control effects only."))
                st.caption(simulation_explainability["simulation_explanation"]["summary"])
                st.write(t("simulation_local_explanation_report", language, "Residual risk is a local simulation based on mapped control effects. It does not execute actions or guarantee production risk reduction."))
                st.dataframe(
                    [
                        {
                            t("factor_label", language, "Factor"): t(f"factor_{item.get('factor')}", language, humanize_key(item.get("factor"))),
                            t("remaining_score_label", language, "Remaining score"): item.get("remaining_score"),
                        }
                        for item in simulation["remaining_risks"]
                    ],
                    width="stretch",
                    hide_index=True,
                )
                if st.session_state.get("assessment_id"):
                    if st.button(t("save_simulation_button", language, "Save simulation run")):
                        save_simulation_run(int(st.session_state["assessment_id"]), simulation)
                        st.success(t("simulation_saved_success", language, "Simulation saved locally."))
                else:
                    st.caption(
                        t(
                            "save_analysis_before_simulation",
                            language,
                            "Save the analysis first if you want this simulation in history.",
                        )
                    )

with tab_dashboard:
    _show_explanation("risk_score")
    metrics = load_dashboard_metrics()
    current_analysis = st.session_state.get("analysis")
    current_findings = _current_findings()
    render_how_to_read_panel(
        language,
        "dashboard_how_to_read",
        "Use Overview for saved local audit signals, Risks for heatmap and evidence, Controls for follow-up items, and History for local audit events.",
    )
    st.caption(t("dashboard_help", language, "Dashboard metrics are built only from reports you intentionally saved in local SQLite."))
    if metrics["saved_analyses"] == 0:
        render_empty_state(
            t("dashboard_empty_title", language, "No saved audits yet"),
            t("dashboard_empty_state", language, "No saved audits yet. Run an audit, save the report locally, then return here to see metrics."),
            t("dashboard_empty_action", language, "You can still inspect the current unsaved analysis if one is open."),
        )
    elif metrics["saved_analyses"] < 3:
        st.warning(
            t(
                "dashboard_small_sample_warning",
                language,
                "This dashboard is based on very few saved reports. Treat averages as orientation, not trend evidence.",
            )
        )
    st.caption(
        t("dashboard_sample_basis", language, "Average based on saved reports in local SQLite.")
        + " "
        + t(
            "dashboard_sample_counts",
            language,
            "{saved} saved report(s): {user_saved} user-saved, {demo_saved} demo/sample.",
        ).format(
            saved=metrics["saved_analyses"],
            user_saved=metrics.get("user_saved_analyses", 0),
            demo_saved=metrics.get("demo_saved_analyses", 0),
        )
    )

    dashboard_overview, dashboard_risks, dashboard_controls, dashboard_history = st.tabs(
        [
            t("dashboard_view_overview", language, "Overview"),
            t("dashboard_view_risks", language, "Risks & Evidence"),
            t("dashboard_view_controls", language, "Controls"),
            t("dashboard_view_history", language, "History"),
        ]
    )

    with dashboard_overview:
        render_section_header(
            t("dashboard_section_executive_overview", language, "Executive overview"),
            t("dashboard_section_executive_overview_subtitle", language, "Current posture, evidence volume, local-only status, report readiness, and residual simulation state."),
            "calculated",
            language,
        )
        _render_dashboard_executive_overview(metrics, current_analysis, current_findings, language)
        metric_cols = st.columns(4)
        with metric_cols[0]:
            render_metric_card(
                t("dashboard_saved_analyses", language, "Saved analyses"),
                f"{metrics['saved_analyses']} {t('saved_report_unit', language, 'local report(s)')}",
                t("dashboard_saved_analyses_help", language, "Reports intentionally saved locally."),
                t("dashboard_saved_analyses_meaning", language, "Shows how much local history is available for this dashboard."),
                t("dashboard_saved_analyses_limit", language, "Unsaved analyses are not included in saved-history metrics."),
                "local_only",
                language,
            )
        with metric_cols[1]:
            render_metric_card(
                t("dashboard_average_risk", language, "Average raw risk"),
                f"{metrics['average_risk']} {t('score_point_unit', language, 'score point(s)')}",
                t("dashboard_average_risk_help", language, "Mean raw deterministic score, not a statistical trend."),
                t("dashboard_average_risk_meaning", language, "Higher values suggest more review effort in saved local audits."),
                t("dashboard_average_risk_limit", language, "This average is indicative and can be misleading with few reports."),
                "calculated",
                language,
            )
        with metric_cols[2]:
            render_metric_card(
                t("dashboard_simulations", language, "Simulations"),
                f"{metrics['simulation_count']} {t('simulation_unit', language, 'saved run(s)')}",
                t("dashboard_simulations_help", language, "Residual-risk simulations saved locally."),
                t("dashboard_simulations_meaning", language, "Shows how often recommended controls were simulated."),
                t("dashboard_simulations_limit", language, "Simulations are planning estimates, not implemented remediation."),
                "simulated",
                language,
            )
        with metric_cols[3]:
            render_metric_card(
                t("dashboard_average_reduction", language, "Average reduction"),
                f"{metrics['average_simulated_reduction']} {t('score_point_unit', language, 'score point(s)')}",
                t("dashboard_average_reduction_help", language, "Mean simulated reduction from selected controls."),
                t("dashboard_average_reduction_meaning", language, "Shows expected reduction from saved control simulations."),
                t("dashboard_average_reduction_limit", language, "It does not prove a control was applied in production."),
                "simulated",
                language,
            )
        render_section_header(
            t("dashboard_workflow_graph_title", language, "Local audit pipeline"),
            t("dashboard_workflow_graph_subtitle", language, "A product map of how the app interprets workflow text locally."),
            "local_only",
            language,
        )
        render_workflow_graph(language)
        render_accessibility_note(language)

    with dashboard_risks:
        render_section_header(
            t("dashboard_section_risk_posture", language, "Risk posture"),
            t("dashboard_section_risk_posture_subtitle", language, "Severity distribution and impact context from current or saved local evidence."),
            "calculated",
            language,
        )
        render_section_header(
            t("dashboard_heatmap_title", language, "Risk heatmap"),
            t("dashboard_heatmap_subtitle", language, "Text-first category by severity view. Counts come from the current analysis when available, otherwise saved local findings."),
            "detected",
            language,
        )
        heatmap_source = current_findings if current_findings else list(metrics.get("finding_heatmap", []))
        render_heatmap(heatmap_source, language)
        render_section_header(
            t("dashboard_matrix_title", language, "Impact / likelihood matrix"),
            t("dashboard_matrix_subtitle", language, "Uses current analysis matrix entries when available. Saved history does not store a full matrix reconstruction."),
            "calculated",
            language,
        )
        if isinstance(current_analysis, dict) and current_analysis.get("valid"):
            matrix = current_analysis.get("risk_matrix", {})
            matrix_entries = matrix.get("entries", []) if isinstance(matrix, dict) else []
            render_risk_matrix([item for item in matrix_entries if isinstance(item, dict)], language)
        else:
            render_empty_state(
                t("matrix_current_empty_title", language, "No current matrix loaded"),
                t("matrix_current_empty_body", language, "Run an audit in this session to inspect impact and likelihood cells. Saved dashboard history keeps aggregate counts only."),
            )
        render_section_header(
            t("dashboard_section_findings_evidence", language, "Findings and evidence"),
            t("dashboard_section_findings_evidence_subtitle", language, "Localized filters, evidence cards, source phrases, and advisory limits."),
            "detected",
            language,
        )
        render_section_header(
            t("dashboard_evidence_title", language, "Evidence drill-down"),
            t("dashboard_evidence_subtitle", language, "Open one detected risk to see source phrase, rule, confidence, recommended control, and limit."),
            "detected",
            language,
        )
        if current_findings:
            labels = [
                f"{index}. {translate_severity(item.get('severity'), language)} / {translate_category(item.get('category'), language)}: {str(item.get('matched_text_evidence', ''))[:70]}"
                for index, item in enumerate(sorted_findings(current_findings), start=1)
            ]
            selected_finding_label = st.selectbox(t("evidence_selector_label", language, "Finding to inspect"), labels)
            selected_index = labels.index(selected_finding_label)
            render_evidence_card(sorted_findings(current_findings)[selected_index], selected_index + 1, language)
            with st.expander(t("all_findings_table_title", language, "View matching findings"), expanded=False):
                columns = _translate_column_map(language)
                st.dataframe(
                    [
                        {
                            columns["severity"]: translate_severity(item.get("severity"), language),
                            columns["category"]: _category_label(item.get("category"), language),
                            columns["evidence"]: item.get("matched_text_evidence"),
                            columns["rule"]: item.get("matched_rule_id"),
                            columns["confidence"]: item.get("confidence"),
                        }
                        for item in sorted_findings(current_findings)
                    ],
                    width="stretch",
                    hide_index=True,
                )
        else:
            render_empty_state(
                t("evidence_empty_title", language, "No current evidence to inspect"),
                t("evidence_empty_body", language, "Run an audit first. Saved aggregate metrics do not expose full source phrases in this dashboard panel."),
            )

    with dashboard_controls:
        render_section_header(
            t("dashboard_section_controls_followup", language, "Controls and follow-up"),
            t("dashboard_section_controls_followup_subtitle", language, "Advisory checklist, follow-up items, and top controls without production-ticket claims."),
            "recommended",
            language,
        )
        st.warning(
            t(
                "local_issue_tracker_notice",
                language,
                "These are local audit follow-up items generated from findings. They are not production tickets and do not prove that remediation was applied.",
            )
        )
        render_section_header(
            t("issue_tracker_title", language, "Local follow-up items"),
            t("issue_tracker_subtitle", language, "A lightweight local checklist generated from current findings, not a Jira or production tracker."),
            "recommended",
            language,
        )
        issues = _build_local_issues(current_findings, language)
        if issues:
            for issue in issues:
                render_issue_card(issue, language)
        else:
            render_empty_state(
                t("issue_tracker_empty_title", language, "No local follow-up items yet"),
                t("issue_tracker_empty_body", language, "Run an audit with findings to generate advisory local follow-up items."),
            )
        render_section_header(
            t("control_checklist_title", language, "Control checklist"),
            t("control_checklist_subtitle", language, "Advisory control-readiness view. It does not prove implementation."),
            "needs_human_review",
            language,
        )
        if isinstance(current_analysis, dict) and current_analysis.get("valid"):
            st.dataframe(_build_control_checklist(current_analysis, language), width="stretch", hide_index=True)
        else:
            render_empty_state(
                t("control_checklist_empty_title", language, "No current checklist"),
                t("control_checklist_empty_body", language, "Run an audit to generate a control checklist from local findings and recommendations."),
            )
        render_section_header(
            t("dashboard_top_controls", language, "Top controls"),
            t("dashboard_top_controls_subtitle", language, "Most frequently recommended controls in saved local reports."),
            "recommended",
            language,
        )
        if metrics["top_recommended_controls"]:
            st.dataframe(metrics["top_recommended_controls"], width="stretch", hide_index=True)
        else:
            render_empty_state(
                t("top_controls_empty_title", language, "No saved controls yet"),
                t("top_controls_empty_body", language, "Save audits with findings to build a local control frequency summary."),
            )

    with dashboard_history:
        render_section_header(
            t("dashboard_section_local_history", language, "Local history"),
            t("dashboard_section_local_history_subtitle", language, "Saved reports, timeline events, and trends stored in local SQLite only."),
            "local_only",
            language,
        )
        render_section_header(
            t("timeline_title", language, "Local audit timeline"),
            t("timeline_subtitle", language, "SQLite audit events created by explicit local actions."),
            "local_only",
            language,
        )
        if metrics.get("latest_audit_at"):
            render_info_card(
                t("last_audit_timestamp_label", language, "Last saved audit timestamp"),
                str(metrics["latest_audit_at"]),
                "local_only",
                language,
            )
        render_timeline(load_audit_trail(limit=12), language)
        with st.expander(t("dashboard_latest_reports", language, "Latest reports"), expanded=False):
            st.dataframe(metrics["latest_reports"], width="stretch", hide_index=True)
        with st.expander(t("dashboard_risk_trend", language, "Risk trend"), expanded=False):
            st.caption(t("dashboard_metric_note", language, "Average raw risk uses deterministic matrix scores. Average reduction uses saved residual-risk simulations."))
            st.dataframe(metrics["risk_trend"], width="stretch", hide_index=True)

with tab_reports:
    _show_explanation("auditability")
    render_how_to_read_panel(
        language,
        "reports_how_to_read",
        "Markdown is the human-readable deterministic report. JSON keeps stable technical keys for export while explanatory values remain localized where supported.",
    )
    reports = load_report_history()
    if not reports:
        render_empty_state(
            t("reports_empty_title", language, "No saved reports yet"),
            t("no_reports_saved", language, "No reports saved yet. Save from the Audit tab after analysis."),
        )
    else:
        labels = [f"#{report['id']} {report['title']} ({report['created_at']})" for report in reports]
        selected_report_label = st.selectbox(t("report_selector", language, "Saved report"), labels)
        report_id = int(selected_report_label.split()[0].lstrip("#"))
        report = open_report(report_id)
        if report:
            render_info_card(
                t("reports_deterministic_notice_title", language, "Deterministic report preview"),
                t(
                    "reports_deterministic_notice_body",
                    language,
                    "The saved report is generated from local deterministic analysis. Optional local AI narrative may appear only as wording assistance and does not change scores.",
                ),
                "calculated",
                language,
            )
            markdown_preview, json_preview = st.tabs(
                [
                    t("reports_markdown_preview", language, "Markdown preview"),
                    t("reports_json_preview", language, "JSON export preview"),
                ]
            )
            with markdown_preview:
                st.markdown(markdown_to_html(str(report["markdown"]), language=language), unsafe_allow_html=True)
                st.download_button(
                    t("download_button", language),
                    data=str(report["markdown"]),
                    file_name=f"aiwra_pro_report_{report_id}.md",
                    mime="text/markdown",
                )
            with json_preview:
                st.caption(t("reports_json_notice", language, "JSON keeps stable English technical keys for automation; explanatory fields may be localized."))
                st.code(str(report["json_summary"]), language="json")
                st.download_button(
                    t("download_json_button", language, "Download JSON summary"),
                    data=str(report["json_summary"]),
                    file_name=f"aiwra_pro_summary_{report_id}.json",
                    mime="application/json",
                )
    with st.expander(t("audit_trail_title", language, "Local audit trail")):
        st.dataframe(load_audit_trail(), width="stretch", hide_index=True)

with tab_kb:
    _show_explanation("knowledge_base")
    render_read_only_notice(language)
    counts = knowledge_counts()
    count_cols = st.columns(5)
    kb_count_cards = [
        ("kb_risk_patterns_title", counts["risk_patterns"], "risk_patterns"),
        ("kb_controls_title", counts["control_library"], "control_library"),
        ("kb_data_categories_title", counts["data_categories"], "data_categories"),
        ("kb_demo_scenarios_title", counts["demo_scenarios"], "demo_scenarios"),
        ("kb_explanation_cards_title", counts["explanation_cards"], "explanation_cards"),
    ]
    for column, (label_key, value, source_key) in zip(count_cols, kb_count_cards):
        with column:
            render_metric_card(
                t(label_key, language, humanize_key(source_key)),
                f"{value} {t('kb_item_unit', language, 'local item(s)')}",
                t("kb_metric_source", language, "Loaded from local JSON and local SQLite seed data."),
                t("kb_metric_meaning", language, "Shows the size of the read-only local rule library."),
                t("kb_metric_limit", language, "Counts do not imply coverage or certification."),
                "read_only",
                language,
            )
    search = st.text_input(t("knowledge_search", language, "Search local knowledge base"), value="")
    normalized_search = search.casefold().strip()

    kb_tabs = st.tabs(
        [
            t("kb_risk_patterns_title", language, "Risk patterns"),
            t("kb_controls_title", language, "Controls"),
            t("kb_data_categories_title", language, "Data categories"),
            t("kb_demo_scenarios_title", language, "Demo scenarios"),
            t("kb_explanation_cards_title", language, "Explanations"),
        ]
    )

    def _filter(items: list[dict[str, object]]) -> list[dict[str, object]]:
        if not normalized_search:
            return items
        return [item for item in items if normalized_search in str(item).casefold()]

    with kb_tabs[0]:
        patterns = _filter(load_risk_patterns())[:80]
        columns = _translate_column_map(language)
        st.dataframe(
            [
                {
                    columns["id"]: item["id"],
                    columns["status"]: t("kb_active_local_rule", language, "Active local rule"),
                    columns["category"]: _category_label(item["category"], language),
                    columns["severity"]: t(f"risk_level_{item['severity']}", language, str(item["severity"]).title()),
                    columns["topics"]: ", ".join(str(keyword) for keyword in item["keywords"][:4]),
                    columns["limit"]: t("kb_rule_limit", language, "Rule match is advisory and can miss context."),
                }
                for item in patterns
            ],
            width="stretch",
            hide_index=True,
        )
    with kb_tabs[1]:
        columns = _translate_column_map(language)
        st.dataframe(
            [
                {
                    columns["id"]: item["id"],
                    columns["status"]: t("kb_active_local_rule", language, "Active local rule"),
                    columns["name"]: item["name"],
                    columns["category"]: _category_label(item["category"], language),
                    t("column_effectiveness", language, "Effectiveness"): f"{item.get('effectiveness')} {t('score_point_unit', language, 'score point(s)')}",
                    columns["meaning"]: item.get("description", ""),
                    columns["limit"]: t("kb_control_limit", language, "Recommended control is not automatically applied."),
                }
                for item in _filter(load_control_library())[:100]
            ],
            width="stretch",
            hide_index=True,
        )
    with kb_tabs[2]:
        columns = _translate_column_map(language)
        st.dataframe(
            [
                {
                    columns["id"]: item["id"],
                    columns["name"]: item["name"],
                    columns["category"]: t("column_sensitivity", language, "Sensitivity"),
                    columns["meaning"]: item.get("privacy_notes", ""),
                    columns["limit"]: item.get("recommended_handling", ""),
                }
                for item in _filter(load_data_categories())
            ],
            width="stretch",
            hide_index=True,
        )
    with kb_tabs[3]:
        render_info_card(
            t("demo_scenarios_explainer_title", language, "What is a demo scenario?"),
            t(
                "demo_scenarios_explainer_body",
                language,
                "Demo scenarios are synthetic local examples for learning and screenshots. They are not user saved data and do not connect to production systems.",
            ),
            "demo",
            language,
        )
        scenario_categories = sorted({str(item.get("category", "unknown")) for item in load_demo_scenarios()})
        selected_category = st.selectbox(
            t("demo_category_filter", language, "Filter demo scenarios by category"),
            ["all"] + scenario_categories,
            format_func=lambda value: translate_filter_option(value, language),
        )
        scenarios = _filter(load_demo_scenarios())
        if selected_category != "all":
            scenarios = [item for item in scenarios if str(item.get("category", "")) == selected_category]
        for scenario in scenarios[:16]:
            with st.expander(str(scenario.get("name", scenario.get("id"))), expanded=False):
                col_status, col_source = st.columns(2)
                with col_status:
                    render_status_badge("demo", language)
                with col_source:
                    render_status_badge("read_only", language)
                st.write(str(scenario.get("workflow_text", "")))
                st.caption(
                    f"{t('category_label', language, 'Category')}: {_category_label(scenario.get('category'), language)} | "
                    f"{t('column_synthetic', language, 'Synthetic')}: {t('yes_label', language, 'Yes')}"
                )
                st.caption(str(scenario.get("demo_notes", "")))
    with kb_tabs[4]:
        columns = _translate_column_map(language)
        st.dataframe(
            [
                {
                    columns["id"]: item["id"],
                    columns["name"]: item["title"],
                    columns["category"]: item.get("related_ui_area", ""),
                    columns["meaning"]: item.get("short_explanation", ""),
                    columns["limit"]: item.get("why_it_matters", ""),
                }
                for item in _filter(load_explanation_cards())
            ],
            width="stretch",
            hide_index=True,
        )

with tab_local_ai:
    render_how_to_read_panel(
        language,
        "local_ai_how_to_read",
        "This page shows what Ollama can add locally, what it cannot add, and the exact prompt/response when a local model is used.",
    )
    status = check_ollama_status()
    local_models = [str(name) for name in status.get("models", [])]
    cloud_models = [str(name) for name in status.get("cloud_models", [])]
    availability = t("available_label", language, "Available") if status.get("available") else t("not_available_label", language, "Not available")

    ai_cols = st.columns(4)
    with ai_cols[0]:
        render_metric_card(
            t("local_ai_status_title", language, "Ollama status"),
            availability,
            t("local_ai_status_source", language, "Checked against the localhost Ollama tags endpoint."),
            str(status.get("message", "")),
            t("local_ai_status_limit", language, "If unavailable, the app remains fully deterministic."),
            "local_only" if status.get("available") else "not_available",
            language,
        )
    with ai_cols[1]:
        render_metric_card(
            t("local_ai_endpoint_title", language, "Endpoint"),
            DEFAULT_BASE_URL,
            t("local_ai_endpoint_source", language, "Hard-coded local-only default endpoint."),
            t("local_ai_endpoint_meaning", language, "Only localhost, 127.0.0.1, or ::1 endpoints are accepted by the client."),
            t("local_ai_endpoint_limit", language, "Remote endpoints are rejected and are not used as fallback."),
            "local_only",
            language,
        )
    with ai_cols[2]:
        render_metric_card(
            t("local_ai_models_title", language, "Local models"),
            f"{len(local_models)} {t('model_unit', language, 'model(s)')}",
            t("local_ai_models_source", language, "Listed from local Ollama only."),
            ", ".join(local_models[:4]) if local_models else t("ollama_no_local_models", language, "Ollama is reachable, but no local-only models were listed. Deterministic report was used."),
            t("local_ai_models_limit", language, "Model availability does not validate scores or findings."),
            "local_only" if local_models else "not_available",
            language,
        )
    with ai_cols[3]:
        render_metric_card(
            t("local_ai_cloud_block_title", language, "Cloud/proxy models"),
            f"{len(cloud_models)} {t('blocked_model_unit', language, 'blocked model(s)')}",
            t("local_ai_cloud_block_source", language, "Detected from model metadata or cloud-like names."),
            t("local_ai_cloud_block_meaning", language, "Cloud/proxy models are blocked for local-only enrichment."),
            t("local_ai_cloud_block_limit", language, "The app never falls back to a cloud model."),
            "local_only",
            language,
        )

    st.warning(
        t(
            "local_ai_score_guardrail",
            language,
            "Local AI output never changes deterministic findings, scores, controls, or residual-risk simulation.",
        )
    )
    local_ai_value, local_ai_limits = st.columns(2)
    with local_ai_value:
        render_section_header(t("local_ai_adds_title", language, "What local AI adds"), "", "local_only", language)
        st.markdown(
            "\n".join(
                f"- {item}"
                for item in [
                    t("local_ai_adds_narrative", language, "Local narrative drafting."),
                    t("local_ai_adds_explanation", language, "Optional explanation wording."),
                    t("local_ai_adds_synthetic", language, "Local-only synthetic test."),
                    t("local_ai_adds_wording", language, "Report wording assistance."),
                ]
            )
        )
    with local_ai_limits:
        render_section_header(t("local_ai_does_not_add_title", language, "What local AI does not add"), "", "uncertain", language)
        st.markdown(
            "\n".join(
                f"- {item}"
                for item in [
                    t("local_ai_no_scientific_validation", language, "Scientific validation."),
                    t("local_ai_no_certification", language, "Compliance certification."),
                    t("local_ai_no_score_authority", language, "Score authority."),
                    t("local_ai_no_cloud_analysis", language, "Cloud analysis."),
                    t("local_ai_no_remediation", language, "Automatic remediation."),
                ]
            )
        )

    language_name = str(available_languages()[language]["name"])
    selected_ai_model = "llama3"
    if local_models:
        default_index = local_models.index("llama3") if "llama3" in local_models else 0
        selected_ai_model = st.selectbox(
            t("local_ai_selected_model", language, "Selected local model"),
            local_models,
            index=default_index,
        )
    else:
        selected_ai_model = st.text_input(t("local_ai_selected_model", language, "Selected local model"), value="llama3")

    synthetic_prompt = build_synthetic_test_prompt(language_name)
    st.session_state.setdefault("local_ai_synthetic_response", None)
    render_section_header(
        t("local_ai_synthetic_test_title", language, "Run local synthetic AI test"),
        t("local_ai_synthetic_test_subtitle", language, "This test uses only synthetic text and shows the exact prompt before sending."),
        "local_only",
        language,
    )
    if st.button(t("local_ai_run_synthetic_test", language, "Run local synthetic AI test")):
        st.session_state["local_ai_synthetic_response"] = generate_local_prompt_response(
            synthetic_prompt,
            model=selected_ai_model,
        )
    render_ai_output_panel(
        synthetic_prompt,
        st.session_state.get("local_ai_synthetic_response"),
        t("local_ai_synthetic_deterministic_summary", language, "Deterministic audit remains available even if this synthetic local AI test is not run or fails."),
        language,
    )

    render_section_header(
        t("local_ai_current_report_title", language, "Generate local narrative for current report"),
        t("local_ai_current_report_subtitle", language, "Uses current workflow text only when you explicitly click the button and only with a listed local model."),
        "recommended",
        language,
    )
    current_analysis = st.session_state.get("analysis")
    if isinstance(current_analysis, dict) and current_analysis.get("valid"):
        current_prompt = build_enrichment_prompt(
            str(st.session_state.get("last_workflow_text", "")),
            current_analysis,
            language_name,
        )
        if st.button(t("local_ai_generate_current", language, "Generate local narrative for current report")):
            st.session_state["local_ai_current_response"] = generate_local_prompt_response(
                current_prompt,
                model=selected_ai_model,
            )
        explainability = build_explainability_payload(current_analysis, st.session_state.get("simulation"), language)
        render_ai_output_panel(
            current_prompt,
            st.session_state.get("local_ai_current_response"),
            explainability["score_explanation_simple"],
            language,
        )
    else:
        render_empty_state(
            t("local_ai_no_current_analysis_title", language, "No current deterministic analysis"),
            t("local_ai_no_current_analysis_body", language, "Run an audit first to generate an optional local narrative for the current report."),
        )
