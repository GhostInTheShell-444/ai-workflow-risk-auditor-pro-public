from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from database import get_connection, init_db, row_to_dict, rows_to_dicts
from export_json import render_json_summary


def create_audit_event(
    event_type: str,
    entity_type: str,
    entity_id: int | None = None,
    details: dict[str, Any] | None = None,
    db_path: str | Path | None = None,
) -> int:
    init_db(db_path)
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO audit_events(event_type, entity_type, entity_id, details_json)
            VALUES (?, ?, ?, ?)
            """,
            (event_type, entity_type, entity_id, json.dumps(details or {}, ensure_ascii=False)),
        )
        return int(cursor.lastrowid)


def create_project(
    name: str,
    description: str = "",
    is_demo: bool = False,
    db_path: str | Path | None = None,
) -> int:
    init_db(db_path)
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO projects(name, description, is_demo) VALUES (?, ?, ?)",
            (name.strip() or "Untitled Project", description, 1 if is_demo else 0),
        )
        project_id = int(cursor.lastrowid)
    create_audit_event("project_created", "project", project_id, {"name": name, "is_demo": is_demo}, db_path)
    return project_id


def list_projects(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    init_db(db_path)
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT id, name, description, is_demo, created_at FROM projects ORDER BY is_demo DESC, created_at DESC"
        ).fetchall()
    return rows_to_dicts(rows)


def save_workflow(
    project_id: int,
    name: str,
    workflow_text: str,
    source: str = "user",
    is_demo: bool = False,
    db_path: str | Path | None = None,
) -> int:
    init_db(db_path)
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO workflows(project_id, name, workflow_text, source, is_demo)
            VALUES (?, ?, ?, ?, ?)
            """,
            (project_id, name.strip() or "Saved workflow", workflow_text, source, 1 if is_demo else 0),
        )
        workflow_id = int(cursor.lastrowid)
    create_audit_event("workflow_saved", "workflow", workflow_id, {"source": source, "is_demo": is_demo}, db_path)
    return workflow_id


def save_workflow_steps(
    workflow_id: int,
    steps: list[str],
    db_path: str | Path | None = None,
) -> int:
    init_db(db_path)
    with get_connection(db_path) as connection:
        connection.executemany(
            "INSERT INTO workflow_steps(workflow_id, step_index, text) VALUES (?, ?, ?)",
            [(workflow_id, index, text) for index, text in enumerate(steps, start=1)],
        )
    create_audit_event("workflow_steps_saved", "workflow", workflow_id, {"step_count": len(steps)}, db_path)
    return len(steps)


def save_assessment(
    project_id: int,
    workflow_id: int | None,
    analysis: dict[str, Any],
    db_path: str | Path | None = None,
) -> int:
    init_db(db_path)
    risk = analysis.get("risk", {})
    risk_matrix = analysis.get("risk_matrix", {})
    raw_score = int(risk_matrix.get("raw_risk_score", risk.get("score", 0) if isinstance(risk, dict) else 0))
    severity = str(risk_matrix.get("severity", risk.get("level", "low") if isinstance(risk, dict) else "low"))
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO assessments(project_id, workflow_id, workflow_type, raw_score, severity, risk_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                workflow_id,
                str(analysis.get("workflow_type", "unknown")),
                raw_score,
                severity,
                json.dumps({"risk": risk, "risk_matrix": risk_matrix}, ensure_ascii=False),
            ),
        )
        assessment_id = int(cursor.lastrowid)
        for entry in risk_matrix.get("entries", []):
            connection.execute(
                """
                INSERT INTO risk_factors
                (assessment_id, factor_key, weight, impact, likelihood, confidence, score_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment_id,
                    entry["factor"],
                    int(entry["score_impact"]),
                    int(entry["impact"]),
                    int(entry["likelihood"]),
                    float(entry["confidence"]),
                    int(entry["score_impact"]),
                ),
            )
    create_audit_event("assessment_saved", "assessment", assessment_id, {"severity": severity}, db_path)
    return assessment_id


def save_findings(
    assessment_id: int,
    findings: list[dict[str, Any]],
    db_path: str | Path | None = None,
) -> int:
    init_db(db_path)
    with get_connection(db_path) as connection:
        connection.executemany(
            """
            INSERT INTO detected_findings
            (assessment_id, finding_id, category, severity, confidence, evidence, matched_rule_id,
             step_reference, explanation, controls_json, factors_json, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    assessment_id,
                    finding["finding_id"],
                    finding["category"],
                    finding["severity"],
                    float(finding["confidence"]),
                    finding["matched_text_evidence"],
                    finding["matched_rule_id"],
                    finding["workflow_step_reference"],
                    finding["explanation"],
                    json.dumps(finding.get("recommended_controls", []), ensure_ascii=False),
                    json.dumps(finding.get("risk_factor_mapping", []), ensure_ascii=False),
                    finding.get("language_detected_when_possible", ""),
                )
                for finding in findings
            ],
        )
    create_audit_event("findings_saved", "assessment", assessment_id, {"finding_count": len(findings)}, db_path)
    return len(findings)


