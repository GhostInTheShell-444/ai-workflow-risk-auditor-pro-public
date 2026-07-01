from __future__ import annotations

import html
from typing import Any, Iterable

from i18n import format_count, is_rtl, t, translate_category, translate_severity
from score_explainability import build_explainability_payload, sorted_findings


def _translated_items(keys: Iterable[str], prefix: str, language: str) -> list[str]:
    return [t(f"{prefix}_{key}", language, key.replace("_", " ")) for key in keys]


def _append_list(lines: list[str], items: Iterable[str], language: str) -> None:
    item_list = list(items)
    if not item_list:
        lines.append(f"- {t('none_detected', language)}")
        return
    for item in item_list:
        lines.append(f"- {item}")


def _append_findings(lines: list[str], findings: list[dict[str, Any]], language: str) -> None:
    if not findings:
        lines.append(f"- {t('none_detected', language)}")
        return
    for finding in sorted_findings(findings)[:12]:
        evidence = str(finding.get("matched_text_evidence", "")).strip()
        rule = str(finding.get("matched_rule_id", "")).strip()
        controls = ", ".join(str(control) for control in finding.get("recommended_controls", [])[:3])
        lines.append(
            "- "
            f"[{t('badge_detected', language, 'Detected in text')}] "
            f"{translate_severity(finding.get('severity', 'medium'), language)} / "
            f"{translate_category(finding.get('category', 'general'), language)}: "
            f"{evidence} "
            f"({t('rule_used_label', language, 'Rule used')}: {rule}, "
            f"{t('confidence_label', language, 'Confidence')}: {finding.get('confidence', '')}, "
            f"{t('badge_uncertain', language, 'Uncertain until human review')})"
        )
        if controls:
            lines.append(f"  {t('recommended_controls_inline_label', language, 'Recommended controls')}: {controls}")
        if finding.get("why_it_matters"):
            lines.append(f"  {t('why_it_matters_label', language, 'Why it matters')}: {finding.get('why_it_matters')}")
        if finding.get("human_review_question"):
            lines.append(f"  {t('human_review_question_label', language, 'Human review question')}: {finding.get('human_review_question')}")
        if finding.get("residual_simulation_assumption"):
            lines.append(f"  {t('simulation_assumption_label', language, 'Residual simulation assumption')}: {finding.get('residual_simulation_assumption')}")
        if finding.get("limitation"):
            lines.append(f"  {t('limit_label', language, 'Limit')}: {finding.get('limitation')}")


def _append_risk_matrix(lines: list[str], matrix: dict[str, Any], language: str) -> None:
    entries = matrix.get("entries", [])
    if not entries:
        lines.append(f"- {t('none_detected', language)}")
        return
    for entry in entries:
        factor = str(entry.get("factor", ""))
        lines.append(
            "- "
            f"{t(f'factor_{factor}', language, factor.replace('_', ' '))}: "
            f"{t('likelihood_label', language, 'Likelihood')} {entry.get('likelihood')}, "
            f"{t('impact_label', language, 'Impact')} {entry.get('impact')}, "
            f"{t('confidence_label', language, 'Confidence')} {entry.get('confidence')}, "
            f"{t('score_impact_label', language, 'Score impact')} +{entry.get('score_impact')}"
        )


def _append_controls(lines: list[str], controls: list[dict[str, Any]], language: str) -> None:
    if not controls:
        lines.append(f"- {t('no_controls_mapped_report', language, 'No controls mapped from detected evidence.')}")
        return
    for control in controls[:12]:
        lines.append(
            f"- [{t('badge_recommended', language, 'Recommended')}] {control.get('name', control.get('id'))}: "
            f"{control.get('implementation_guidance', control.get('reason', ''))} "
            f"{t('expected_effect_label', language, 'Expected effect')}: "
            f"{t('control_expected_effect_short', language, 'may reduce mapped risk in simulation; not a guarantee.')}"
        )


def _append_validation_plan(lines: list[str], checkpoints: list[dict[str, Any]], language: str) -> None:
    if not checkpoints:
        lines.append(f"- {t('no_validation_checkpoint_report', language, 'No high-impact checkpoint was generated from the submitted workflow.')}")
        return
    for checkpoint in checkpoints[:10]:
        lines.append(
            f"- {checkpoint.get('responsible_role')}: {checkpoint.get('validation_moment')} "
            f"{t('evidence_label', language, 'Evidence')}: {checkpoint.get('linked_evidence')}"
        )


