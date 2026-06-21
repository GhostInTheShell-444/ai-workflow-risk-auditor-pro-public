from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from knowledge_loader import load_control_library, load_demo_scenarios, load_explanation_cards


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "aiwra.db"
SCHEMA_VERSION = 1


SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    workflow_text TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'user',
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS workflow_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    step_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY(workflow_id) REFERENCES workflows(id)
);

CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    workflow_id INTEGER,
    workflow_type TEXT NOT NULL,
    raw_score INTEGER NOT NULL,
    severity TEXT NOT NULL,
    risk_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(workflow_id) REFERENCES workflows(id)
);

CREATE TABLE IF NOT EXISTS detected_findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    finding_id TEXT NOT NULL,
    category TEXT NOT NULL,
    severity TEXT NOT NULL,
    confidence REAL NOT NULL,
    evidence TEXT NOT NULL,
    matched_rule_id TEXT NOT NULL,
    step_reference TEXT NOT NULL,
    explanation TEXT NOT NULL,
    controls_json TEXT NOT NULL,
    factors_json TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(assessment_id) REFERENCES assessments(id)
);

CREATE TABLE IF NOT EXISTS risk_factors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    factor_key TEXT NOT NULL,
    weight INTEGER NOT NULL,
    impact INTEGER NOT NULL,
    likelihood INTEGER NOT NULL,
    confidence REAL NOT NULL,
    score_impact INTEGER NOT NULL,
    FOREIGN KEY(assessment_id) REFERENCES assessments(id)
);

CREATE TABLE IF NOT EXISTS control_library (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    effectiveness INTEGER NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    definition_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recommended_controls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    control_id TEXT NOT NULL,
    name TEXT NOT NULL,
    reason TEXT NOT NULL,
    risk_factors_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(assessment_id) REFERENCES assessments(id)
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    selected_controls_json TEXT NOT NULL,
    raw_score INTEGER NOT NULL,
    residual_score INTEGER NOT NULL,
    reduction INTEGER NOT NULL,
    severity_before TEXT NOT NULL,
    severity_after TEXT NOT NULL,
    explanation TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(assessment_id) REFERENCES assessments(id)
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    markdown TEXT NOT NULL,
    json_summary TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(assessment_id) REFERENCES assessments(id),
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    details_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_articles (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_json TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS demo_scenarios (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    workflow_text TEXT NOT NULL,
    scenario_json TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1
);
"""


def _coerce_path(db_path: str | Path | None = None) -> Path:
    return Path(db_path) if db_path is not None else DB_PATH


def _connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = _coerce_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = _coerce_path(db_path)
    if not path.exists():
        init_db(path)
    return _connect(path)


def init_db(db_path: str | Path | None = None, seed: bool = True) -> Path:
    path = _coerce_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(path) as connection:
        connection.executescript(SCHEMA)
        connection.execute(
            "INSERT OR IGNORE INTO schema_version(version) VALUES (?)",
            (SCHEMA_VERSION,),
        )
    if seed:
        seed_database(path)
    return path


def seed_database(db_path: str | Path | None = None) -> None:
    path = _coerce_path(db_path)
    with _connect(path) as connection:
        for control in load_control_library():
            connection.execute(
                """
                INSERT OR REPLACE INTO control_library
                (id, name, category, effectiveness, enabled, definition_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    control["id"],
                    control["name"],
                    control["category"],
                    int(control["effectiveness"]),
                    1 if control.get("enabled", True) else 0,
                    json.dumps(control, ensure_ascii=False),
                ),
            )

        for card in load_explanation_cards():
            content = f"{card['short_explanation']}\n\n{card['why_it_matters']}"
            connection.execute(
                """
                INSERT OR REPLACE INTO knowledge_articles
                (id, topic, title, content, source_json, enabled)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    card["id"],
                    card["topic"],
                    card["title"],
                    content,
                    json.dumps(card, ensure_ascii=False),
                    1,
                ),
            )

        demo_project_id = connection.execute(
            """
            INSERT OR IGNORE INTO projects(id, name, description, is_demo)
            VALUES (1, ?, ?, 1)
            """,
            (
                "Synthetic Demo Project",
                "Seeded local demo project with synthetic and anonymized scenarios.",
            ),
        ).lastrowid
        if not demo_project_id:
            demo_project_id = 1

        for scenario in load_demo_scenarios():
            connection.execute(
                """
                INSERT OR REPLACE INTO demo_scenarios
                (id, name, workflow_text, scenario_json, enabled)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    scenario["id"],
                    scenario["name"],
                    scenario["workflow_text"],
                    json.dumps(scenario, ensure_ascii=False),
                    1 if scenario.get("enabled", True) else 0,
                ),
            )


def reset_demo_db(db_path: str | Path | None = None) -> Path:
    path = _coerce_path(db_path)
    if path.exists():
        path.unlink()
    return init_db(path, seed=True)


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]