def save_recommended_controls(
    assessment_id: int,
    controls: list[dict[str, Any]],
    db_path: str | Path | None = None,
) -> int:
    init_db(db_path)
    with get_connection(db_path) as connection:
        connection.executemany(
            """
            INSERT INTO recommended_controls(assessment_id, control_id, name, reason, risk_factors_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    assessment_id,
                    control["id"],
                    control["name"],
                    control.get("reason", ""),
                    json.dumps(control.get("risk_factors", []), ensure_ascii=False),
                )
                for control in controls
            ],
        )
    create_audit_event("recommended_controls_saved", "assessment", assessment_id, {"control_count": len(controls)}, db_path)
    return len(controls)


def save_simulation_run(
    assessment_id: int,
    simulation: dict[str, Any],
    db_path: str | Path | None = None,
) -> int:
    init_db(db_path)
    raw = simulation.get("raw_risk", {})
    residual = simulation.get("residual_risk", {})
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO simulation_runs
            (assessment_id, selected_controls_json, raw_score, residual_score, reduction,
             severity_before, severity_after, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assessment_id,
                json.dumps(simulation.get("selected_controls", []), ensure_ascii=False),
                int(raw.get("score", 0)),
                int(residual.get("score", 0)),
                int(simulation.get("score_reduction", 0)),
                str(raw.get("severity", "low")),
                str(residual.get("severity", "low")),
                str(simulation.get("explanation", "")),
            ),
        )
        simulation_id = int(cursor.lastrowid)
    create_audit_event("simulation_saved", "simulation", simulation_id, {"assessment_id": assessment_id}, db_path)
    return simulation_id


def save_report(
    assessment_id: int,
    project_id: int,
    title: str,
    markdown: str,
    json_summary: str | None = None,
    analysis: dict[str, Any] | None = None,
    simulation: dict[str, Any] | None = None,
    db_path: str | Path | None = None,
) -> int:
    init_db(db_path)
    summary = json_summary or (render_json_summary(analysis or {}, simulation) if analysis is not None else "{}")
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO reports(assessment_id, project_id, title, markdown, json_summary)
            VALUES (?, ?, ?, ?, ?)
            """,
            (assessment_id, project_id, title.strip() or "AI Workflow Risk Audit Report", markdown, summary),
        )
        report_id = int(cursor.lastrowid)
    create_audit_event("report_saved", "report", report_id, {"assessment_id": assessment_id}, db_path)
    return report_id


