from __future__ import annotations

from pathlib import Path
from typing import Any

from repositories import get_dashboard_metrics


def load_dashboard_metrics(db_path: str | Path | None = None) -> dict[str, Any]:
    return get_dashboard_metrics(db_path)
