from __future__ import annotations

from pathlib import Path
from typing import Any

from repositories import get_report, list_audit_events, list_reports


def load_report_history(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    return list_reports(db_path)


def open_report(report_id: int, db_path: str | Path | None = None) -> dict[str, Any] | None:
    return get_report(report_id, db_path)


def load_audit_trail(limit: int = 50, db_path: str | Path | None = None) -> list[dict[str, Any]]:
    return list_audit_events(limit, db_path)