def list_reports(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    init_db(db_path)
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT reports.id, reports.title, reports.created_at, reports.project_id,
                   projects.name AS project_name, assessments.raw_score, assessments.severity
            FROM reports
            JOIN projects ON projects.id = reports.project_id
            JOIN assessments ON assessments.id = reports.assessment_id
            ORDER BY reports.created_at DESC, reports.id DESC
            """
        ).fetchall()
    return rows_to_dicts(rows)


def get_report(report_id: int, db_path: str | Path | None = None) -> dict[str, Any] | None:
    init_db(db_path)
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT * FROM reports WHERE id = ?",
            (report_id,),
        ).fetchone()
    return row_to_dict(row)


def list_audit_events(limit: int = 50, db_path: str | Path | None = None) -> list[dict[str, Any]]:
    init_db(db_path)
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT * FROM audit_events ORDER BY created_at DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return rows_to_dicts(rows)


def get_dashboard_metrics(db_path: str | Path | None = None) -> dict[str, Any]:
    init_db(db_path)
    with get_connection(db_path) as connection:
        saved_analyses = int(connection.execute("SELECT COUNT(*) FROM assessments").fetchone()[0])
        simulation_count = int(connection.execute("SELECT COUNT(*) FROM simulation_runs").fetchone()[0])
        demo_saved_analyses = int(
            connection.execute(
                """
                SELECT COUNT(*)
                FROM assessments
                LEFT JOIN workflows ON workflows.id = assessments.workflow_id
                WHERE COALESCE(workflows.is_demo, 0) = 1
                """
            ).fetchone()[0]
        )
        user_saved_analyses = saved_analyses - demo_saved_analyses
        average_risk = connection.execute("SELECT AVG(raw_score) FROM assessments").fetchone()[0] or 0
        average_reduction = connection.execute("SELECT AVG(reduction) FROM simulation_runs").fetchone()[0] or 0
        distribution_rows = connection.execute(
            "SELECT severity, COUNT(*) AS count FROM assessments GROUP BY severity ORDER BY severity"
        ).fetchall()
        top_categories_rows = connection.execute(
            """
            SELECT category, COUNT(*) AS count
            FROM detected_findings
            GROUP BY category
            ORDER BY count DESC, category
            LIMIT 8
            """
        ).fetchall()
        top_controls_rows = connection.execute(
            """
            SELECT name, COUNT(*) AS count
            FROM recommended_controls
            GROUP BY name
            ORDER BY count DESC, name
            LIMIT 8
            """
        ).fetchall()
        latest_reports = connection.execute(
            """
            SELECT id, title, created_at
            FROM reports
            ORDER BY created_at DESC, id DESC
            LIMIT 5
            """
        ).fetchall()
        trend_rows = connection.execute(
            """
            SELECT date(created_at) AS day, AVG(raw_score) AS average_score
            FROM assessments
            GROUP BY date(created_at)
            ORDER BY day
            """
        ).fetchall()
        heatmap_rows = connection.execute(
            """
            SELECT category, severity, COUNT(*) AS count
            FROM detected_findings
            GROUP BY category, severity
            ORDER BY category, severity
            """
        ).fetchall()
        latest_audit_at_row = connection.execute(
            "SELECT MAX(created_at) FROM assessments"
        ).fetchone()
        latest_audit_at = latest_audit_at_row[0] if latest_audit_at_row else None
    return {
        "saved_analyses": saved_analyses,
        "average_risk": round(float(average_risk), 2),
        "risk_distribution": rows_to_dicts(distribution_rows),
        "top_risk_categories": rows_to_dicts(top_categories_rows),
        "top_recommended_controls": rows_to_dicts(top_controls_rows),
        "latest_reports": rows_to_dicts(latest_reports),
        "risk_trend": rows_to_dicts(trend_rows),
        "finding_heatmap": rows_to_dicts(heatmap_rows),
        "latest_audit_at": latest_audit_at,
        "simulation_count": simulation_count,
        "average_simulated_reduction": round(float(average_reduction), 2),
        "user_saved_analyses": user_saved_analyses,
        "demo_saved_analyses": demo_saved_analyses,
    }
