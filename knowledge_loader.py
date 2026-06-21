from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"

RISK_PATTERN_KEYS = {
    "id",
    "version",
    "name",
    "category",
    "severity",
    "languages_supported",
    "enabled",
    "keywords",
    "regex_pattern",
    "risk_factor_mapping",
    "explanation",
    "recommended_control_ids",
}
CONTROL_KEYS = {
    "id",
    "version",
    "name",
    "category",
    "effectiveness",
    "enabled",
    "description",
    "reduced_risk_factors",
    "implementation_guidance",
    "human_role_if_relevant",
}
DATA_CATEGORY_KEYS = {
    "id",
    "name",
    "sensitivity",
    "synthetic_examples",
    "privacy_notes",
    "recommended_handling",
}
EXPLANATION_CARD_KEYS = {
    "id",
    "topic",
    "title",
    "short_explanation",
    "why_it_matters",
    "related_ui_area",
}


def _read_json_list(filename: str) -> list[dict[str, Any]]:
    path = KNOWLEDGE_BASE_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError(f"{filename} must contain a JSON list.")
    return [item for item in payload if isinstance(item, dict)]


def _validate_items(items: list[dict[str, Any]], required_keys: set[str], filename: str) -> None:
    for index, item in enumerate(items):
        missing = required_keys - set(item)
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(f"{filename}[{index}] is missing required keys: {missing_list}")


@lru_cache(maxsize=None)
def load_risk_patterns(enabled_only: bool = True) -> list[dict[str, Any]]:
    items = _read_json_list("risk_patterns.json")
    _validate_items(items, RISK_PATTERN_KEYS, "risk_patterns.json")
    return [item for item in items if bool(item.get("enabled"))] if enabled_only else items


@lru_cache(maxsize=None)
def load_control_library(enabled_only: bool = True) -> list[dict[str, Any]]:
    items = _read_json_list("control_library.json")
    _validate_items(items, CONTROL_KEYS, "control_library.json")
    return [item for item in items if bool(item.get("enabled"))] if enabled_only else items


@lru_cache(maxsize=None)
def load_data_categories() -> list[dict[str, Any]]:
    items = _read_json_list("data_categories.json")
    _validate_items(items, DATA_CATEGORY_KEYS, "data_categories.json")
    return items


@lru_cache(maxsize=None)
def load_workflow_templates(enabled_only: bool = True) -> list[dict[str, Any]]:
    items = _read_json_list("workflow_templates.json")
    return [item for item in items if bool(item.get("enabled", True))] if enabled_only else items


@lru_cache(maxsize=None)
def load_demo_scenarios(enabled_only: bool = True) -> list[dict[str, Any]]:
    items = _read_json_list("demo_scenarios.json")
    return [item for item in items if bool(item.get("enabled", True))] if enabled_only else items


@lru_cache(maxsize=None)
def load_explanation_cards() -> list[dict[str, Any]]:
    items = _read_json_list("explanation_cards.json")
    _validate_items(items, EXPLANATION_CARD_KEYS, "explanation_cards.json")
    return items


def load_knowledge_base() -> dict[str, list[dict[str, Any]]]:
    return {
        "risk_patterns": load_risk_patterns(),
        "control_library": load_control_library(),
        "data_categories": load_data_categories(),
        "workflow_templates": load_workflow_templates(),
        "demo_scenarios": load_demo_scenarios(),
        "explanation_cards": load_explanation_cards(),
    }


def get_control_map() -> dict[str, dict[str, Any]]:
    return {str(control["id"]): control for control in load_control_library()}


def get_explanation_card(topic_or_id: str) -> dict[str, Any] | None:
    requested = topic_or_id.casefold()
    for card in load_explanation_cards():
        if str(card.get("id", "")).casefold() == requested or str(card.get("topic", "")).casefold() == requested:
            return card
    return None


def knowledge_counts() -> dict[str, int]:
    kb = load_knowledge_base()
    return {key: len(value) for key, value in kb.items()}
