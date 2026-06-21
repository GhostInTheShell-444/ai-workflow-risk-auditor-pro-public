import json
import sqlite3

from analyzer import analyze_workflow
from database import SCHEMA_VERSION, init_db, reset_demo_db
from examples import get_example_text
from repositories import (
    create_audit_event,
    create_project,
    get_dashboard_metrics,
    get_report,
    list_projects,
    list_reports,
    save_assessment,
    save_findings,
    save_recommended_controls,
    save_report,
    save_simulation_run,
    save_workflow,
    save_workflow_steps,
)
from residual_risk import default_control_selection, simulate_residual_risk
from workflow_parser import extract_workflow_steps


REQUIRED_TABLES = {
    "schema_version",
    "projects",
    "workflows",
    "workflow_steps",
    "assessments",
    "detected_findings",
    "risk_factors",
    "control_library",
    "recommended_controls",
    "simulation_runs",
    "reports",
    "audit_events",
    "knowledge_articles",
    "demo_scenarios",
}


def _count(db_path, table):
    with sqlite3.connect(db_path) as connection:
        return connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_database_initialization_creates_required_tables(tmp_path):
    db_path = tmp_path / "aiwra.db"
    init_db(db_path, seed=False)
    with sqlite3.connect(db_path) as connection:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        }
    assert REQUIRED_TABLES.issubset(tables)


def test_schema_version_is_recorded(tmp_path):
    db_path = tmp_path / "aiwra.db"
    init_db(db_path, seed=False)
    with sqlite3.connect(db_path) as connection:
        version = connection.execute("SELECT version FROM schema_version").fetchone()[0]
    assert version == SCHEMA_VERSION


def test_seed_database_loads_controls_articles_and_demo_scenarios(tmp_path):
    db_path = tmp_path / "aiwra.db"
    init_db(db_path, seed=True)
    assert _count(db_path, "control_library") >= 40
    assert _count(db_path, "knowledge_articles") >= 25
    assert _count(db_path, "demo_scenarios") >= 20


def test_reset_demo_db_recreates_seed_data(tmp_path):
    db_path = tmp_path / "aiwra.db"
    init_db(db_path, seed=True)
    create_project("Temporary user project", db_path=db_path)
    reset_demo_db(db_path)
    project_names = [project["name"] for project in list_projects(db_path)]
    assert "Synthetic Demo Project" in project_names
    assert "Temporary user project" not in project_names


def test_create_project_is_listed(tmp_path):
    db_path = tmp_path / "aiwra.db"
    init_db(db_path, seed=True)
    project_id = create_project("Privacy review", "Local only", db_path=db_path)
    projects = list_projects(db_path)
    assert any(project["id"] == project_id and project["name"] == "Privacy review" for project in projects)


def test_save_workflow_requires_explicit_call(tmp_path):
    db_path = tmp_path / "aiwra.db"
    init_db(db_path, seed=False)
    analyze_workflow("AI drafts customer emails, but a human reviews them.")
    assert _count(db_path, "workflows") == 0
    project_id = create_project("Explicit save", db_path=db_path)
    workflow_id = save_workflow(project_id, "Workflow", "AI drafts customer emails.", db_path=db_path)
    assert workflow_id > 0
    assert _count(db_path, "workflows") == 1


def test_workflow_steps_are_persisted(tmp_path):
    db_path = tmp_path / "aiwra.db"
    project_id = create_project("Steps", db_path=db_path)
    text = get_example_text("customer_support")
    workflow_id = save_workflow(project_id, "Support", text, db_path=db_path)
    steps = extract_workflow_steps(text)
    assert save_workflow_steps(workflow_id, steps, db_path=db_path) == len(steps)
    assert _count(db_path, "workflow_steps") == len(steps)


def test_assessment_and_risk_factors_are_persisted(tmp_path):
    db_path = tmp_path / "aiwra.db"
    project_id = create_project("Assessment", db_path=db_path)
    analysis = analyze_workflow(get_example_text("soc_alert_triage"))
    assessment_id = save_assessment(project_id, None, analysis, db_path=db_path)
    assert assessment_id > 0
    assert _count(db_path, "assessments") == 1
    assert _count(db_path, "risk_factors") >= 1


