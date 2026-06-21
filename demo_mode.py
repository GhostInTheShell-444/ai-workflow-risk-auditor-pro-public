from __future__ import annotations

from typing import Any

from knowledge_loader import load_demo_scenarios


DEMO_STEPS = [
    "Select or create a local project.",
    "Choose a synthetic scenario or paste anonymized workflow text.",
    "Run the deterministic audit.",
    "Inspect evidence and risk matrix entries.",
    "Select controls and simulate residual risk.",
    "Save the report only when you intentionally want history.",
    "Open Reports and Dashboard to review local persistence.",
    "Download Markdown or JSON for the portfolio demo.",
]


def get_demo_steps() -> list[str]:
    return DEMO_STEPS.copy()


def get_demo_scenario_options() -> list[dict[str, Any]]:
    return load_demo_scenarios()