def render_markdown_report(
    analysis: dict[str, object],
    language: str = "en",
    enrichment: str | None = None,
    simulation: dict[str, Any] | None = None,
    audit_trail: list[dict[str, Any]] | None = None,
) -> str:
    if not analysis.get("valid"):
        return f"# {t('report_title', language)}\n\n{t('empty_input_warning', language)}\n"

    risk = analysis.get("risk", {})
    risk_dict = risk if isinstance(risk, dict) else {}
    level_key = str(risk_dict.get("level", "low"))
    level_label = t(f"risk_level_{level_key}", language)
    score = risk_dict.get("score", 0)
    breakdown = risk_dict.get("breakdown", [])
    automation = analysis.get("automation_opportunities", {})
    automation_dict = automation if isinstance(automation, dict) else {}

    findings = [item for item in analysis.get("findings", []) if isinstance(item, dict)]
    risk_matrix = analysis.get("risk_matrix", {})
    matrix_dict = risk_matrix if isinstance(risk_matrix, dict) else {}
    controls = [item for item in analysis.get("recommended_controls", []) if isinstance(item, dict)]
    checkpoints = [item for item in analysis.get("human_validation_plan", []) if isinstance(item, dict)]
    explainability = build_explainability_payload(analysis, simulation, language)
    score_summary = explainability["score_summary"]
    legend_lines = explainability["source_of_truth_labels"]

    lines: list[str] = [
        f"# {t('report_title', language)}",
        "",
        "AI Workflow Risk Auditor Pro",
        "",
        f"## {t('section_how_to_read', language, 'How to read this report')}",
        explainability["one_minute_explanation"],
        "",
        explainability["score_disclaimer"],
        "",
        f"### {t('section_simple_glossary', language, 'Simple glossary')}",
        *[f"- {item}" for item in legend_lines],
        "",
        f"## {t('section_one_minute_explanation', language, 'One-minute explanation')}",
        explainability["one_minute_explanation"],
        "",
        f"## {t('section_local_privacy_report', language, 'What is saved and what stays local')}",
        f"- {t('report_local_privacy_line_analysis', language, 'Analysis runs locally from the workflow text supplied in the app.')}",
        f"- {t('report_local_privacy_line_save', language, 'User workflow text is saved only after an explicit local save action.')}",
        f"- {t('report_local_privacy_line_sqlite', language, 'Saved workflows, assessments, simulations, and reports are stored in local SQLite.')}",
        f"- {t('report_local_privacy_line_no_cloud', language, 'The app does not require a cloud API and does not send workflow text to a cloud service.')}",
        f"- {t('report_local_privacy_line_ollama', language, 'Optional Ollama enrichment remains local-only and does not change deterministic scoring.')}",
        "",
        f"## {t('section_what_score_means', language, 'What this score means')}",
        f"{score_summary['score']} {t('score_means_label', language, 'means')}: {score_summary['simple']}",
        f"{t('scale_label', language, 'Scale')}: {score_summary['scale']}",
        explainability["score_disclaimer"],
        "",
        f"## {t('section_executive_summary', language, 'Executive Summary')}",
        t(
            "report_executive_summary_template",
            language,
            "Deterministic local audit result: {level} risk / {score}. {summary} The compatibility score is {compatibility}; the risk matrix raw score is {raw_score}.",
        ).format(
            level=score_summary["level_label"],
            score=score_summary["score"],
            summary=explainability["score_explanation_simple"],
            compatibility=score,
            raw_score=matrix_dict.get("raw_risk_score", score),
        ),
        "",
        f"## {t('section_workflow_overview', language, 'Workflow Overview')}",
        f"{t('workflow_type_label', language, 'Workflow type')}: {analysis.get('workflow_type', 'unknown')}",
        f"{t('detected_language_label', language, 'Detected language')}: {analysis.get('language_detected', 'unknown')}",
        "",
        f"## {t('section_workflow_summary', language)}",
        str(analysis.get("workflow_summary", "")),
        "",
    ]

    if enrichment:
        lines.extend([f"## {t('section_local_enrichment', language)}", enrichment.strip(), ""])

    lines.extend([f"## {t('section_what_detected', language, 'What is detected')}"])
    lines.append(
        "- "
        + t(
            "report_detected_count_template",
            language,
            "{count} findings were detected in the submitted text. Detected means the evidence appeared in the workflow text or matched a local pattern.",
        ).format(count=explainability["detected_evidence_count"])
    )
    for risk_item in explainability["top_risks"]:
        lines.append(
            f"- {risk_item['label']}: {risk_item['plain_language']} "
            f"Evidence: {risk_item['evidence']} Rule: {risk_item['rule']}."
        )
    lines.append("")

    lines.extend([f"## {t('section_what_calculated', language, 'What is calculated')}"])
    lines.append(f"- {t('label_score', language, 'Risk score')}: {score_summary['score']} / {score_summary['level_label']}. {score_summary['simple']}")
    lines.append(f"- {t('scale_label', language, 'Scale')}: {score_summary['scale']}")
    lines.append(f"- {t('basis_label', language, 'Basis')}: {explainability['calculation_basis']['formula']}")
    lines.append("")

    lines.extend([f"## {t('section_what_simulated', language, 'What is simulated')}"])
    lines.append(f"- {explainability['simulation_explanation']['summary']}")
    lines.append("")

    lines.extend([f"## {t('section_what_recommended', language, 'What is recommended')}"])
    if explainability["next_actions"]:
        for action in explainability["next_actions"]:
            lines.append(
                f"- {action['name']}: {action['implementation']} "
                f"{t('why_label', language, 'Why')}: {action['risk_reduced']}. "
                f"{t('status_label', language, 'Status')}: {action['required_or_advised']}."
            )
    else:
        lines.append(f"- {t('no_mapped_control_recommendation', language, 'No mapped control recommendation was generated from the detected evidence.')}")
    lines.append("")

    lines.extend([f"## {t('section_detected_steps', language)}"])
    _append_list(lines, [str(step) for step in analysis.get("steps", [])], language)
    lines.append("")

    lines.extend([f"## {t('section_automation_opportunities', language)}"])
    for group_key in ("good_candidates", "requires_approval", "poor_candidates", "guardrails"):
        lines.append(f"### {t(f'automation_group_{group_key}', language)}")
        items = _translated_items(automation_dict.get(group_key, []), "recommendation", language)
        _append_list(lines, items, language)
    lines.append("")

    lines.extend([f"## {t('section_sensitive_data', language)}"])
    _append_list(lines, _translated_items(analysis.get("sensitive_data", []), "category", language), language)
    lines.append("")

    lines.extend([f"## {t('section_cybersecurity_risks', language)}"])
    _append_list(lines, _translated_items(analysis.get("cybersecurity_risks", []), "cyber_risk", language), language)
    lines.append("")

    lines.extend([f"## {t('section_privacy_risks', language)}"])
    _append_list(lines, _translated_items(analysis.get("privacy_risks", []), "privacy_risk", language), language)
    lines.append("")

    lines.extend([f"## {t('section_human_checkpoints', language)}"])
    _append_list(lines, _translated_items(analysis.get("human_checkpoints", []), "checkpoint", language), language)
    lines.append("")

    lines.extend([f"## {t('section_detected_evidence', language, 'Detected Evidence')}"])
    _append_findings(lines, findings, language)
    lines.append("")

    lines.extend([f"## {t('section_risk_matrix', language, 'Risk Matrix')}"])
    lines.append(t("risk_matrix_report_explanation", language, "Raw risk is the deterministic sum of mapped factor weights. Likelihood and impact are explainable matrix attributes derived from evidence counts and factor weights."))
    _append_risk_matrix(lines, matrix_dict, language)
    lines.append("")

    matrix_severity = str(matrix_dict.get("severity", level_key))
    lines.extend(
        [
            f"## {t('section_raw_risk', language, 'Raw Risk')}",
            f"- {t('raw_matrix_score_label', language, 'Raw matrix score')}: {matrix_dict.get('raw_risk_score', score)}. {t('raw_matrix_score_explanation_report', language, 'This is calculated by summing local risk-factor weights mapped from evidence.')}",
            f"- {t('matrix_severity_label', language, 'Matrix severity')}: {translate_severity(matrix_severity, language)}. {t('severity_thresholds_sentence', language, 'Severity comes from fixed thresholds: low 0-4, medium 5-9, high 10-15, critical 16+.')}",
            f"- {t('compatibility_score_label', language, 'Compatibility score')}: {score}. {t('compatibility_score_explanation', language, 'This preserves the original deterministic analyzer score for compatibility.')}",
            f"- {t('compatibility_level_label', language, 'Compatibility level')}: {level_label}. {t('compatibility_level_explanation', language, 'Use the raw matrix score for the explainable report narrative.')}",
            "",
        ]
    )

    lines.extend(
        [
            f"## {t('section_risk_score', language)}",
            f"- {t('label_score', language)}: {score_summary['score']}. {score_summary['simple']}",
            f"- {t('label_risk_level', language)}: {score_summary['level_label']}. {score_summary['scale']}",
            "",
            f"## {t('section_score_explanation', language)}",
        ]
    )
    if breakdown:
        for item in breakdown:
            if not isinstance(item, dict):
                continue
            key = str(item.get("key", ""))
            weight = item.get("weight", 0)
            lines.append(f"- {t(f'factor_{key}', language, key.replace('_', ' '))}: +{weight}")
    else:
        lines.append(f"- {t('no_weighted_factors', language)}")
    lines.append("")

    lines.extend([f"## {t('section_score_basis', language, 'Score basis')}"])
    lines.append(explainability["score_disclaimer"])
    for factor in score_summary["main_factors"]:
        lines.append(
            f"- [{t('badge_calculated', language, 'Calculated by local rules')}] "
            f"{factor['label']}: +{factor['score_impact']} "
            f"{format_count('evidence', factor['evidence_count'], language)}."
        )
    lines.append("")

    lines.extend([f"## {t('section_top_3_risks', language, 'Top 3 risks')}"])
    if explainability["top_risks"]:
        for risk_item in explainability["top_risks"]:
            lines.append(
                f"- [{t('badge_detected', language, 'Detected in text')}] {risk_item['label']}: {risk_item['plain_language']} "
                f"{t('evidence_label', language, 'Evidence')}: {risk_item['evidence']} "
                f"{t('rule_used_label', language, 'Rule used')}: {risk_item['rule']}."
            )
    else:
        lines.append(f"- {t('none_detected', language)}")
    lines.append("")

    lines.extend([f"## {t('section_next_3_actions', language, 'Next 3 actions')}"])
    if explainability["next_actions"]:
        for action in explainability["next_actions"]:
            lines.append(
                f"- [{t('badge_recommended', language, 'Recommended')}] {action['name']}: {action['implementation']} "
                f"{t('expected_effect_label', language, 'Expected effect')}: {action['expected_effect']}"
            )
    else:
        lines.append(f"- {t('review_workflow_manually_report', language, 'Review the workflow manually and decide whether additional controls are needed.')}")
    lines.append("")

    lines.extend([f"## {t('section_recommended_safe_automation', language)}"])
    safe_recommendations = (
        _translated_items(automation_dict.get("good_candidates", []), "recommendation", language)
        + _translated_items(automation_dict.get("guardrails", []), "recommendation", language)
    )
    _append_list(lines, safe_recommendations, language)
    lines.append("")

    lines.extend([f"## {t('section_recommended_controls', language, 'Recommended Controls')}"])
    _append_controls(lines, controls, language)
    lines.append("")

    lines.extend([f"## {t('section_residual_risk_simulation', language, 'Residual Risk Simulation')}"])
    if simulation:
        raw = simulation.get("raw_risk", {})
        residual = simulation.get("residual_risk", {})
        lines.append(
            f"- [{t('badge_calculated', language, 'Calculated by local rules')}] "
            f"{t('raw_risk_metric', language, 'Raw risk')}: {translate_severity(raw.get('severity', 'low'), language)} / {raw.get('score', 0)}. "
            f"{t('raw_risk_metric_help', language, 'This is the local rule score before selected protections.')}"
        )
        selected_controls = simulation.get("selected_controls", [])
        if selected_controls:
            lines.append(f"- [{t('badge_recommended', language, 'Recommended')}] {t('selected_controls_label', language, 'Selected controls')}:")
            for control in selected_controls:
                lines.append(f"  - {control.get('name', control.get('id'))}")
                lines.append(f"    {t('simulation_assumption_label', language, 'Assumption')}: {control.get('assumption', '')}")
                lines.append(f"    {t('evidence_required_label', language, 'Evidence required')}: {control.get('evidence_required', '')}")
                lines.append(f"    {t('implementation_check_label', language, 'Implementation check')}: {control.get('implementation_check', '')}")
                lines.append(f"    {t('limit_label', language, 'Limit')}: {control.get('limitation', '')}")
                lines.append(f"    {t('not_proof_warning_label', language, 'Not proof of implementation')}: {control.get('not_proof_warning', '')}")
        lines.append(
            f"- [{t('badge_simulated', language, 'Simulated')}] "
            f"{t('residual_risk_metric', language, 'Residual risk')}: {translate_severity(residual.get('severity', 'low'), language)} / {residual.get('score', 0)}. "
            f"{t('residual_risk_metric_help', language, 'This is an estimated remaining score after selected protections, not a guarantee.')}"
        )
        lines.append(
            f"- [{t('badge_simulated', language, 'Simulated')}] "
            f"{t('reduction_metric', language, 'Reduction')}: -{simulation.get('score_reduction', 0)}. "
            f"{t('reduction_metric_help', language, 'This is calculated from mapped control effects only.')}"
        )
        lines.append(f"- {t('explanation_label', language, 'Explanation')}: {t('simulation_local_explanation_report', language, 'Residual risk is a local simulation based on mapped control effects. It does not execute actions or guarantee production risk reduction.')}")
        lines.append(f"- {t('human_review_required_label', language, 'Human review required')}: {simulation.get('human_review_required', True)}")
        lines.append(f"- {t('not_proof_warning_label', language, 'Not proof of implementation')}: {simulation.get('not_proof_warning', 'This simulation is not proof of implementation or assurance.')}")
    else:
        lines.append(f"- {t('no_residual_simulation_report', language, 'No residual simulation has been saved for this report. Simulation is local planning only.')}")
    lines.append("")

    lines.extend([f"## {t('section_human_validation_plan', language, 'Human Validation Plan')}"])
    _append_validation_plan(lines, checkpoints, language)
    lines.append("")

    lines.extend([f"## {t('section_implementation_roadmap', language, 'Implementation Roadmap')}"])
    roadmap = [
        t("roadmap_keep_local", language, "Keep analysis local and advisory."),
        t("roadmap_review_evidence", language, "Review evidence with the responsible business owner."),
        t("roadmap_document_residual", language, "Select controls and document residual risk assumptions."),
        t("roadmap_human_approval", language, "Require human approval before external, people-affecting, or irreversible steps."),
        t("roadmap_security_review", language, "Treat any future production integration as a separate security review."),
    ]
    _append_list(lines, roadmap, language)
    lines.append("")

    lines.extend([f"## {t('section_audit_trail', language, 'Audit Trail')}"])
    if audit_trail:
        for event in audit_trail[:10]:
            lines.append(
                f"- {event.get('created_at', '')}: {event.get('event_type', '')} "
                f"({event.get('entity_type', '')} #{event.get('entity_id', '')})"
            )
    else:
        lines.append(f"- {t('report_generated_locally_line', language, 'Report generated locally. Persistence occurs only after explicit save actions.')}")
    lines.append("")

    lines.extend([f"## {t('section_minimal_architecture', language)}"])
    _append_list(lines, _translated_items(analysis.get("minimal_architecture", []), "architecture", language), language)
    lines.append("")

    lines.extend([f"## {t('section_implementation_notes', language)}"])
    _append_list(lines, _translated_items(analysis.get("implementation_notes", []), "implementation", language), language)
    lines.append("")

    lines.extend([f"## {t('section_limitations', language)}"])
    _append_list(lines, _translated_items(analysis.get("limitations", []), "limitation", language), language)
    for limitation in explainability["limitations"]:
        lines.append(f"- {limitation}")
    lines.append("")

    lines.extend([f"## {t('section_simple_glossary', language, 'Simple glossary')}"])
    for item in legend_lines:
        lines.append(f"- {item}")
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def markdown_to_html(markdown_text: str, language: str = "en") -> str:
    direction = "rtl" if is_rtl(language) else "ltr"
    align = "right" if is_rtl(language) else "left"
    html_lines = [f'<div dir="{direction}" style="text-align: {align}; line-height: 1.55;">']
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html_lines.append("</ul>")
            in_list = False

    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            close_list()
            continue
        if line.startswith("# "):
            close_list()
            html_lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            close_list()
            html_lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            close_list()
            html_lines.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{html.escape(line[2:])}</li>")
        else:
            close_list()
            html_lines.append(f"<p>{html.escape(line)}</p>")

    close_list()
    html_lines.append("</div>")
    return "\n".join(html_lines)