def test_findings_are_persisted(tmp_path):
    db_path = tmp_path / "aiwra.db"
    project_id = create_project("Findings", db_path=db_path)
    analysis = analyze_workflow(get_example_text("customer_support"))
    assessment_id = save_assessment(project_id, None, analysis, db_path=db_path)
    saved = save_findings(assessment_id, analysis["findings"], db_path=db_path)
    assert saved == len(analysis["findings"])
    assert _count(db_path, "detected_findings") == saved


def test_recommended_controls_are_persisted(tmp_path):
    db_path = tmp_path / "aiwra.db"
    project_id = create_project("Controls", db_path=db_path)
    analysis = analyze_workflow(get_example_text("hr_candidate_screening"))
    assessment_id = save_assessment(project_id, None, analysis, db_path=db_path)
    saved = save_recommended_controls(assessment_id, analysis["recommended_controls"], db_path=db_path)
    assert saved == len(analysis["recommended_controls"])
    assert _count(db_path, "recommended_controls") == saved


def test_simulation_run_is_persisted_and_visible_in_metrics(tmp_path):
    db_path = tmp_path / "aiwra.db"
    project_id = create_project("Simulation", db_path=db_path)
    analysis = analyze_workflow(get_example_text("logistics_operations"))
    assessment_id = save_assessment(project_id, None, analysis, db_path=db_path)
    selected = default_control_selection(analysis["recommended_controls"])
    simulation = simulate_residual_risk(analysis["risk_matrix"], selected, analysis["recommended_controls"])
    simulation_id = save_simulation_run(assessment_id, simulation, db_path=db_path)
    metrics = get_dashboard_metrics(db_path)
    assert simulation_id > 0
    assert metrics["simulation_count"] == 1
    assert metrics["average_simulated_reduction"] >= 0


def test_report_persistence_and_lookup(tmp_path):
    db_path = tmp_path / "aiwra.db"
    project_id = create_project("Reports", db_path=db_path)
    analysis = analyze_workflow(get_example_text("customer_support"))
    assessment_id = save_assessment(project_id, None, analysis, db_path=db_path)
    report_id = save_report(assessment_id, project_id, "Local Report", "# Report", analysis=analysis, db_path=db_path)
    assert list_reports(db_path)[0]["id"] == report_id
    assert get_report(report_id, db_path)["markdown"] == "# Report"


def test_audit_event_creation(tmp_path):
    db_path = tmp_path / "aiwra.db"
    init_db(db_path, seed=True)
    event_id = create_audit_event("checked", "test", 7, {"ok": True}, db_path=db_path)
    assert event_id > 0
    assert _count(db_path, "audit_events") >= 1


def test_dashboard_metrics_empty_without_saved_analysis(tmp_path):
    db_path = tmp_path / "aiwra.db"
    init_db(db_path, seed=True)
    metrics = get_dashboard_metrics(db_path)
    assert metrics["saved_analyses"] == 0
    assert metrics["average_risk"] == 0


def test_explicit_full_save_flow_populates_dashboard(tmp_path):
    db_path = tmp_path / "aiwra.db"
    project_id = create_project("Full save", db_path=db_path)
    analysis = analyze_workflow(get_example_text("soc_alert_triage"))
    workflow_id = save_workflow(project_id, "SOC", get_example_text("soc_alert_triage"), db_path=db_path)
    save_workflow_steps(workflow_id, analysis["steps"], db_path=db_path)
    assessment_id = save_assessment(project_id, workflow_id, analysis, db_path=db_path)
    save_findings(assessment_id, analysis["findings"], db_path=db_path)
    save_recommended_controls(assessment_id, analysis["recommended_controls"], db_path=db_path)
    save_report(assessment_id, project_id, "SOC report", "# SOC", json_summary=json.dumps({"ok": True}), db_path=db_path)
    metrics = get_dashboard_metrics(db_path)
    assert metrics["saved_analyses"] == 1
    assert metrics["top_risk_categories"]
    assert metrics["latest_reports"]


def test_seeded_demo_content_is_marked_synthetic(tmp_path):
    db_path = tmp_path / "aiwra.db"
    init_db(db_path, seed=True)
    with sqlite3.connect(db_path) as connection:
        payloads = [json.loads(row[0]) for row in connection.execute("SELECT scenario_json FROM demo_scenarios")]
    assert payloads
    assert all(payload["synthetic"] is True for payload in payloads)
    assert all("synthetic" in payload["demo_notes"].casefold() for payload in payloads)
