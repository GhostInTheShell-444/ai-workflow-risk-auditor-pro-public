from __future__ import annotations

import html
from collections import Counter, defaultdict
from typing import Any

import streamlit as st

from design_tokens import COLORS, FONT_STACK, color_css_variables, severity_token, status_token
from i18n import is_rtl, t, translate_category


SEVERITY_ORDER = ("critical", "high", "medium", "low", "unknown")


def _escape(value: object) -> str:
    return html.escape(str(value or ""))


def humanize_key(value: object) -> str:
    return str(value or "unknown").replace("_", " ").strip().title()


def apply_global_styles(language: str, theme: str = "light") -> None:
    direction = "rtl" if is_rtl(language) else "ltr"
    align = "right" if is_rtl(language) else "left"
    rtl_css = ""
    if is_rtl(language):
        rtl_css = """
        div[data-testid="stAppViewContainer"],
        div[data-testid="stSidebar"] {
            direction: rtl;
            text-align: right;
        }
        .aiwra-code,
        .aiwra-prompt,
        pre,
        code {
            direction: ltr;
            text-align: left;
        }
        """
    st.markdown(
        f"""
        <style>
        :root {{
            {color_css_variables(theme)}
            --aiwra-font-stack: {FONT_STACK};
            color-scheme: {"dark" if theme == "dark" else "light"};
        }}
        html, body, .stApp {{
            font-family: var(--aiwra-font-stack);
            color: var(--aiwra-text);
            background: var(--aiwra-bg);
        }}
        .stApp,
        div[data-testid="stAppViewContainer"] {{
            background: var(--aiwra-bg);
        }}
        div[data-testid="stSidebar"] {{
            background: var(--aiwra-surface);
            border-inline-end: 1px solid var(--aiwra-border);
        }}
        div[data-testid="stHeader"] {{
            background: color-mix(in srgb, var(--aiwra-bg) 88%, transparent);
        }}
        .block-container {{
            padding-top: 1.25rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }}
        .aiwra-root {{
            direction: {direction};
            text-align: {align};
        }}
        .aiwra-hero {{
            border: 1px solid var(--aiwra-border);
            border-inline-start: 4px solid var(--aiwra-primary);
            background: linear-gradient(135deg, var(--aiwra-surface), var(--aiwra-surface-alt));
            border-radius: 8px;
            padding: 1rem 1.1rem;
            margin: 0.25rem 0 0.85rem 0;
            box-shadow: 0 14px 34px var(--aiwra-shadow);
        }}
        .aiwra-hero h2 {{
            margin: 0 0 0.45rem 0;
            font-size: 1.55rem;
            line-height: 1.25;
            letter-spacing: 0;
        }}
        .aiwra-card {{
            border: 1px solid var(--aiwra-border);
            background: var(--aiwra-surface);
            border-radius: 8px;
            padding: 0.9rem;
            margin: 0.28rem 0 0.65rem 0;
            box-shadow: 0 10px 26px var(--aiwra-shadow);
        }}
        .aiwra-card h3,
        .aiwra-card h4 {{
            margin: 0 0 0.4rem 0;
            letter-spacing: 0;
        }}
        .aiwra-card p {{
            margin: 0.35rem 0;
            color: var(--aiwra-muted);
            line-height: 1.45;
            font-size: 0.92rem;
        }}
        .aiwra-kpi-value {{
            display: block;
            color: var(--aiwra-text);
            font-size: 1.65rem;
            font-weight: 700;
            line-height: 1.2;
            margin: 0.35rem 0;
        }}
        .aiwra-label {{
            font-size: 0.88rem;
            font-weight: 700;
            color: var(--aiwra-text);
        }}
        .aiwra-muted {{
            color: var(--aiwra-muted);
        }}
        .aiwra-badge {{
            display: inline-flex;
            align-items: center;
            max-width: 100%;
            white-space: normal;
            border-radius: 999px;
            border: 1px solid var(--aiwra-border);
            padding: 0.18rem 0.55rem;
            margin: 0.1rem 0.2rem 0.1rem 0;
            font-size: 0.82rem;
            font-weight: 700;
            line-height: 1.35;
        }}
        .aiwra-section {{
            border-bottom: 1px solid var(--aiwra-border);
            padding-bottom: 0.45rem;
            margin: 1rem 0 0.7rem 0;
        }}
        .aiwra-section h3 {{
            margin: 0;
            letter-spacing: 0;
        }}
        .aiwra-grid {{
            display: grid;
            gap: 0.75rem;
        }}
        .aiwra-grid-3 {{
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        }}
        .aiwra-bento {{
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.55rem 0 1rem 0;
        }}
        .aiwra-bento-card {{
            grid-column: span 2;
            min-height: 168px;
            border: 1px solid var(--aiwra-border);
            background: var(--aiwra-surface);
            border-radius: 8px;
            padding: 0.95rem;
            box-shadow: 0 12px 30px var(--aiwra-shadow);
            display: flex;
            flex-direction: column;
            gap: 0.42rem;
        }}
        .aiwra-bento-wide {{
            grid-column: span 3;
        }}
        .aiwra-bento-title {{
            color: var(--aiwra-muted);
            font-size: 0.84rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0;
        }}
        .aiwra-bento-value {{
            color: var(--aiwra-text);
            font-size: 1.45rem;
            line-height: 1.2;
            font-weight: 800;
        }}
        .aiwra-severity-strip {{
            width: 100%;
            height: 0.28rem;
            border-radius: 999px;
            background: var(--aiwra-primary);
            margin-bottom: 0.15rem;
        }}
        .aiwra-card-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.65rem;
            margin: 0.4rem 0 0.85rem 0;
        }}
        .aiwra-heatmap {{
            display: grid;
            gap: 0.45rem;
            margin: 0.5rem 0 1rem 0;
            overflow-x: auto;
        }}
        .aiwra-heatmap-row {{
            display: grid;
            grid-template-columns: minmax(150px, 1.15fr) repeat(5, minmax(118px, 1fr));
            gap: 0.45rem;
            min-width: 760px;
        }}
        .aiwra-heatmap-head,
        .aiwra-heatmap-label,
        .aiwra-heatmap-cell {{
            border: 1px solid var(--aiwra-border-soft);
            border-radius: 8px;
            padding: 0.62rem;
            background: var(--aiwra-surface);
            line-height: 1.32;
        }}
        .aiwra-heatmap-head {{
            font-weight: 700;
            color: var(--aiwra-text);
            background: var(--aiwra-surface-muted);
        }}
        .aiwra-heatmap-label {{
            font-weight: 700;
            color: var(--aiwra-text);
            background: var(--aiwra-surface-soft);
        }}
        .aiwra-heatmap-cell strong {{
            display: block;
            color: var(--aiwra-text);
        }}
        .aiwra-flow {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: stretch;
            margin: 0.65rem 0;
        }}
        .aiwra-flow-step {{
            border: 1px solid var(--aiwra-border);
            border-radius: 8px;
            background: var(--aiwra-surface);
            padding: 0.7rem 0.85rem;
            min-width: 150px;
            flex: 1 1 150px;
        }}
        .aiwra-flow-step small {{
            display: block;
            color: var(--aiwra-muted);
            margin-top: 0.25rem;
        }}
        .aiwra-timeline-item {{
            border-inline-start: 3px solid var(--aiwra-blue);
            padding: 0.35rem 0.75rem;
            margin: 0.45rem 0;
            background: var(--aiwra-surface);
            border-radius: 0 8px 8px 0;
        }}
        .aiwra-code {{
            direction: ltr;
            text-align: left;
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid var(--aiwra-border);
            border-radius: 8px;
        }}
        div[data-testid="stCodeBlock"],
        pre,
        code {{
            background: var(--aiwra-surface-alt) !important;
            color: var(--aiwra-text) !important;
            border-color: var(--aiwra-border) !important;
        }}
        div[data-testid="stAlert"] {{
            border-radius: 8px;
        }}
        @media (max-width: 900px) {{
            .aiwra-bento {{
                grid-template-columns: 1fr;
            }}
            .aiwra-bento-card,
            .aiwra-bento-wide {{
                grid-column: span 1;
            }}
        }}
        {rtl_css}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_badge(prefix: str, label: str, token: dict[str, Any], description: str = "") -> None:
    title = f"{prefix}: {label}"
    if description:
        title = f"{title} - {description}"
    st.markdown(
        f"""
        <span class="aiwra-badge" title="{_escape(title)}"
              style="color:{token['color']}; background:{token['background']}; border-color:{token['border']};">
            {_escape(prefix)}: {_escape(label)}
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_severity_badge(severity: object, language: str = "en") -> None:
    token = severity_token(severity, language)
    render_badge(t("severity_label", language, "Severity"), token["label"], token, token["description"])


def render_status_badge(status: object, language: str = "en") -> None:
    token = status_token(status, language)
    render_badge(t("status_label", language, "Status"), token["label"], token, token["description"])


def render_source_status_chip(status: object, language: str = "en") -> None:
    token = status_token(status, language)
    render_badge(t("source_label", language, "Source"), token["label"], token, token["description"])


def render_metric_card(
    label: str,
    value: object,
    source: str,
    meaning: str,
    limit: str,
    status: str = "calculated",
    language: str = "en",
) -> None:
    token = status_token(status, language)
    st.markdown(
        f"""
        <div class="aiwra-card">
            <div class="aiwra-label">{_escape(label)}</div>
            <span class="aiwra-kpi-value">{_escape(value)}</span>
            <span class="aiwra-badge"
                  style="color:{token['color']}; background:{token['background']}; border-color:{token['border']};">
                {_escape(t('source_label', language, 'Source'))}: {_escape(token['label'])}
            </span>
            <p><strong>{_escape(t('meaning_label', language, 'Meaning'))}:</strong> {_escape(meaning)}</p>
            <p><strong>{_escape(t('limit_label', language, 'Limit'))}:</strong> {_escape(limit)}</p>
            <p><strong>{_escape(t('source_label', language, 'Source'))}:</strong> {_escape(source)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_bento_cards(cards: list[dict[str, Any]], language: str = "en") -> None:
    html_cards = []
    for index, card in enumerate(cards, start=1):
        status = status_token(card.get("status", "calculated"), language)
        severity = card.get("severity")
        strip_color = "var(--aiwra-primary)"
        if severity:
            strip_color = severity_token(severity, language)["color"]
        card_class = "aiwra-bento-card aiwra-bento-wide" if index in {1, 6} else "aiwra-bento-card"
        html_cards.append(
            f"""
            <div class="{card_class}">
                <div class="aiwra-severity-strip" style="background:{strip_color};"></div>
                <div class="aiwra-bento-title">{_escape(card.get('title', ''))}</div>
                <div class="aiwra-bento-value">{_escape(card.get('value', ''))}</div>
                <span class="aiwra-badge"
                      style="color:{status['color']}; background:{status['background']}; border-color:{status['border']};">
                    {_escape(t('source_label', language, 'Source'))}: {_escape(status['label'])}
                </span>
                <p><strong>{_escape(t('meaning_label', language, 'Meaning'))}:</strong> {_escape(card.get('meaning', ''))}</p>
                <p><strong>{_escape(t('limit_label', language, 'Limit'))}:</strong> {_escape(card.get('limit', ''))}</p>
                <p><strong>{_escape(t('source_label', language, 'Source'))}:</strong> {_escape(card.get('source', ''))}</p>
            </div>
            """
        )
    st.markdown(f"<div class='aiwra-bento'>{''.join(html_cards)}</div>", unsafe_allow_html=True)


def render_info_card(title: str, body: str, status: str | None = None, language: str = "en") -> None:
    badge = ""
    if status:
        token = status_token(status, language)
        badge = (
            f"<span class='aiwra-badge' style='color:{token['color']}; "
            f"background:{token['background']}; border-color:{token['border']};'>"
            f"{_escape(t('status_label', language, 'Status'))}: {_escape(token['label'])}</span>"
        )
    st.markdown(
        f"""
        <div class="aiwra-card">
            <h4>{_escape(title)}</h4>
            {badge}
            <p>{_escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str = "", status: str | None = None, language: str = "en") -> None:
    badge = ""
    if status:
        token = status_token(status, language)
        badge = (
            f"<span class='aiwra-badge' style='color:{token['color']}; "
            f"background:{token['background']}; border-color:{token['border']};'>"
            f"{_escape(token['label'])}</span>"
        )
    st.markdown(
        f"""
        <div class="aiwra-section">
            <h3>{_escape(title)} {badge}</h3>
            <p class="aiwra-muted">{_escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_legend(items: list[tuple[str, str]], title: str | None = None) -> None:
    if title:
        st.caption(title)
    if not items:
        return
    lines = "".join(f"<li><strong>{_escape(label)}</strong>: {_escape(body)}</li>" for label, body in items)
    st.markdown(f"<ul>{lines}</ul>", unsafe_allow_html=True)


def render_empty_state(title: str, body: str, action: str = "") -> None:
    action_html = f"<p><strong>{_escape(action)}</strong></p>" if action else ""
    st.markdown(
        f"""
        <div class="aiwra-card">
            <h4>{_escape(title)}</h4>
            <p>{_escape(body)}</p>
            {action_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_heatmap_cells(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str]] = Counter()
    categories: set[str] = set()
    for finding in findings:
        category = str(finding.get("category") or "unknown")
        severity = str(finding.get("severity") or "unknown").casefold()
        severity = severity if severity in SEVERITY_ORDER else "unknown"
        categories.add(category)
        counts[(category, severity)] += int(finding.get("count") or 1)

    cells: list[dict[str, Any]] = []
    for category in sorted(categories):
        for severity in SEVERITY_ORDER:
            count = counts[(category, severity)]
            cells.append({"category": category, "severity": severity, "count": count})
    return cells


def render_heatmap(findings: list[dict[str, Any]], language: str = "en") -> None:
    cells = build_heatmap_cells(findings)
    if not cells:
        render_empty_state(
            t("heatmap_empty_title", language, "No heatmap data yet"),
            t("heatmap_empty_body", language, "Run or save an audit with detected findings to populate this text-first heatmap."),
        )
        return
    grouped: dict[str, dict[str, int]] = defaultdict(dict)
    for cell in cells:
        grouped[cell["category"]][cell["severity"]] = int(cell["count"])

    headers = [t("category_label", language, "Category")] + [
        severity_token(severity, language)["label"] for severity in SEVERITY_ORDER
    ]
    header_columns = st.columns([1.4, 1, 1, 1, 1])
    for column, header in zip(header_columns, headers):
        column.markdown(f"**{header}**")

    for category, severity_counts in grouped.items():
        row_columns = st.columns([1.4, 1, 1, 1, 1])
        row_columns[0].markdown(f"**{translate_category(category, language)}**")
        for column, severity in zip(row_columns[1:], SEVERITY_ORDER):
            token = severity_token(severity, language)
            count = int(severity_counts.get(severity, 0))
            text = t("heatmap_cell_text", language, "{count} finding(s)").format(count=count)
            column.metric(token["label"], count, help=f"{text}. {token['description']}")


def build_matrix_cells(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[tuple[int, int], dict[str, Any]] = {}
    for entry in entries:
        impact = int(entry.get("impact") or 0)
        likelihood = int(entry.get("likelihood") or 0)
        if impact <= 0 or likelihood <= 0:
            continue
        score = impact * likelihood
        if score >= 20:
            severity = "critical"
        elif score >= 12:
            severity = "high"
        elif score >= 6:
            severity = "medium"
        else:
            severity = "low"
        key = (impact, likelihood)
        current = buckets.setdefault(
            key,
            {
                "impact": impact,
                "likelihood": likelihood,
                "count": 0,
                "severity": severity,
                "factors": [],
            },
        )
        current["count"] += 1
        current["factors"].append(str(entry.get("factor") or "unknown"))
        if SEVERITY_ORDER.index(severity) < SEVERITY_ORDER.index(str(current["severity"])):
            current["severity"] = severity
    return sorted(buckets.values(), key=lambda item: (item["impact"], item["likelihood"]), reverse=True)


def render_risk_matrix(entries: list[dict[str, Any]], language: str = "en") -> None:
    cells = build_matrix_cells(entries)
    if not cells:
        render_empty_state(
            t("matrix_empty_title", language, "No matrix entries yet"),
            t("matrix_empty_body", language, "The matrix appears after evidence is mapped to local impact and likelihood attributes."),
        )
        return
    for cell in cells[:9]:
        token = severity_token(cell["severity"], language)
        factors = ", ".join(t(f"factor_{factor}", language, humanize_key(factor)) for factor in cell["factors"][:3])
        st.markdown(
            f"""
            <div class="aiwra-card" style="border-color:{token['border']}; background:{token['background']};">
                <strong>{_escape(t('matrix_cell_title', language, 'Impact {impact} x likelihood {likelihood}').format(impact=cell['impact'], likelihood=cell['likelihood']))}</strong>
                <p>{_escape(t('matrix_cell_count', language, '{count} mapped factor(s)').format(count=cell['count']))}</p>
                <p>{_escape(t('severity_label', language, 'Severity'))}: {_escape(token['label'])}</p>
                <p>{_escape(t('matrix_cell_factors', language, 'Factors'))}: {_escape(factors)}</p>
                <p>{_escape(t('matrix_cell_limit', language, 'Indicative matrix derived from local evidence counts and rule weights.'))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_workflow_graph(language: str = "en") -> None:
    steps = [
        ("workflow_graph_input", "Input workflow"),
        ("workflow_graph_parser", "Local parser"),
        ("workflow_graph_evidence", "Evidence engine"),
        ("workflow_graph_scoring", "Risk scoring"),
        ("workflow_graph_controls", "Recommended controls"),
        ("workflow_graph_report", "Report export"),
        ("workflow_graph_ai", "Optional local AI narrative"),
    ]
    html_steps = ""
    for index, (key, fallback) in enumerate(steps, start=1):
        html_steps += (
            "<div class='aiwra-flow-step'>"
            f"<strong>{index}. {_escape(t(key, language, fallback))}</strong>"
            f"<small>{_escape(t(f'{key}_help', language, 'Local deterministic pipeline step.'))}</small>"
            "</div>"
        )
    st.markdown(f"<div class='aiwra-flow'>{html_steps}</div>", unsafe_allow_html=True)
    st.caption(
        t(
            "workflow_graph_required_note",
            language,
            "This graph shows how the local deterministic audit pipeline interprets the workflow. It is not a live production integration map.",
        )
    )


def render_evidence_card(finding: dict[str, Any], index: int, language: str = "en") -> None:
    severity = str(finding.get("severity", "unknown"))
    token = severity_token(severity, language)
    category = t(f"kb_category_{finding.get('category')}", language, humanize_key(finding.get("category")))
    controls = finding.get("recommended_controls", [])
    controls_text = ", ".join(str(item) for item in controls[:3]) if isinstance(controls, list) else str(controls)
    st.markdown(
        f"""
        <div class="aiwra-card" style="border-color:{token['border']};">
            <h4>{index}. {_escape(token['label'])} - {_escape(category)}</h4>
            <p><strong>{_escape(t('evidence_label', language, 'Evidence'))}:</strong> {_escape(finding.get('matched_text_evidence', ''))}</p>
            <p><strong>{_escape(t('rule_used_label', language, 'Rule used'))}:</strong> {_escape(finding.get('matched_rule_id', ''))}</p>
            <p><strong>{_escape(t('confidence_label', language, 'Confidence'))}:</strong> {_escape(finding.get('confidence', ''))}</p>
            <p><strong>{_escape(t('recommended_action_label', language, 'Recommended action'))}:</strong> {_escape(controls_text or t('none_detected', language, 'None detected.'))}</p>
            <p><strong>{_escape(t('limit_label', language, 'Limit'))}:</strong> {_escape(t('evidence_card_limit', language, 'This finding is detected from local text evidence and needs human review before action.'))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_issue_card(issue: dict[str, Any], language: str = "en") -> None:
    severity = severity_token(issue.get("severity", "unknown"), language)
    status = status_token(issue.get("status", "recommended"), language)
    human_review = issue.get("human_review", True)
    human_review_label = (
        t("yes_label", language, "Yes")
        if human_review is True or str(human_review).casefold() == "yes"
        else str(human_review)
    )
    st.markdown(
        f"""
        <div class="aiwra-card">
            <h4>{_escape(issue.get('title', t('issue_title_fallback', language, 'Local follow-up item')))}</h4>
            <span class="aiwra-badge" style="color:{severity['color']}; background:{severity['background']}; border-color:{severity['border']};">
                {_escape(t('severity_label', language, 'Severity'))}: {_escape(severity['label'])}
            </span>
            <span class="aiwra-badge" style="color:{status['color']}; background:{status['background']}; border-color:{status['border']};">
                {_escape(t('status_label', language, 'Status'))}: {_escape(status['label'])}
            </span>
            <p><strong>{_escape(t('evidence_label', language, 'Evidence'))}:</strong> {_escape(issue.get('evidence', ''))}</p>
            <p><strong>{_escape(t('recommended_action_label', language, 'Recommended action'))}:</strong> {_escape(issue.get('control', ''))}</p>
            <p><strong>{_escape(t('human_review_required_label', language, 'Human review required'))}:</strong> {_escape(human_review_label)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_timeline(events: list[dict[str, Any]], language: str = "en") -> None:
    if not events:
        render_empty_state(
            t("timeline_empty_title", language, "No local audit timeline yet"),
            t("timeline_empty_body", language, "Save an audit report locally to populate the audit timeline."),
        )
        return
    for event in events[:8]:
        st.markdown(
            f"""
            <div class="aiwra-timeline-item">
                <strong>{_escape(event.get('created_at', ''))}</strong><br>
                {_escape(t('timeline_event_label', language, 'Event'))}: {_escape(humanize_key(event.get('event_type')))}
                <br><span class="aiwra-muted">{_escape(event.get('entity_type', ''))} #{_escape(event.get('entity_id', ''))}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_ai_output_panel(
    prompt: str,
    response: str | None,
    deterministic_summary: str,
    language: str = "en",
) -> None:
    render_info_card(
        t("local_ai_comparison_title", language, "Deterministic report vs local AI narrative"),
        deterministic_summary,
        status="calculated",
        language=language,
    )
    st.markdown(f"**{t('local_ai_prompt_sent', language, 'Prompt sent')}**")
    st.code(prompt or t("local_ai_no_prompt", language, "No prompt generated."), language="text")
    st.markdown(f"**{t('local_ai_exact_response', language, 'Exact local AI response')}**")
    if response:
        st.code(response, language="text")
    else:
        render_empty_state(
            t("local_ai_no_response_title", language, "No local AI response"),
            t("local_ai_no_response_body", language, "Ollama may be unavailable, no local model may be installed, or the request was not run."),
        )


def render_accessibility_note(language: str = "en") -> None:
    render_info_card(
        t("accessibility_note_title", language, "Accessibility note"),
        t(
            "accessibility_note_body",
            language,
            "Colors are only a secondary signal. Badges, heatmap cells, and matrix cells include text labels, counts, source, meaning, and limits.",
        ),
        status="local_only",
        language=language,
    )


def render_how_to_read_panel(language: str, body_key: str, fallback: str) -> None:
    render_info_card(t("how_to_read_title", language, "How to read this page"), t(body_key, language, fallback), "local_only", language)


def render_read_only_notice(language: str = "en") -> None:
    render_info_card(
        t("kb_read_only_title", language, "Read-only local rule library"),
        t(
            "kb_read_only_body",
            language,
            "This Knowledge Base is loaded from local JSON files and seeded into local SQLite. It is not a cloud database and this screen does not edit rules.",
        ),
        "read_only",
        language,
    )
