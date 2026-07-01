from __future__ import annotations

import json
import re
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
    "effectiveness_note",
    "implementation_status",
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
RISK_FACTOR_GROUP_KEYS = {"id", "title", "factors", "review_note", "runtime_status"}
CONTROL_EFFECT_KEYS = {
    "control_id",
    "mapped_factors",
    "assumption",
    "evidence_required",
    "limitation",
    "runtime_status",
}
FRAMEWORK_MAPPING_KEYS = {
    "category",
    "local_topics",
    "mapping_type",
    "claim_boundary",
    "runtime_status",
}
REVIEW_QUESTION_KEYS = {"id", "factor", "question", "runtime_status"}

SEVERITIES = {"low", "medium", "high", "critical"}
REFERENCE_ONLY = "reference_only"


def _read_json_list(filename: str) -> list[dict[str, Any]]:
    path = KNOWLEDGE_BASE_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError(f"{filename} must contain a JSON list.")
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"{filename}[{index}] must be a JSON object.")
    return payload


def _validate_items(items: list[dict[str, Any]], required_keys: set[str], filename: str) -> None:
    for index, item in enumerate(items):
        missing = required_keys - set(item)
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(f"{filename}[{index}] is missing required keys: {missing_list}")


def _require_string(item: dict[str, Any], key: str, filename: str, index: int) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{filename}[{index}].{key} must be a non-empty string.")
    return value


def _require_string_list(item: dict[str, Any], key: str, filename: str, index: int) -> list[str]:
    value = item.get(key)
    if not isinstance(value, list) or not value or any(not isinstance(entry, str) or not entry.strip() for entry in value):
        raise ValueError(f"{filename}[{index}].{key} must be a non-empty list of strings.")
    if len(value) != len(set(value)):
        raise ValueError(f"{filename}[{index}].{key} contains duplicate values.")
    return value


def _validate_unique(items: list[dict[str, Any]], key: str, filename: str) -> None:
    values = [_require_string(item, key, filename, index) for index, item in enumerate(items)]
    if len(values) != len(set(values)):
        raise ValueError(f"{filename} contains duplicate {key} values.")


def _validate_reference_only(items: list[dict[str, Any]], filename: str) -> None:
    for index, item in enumerate(items):
        if item.get("runtime_status") != REFERENCE_ONLY:
            raise ValueError(f"{filename}[{index}].runtime_status must be {REFERENCE_ONLY!r}.")


@lru_cache(maxsize=None)
def load_risk_patterns(enabled_only: bool = True) -> list[dict[str, Any]]:
    items = _read_json_list("risk_patterns.json")
    _validate_items(items, RISK_PATTERN_KEYS, "risk_patterns.json")
    _validate_unique(items, "id", "risk_patterns.json")
    for index, item in enumerate(items):
        _require_string(item, "version", "risk_patterns.json", index)
        _require_string(item, "name", "risk_patterns.json", index)
        _require_string(item, "category", "risk_patterns.json", index)
        _require_string(item, "explanation", "risk_patterns.json", index)
        if item.get("severity") not in SEVERITIES:
            raise ValueError(f"risk_patterns.json[{index}].severity is invalid.")
        if not isinstance(item.get("enabled"), bool):
            raise ValueError(f"risk_patterns.json[{index}].enabled must be boolean.")
        _require_string_list(item, "languages_supported", "risk_patterns.json", index)
        _require_string_list(item, "keywords", "risk_patterns.json", index)
        _require_string_list(item, "risk_factor_mapping", "risk_patterns.json", index)
        _require_string_list(item, "recommended_control_ids", "risk_patterns.json", index)
        regex_pattern = item.get("regex_pattern")
        if regex_pattern is not None:
            if not isinstance(regex_pattern, str) or not regex_pattern.strip():
                raise ValueError(f"risk_patterns.json[{index}].regex_pattern must be null or a non-empty string.")
            try:
                re.compile(regex_pattern)
            except re.error as exc:
                raise ValueError(f"risk_patterns.json[{index}].regex_pattern is invalid: {exc}") from exc
    return [item for item in items if bool(item.get("enabled"))] if enabled_only else items


@lru_cache(maxsize=None)
def load_control_library(enabled_only: bool = True) -> list[dict[str, Any]]:
    items = _read_json_list("control_library.json")
    _validate_items(items, CONTROL_KEYS, "control_library.json")
    _validate_unique(items, "id", "control_library.json")
    for index, item in enumerate(items):
        for key in (
            "version",
            "name",
            "category",
            "description",
            "implementation_guidance",
            "human_role_if_relevant",
            "effectiveness_note",
        ):
            _require_string(item, key, "control_library.json", index)
        if item.get("implementation_status") != "recommended_not_verified":
            raise ValueError(
                f"control_library.json[{index}].implementation_status must be 'recommended_not_verified'."
            )
        if not isinstance(item.get("enabled"), bool):
            raise ValueError(f"control_library.json[{index}].enabled must be boolean.")
        effectiveness = item.get("effectiveness")
        if isinstance(effectiveness, bool) or not isinstance(effectiveness, int) or not 0 <= effectiveness <= 5:
            raise ValueError(f"control_library.json[{index}].effectiveness must be an integer from 0 to 5.")
        reductions = item.get("reduced_risk_factors")
        if not isinstance(reductions, dict) or not reductions:
            raise ValueError(f"control_library.json[{index}].reduced_risk_factors must be a non-empty object.")
        for factor, reduction in reductions.items():
            if not isinstance(factor, str) or not factor.strip():
                raise ValueError(f"control_library.json[{index}] contains an invalid reduced risk factor.")
            if isinstance(reduction, bool) or not isinstance(reduction, int) or reduction < 0:
                raise ValueError(f"control_library.json[{index}] contains an invalid heuristic reduction.")
    return [item for item in items if bool(item.get("enabled"))] if enabled_only else items


@lru_cache(maxsize=None)
def load_data_categories() -> list[dict[str, Any]]:
    items = _read_json_list("data_categories.json")
    _validate_items(items, DATA_CATEGORY_KEYS, "data_categories.json")
    _validate_unique(items, "id", "data_categories.json")
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
    _validate_unique(items, "id", "explanation_cards.json")
    return items


@lru_cache(maxsize=None)
def load_risk_factors_v2() -> list[dict[str, Any]]:
    items = _read_json_list("risk_factors_v2.json")
    _validate_items(items, RISK_FACTOR_GROUP_KEYS, "risk_factors_v2.json")
    _validate_unique(items, "id", "risk_factors_v2.json")
    _validate_reference_only(items, "risk_factors_v2.json")
    factors: list[str] = []
    for index, item in enumerate(items):
        _require_string(item, "title", "risk_factors_v2.json", index)
        _require_string(item, "review_note", "risk_factors_v2.json", index)
        factors.extend(_require_string_list(item, "factors", "risk_factors_v2.json", index))
    if len(factors) != len(set(factors)):
        raise ValueError("risk_factors_v2.json assigns a factor to more than one group.")
    return items


@lru_cache(maxsize=None)
def load_control_effects_v2() -> list[dict[str, Any]]:
    items = _read_json_list("control_effects_v2.json")
    _validate_items(items, CONTROL_EFFECT_KEYS, "control_effects_v2.json")
    _validate_unique(items, "control_id", "control_effects_v2.json")
    _validate_reference_only(items, "control_effects_v2.json")
    for index, item in enumerate(items):
        _require_string_list(item, "mapped_factors", "control_effects_v2.json", index)
        for key in ("assumption", "evidence_required", "limitation"):
            _require_string(item, key, "control_effects_v2.json", index)
    return items


@lru_cache(maxsize=None)
def load_framework_mappings_v2() -> list[dict[str, Any]]:
    items = _read_json_list("framework_mappings_v2.json")
    _validate_items(items, FRAMEWORK_MAPPING_KEYS, "framework_mappings_v2.json")
    _validate_unique(items, "category", "framework_mappings_v2.json")
    _validate_reference_only(items, "framework_mappings_v2.json")
    for index, item in enumerate(items):
        _require_string_list(item, "local_topics", "framework_mappings_v2.json", index)
        _require_string(item, "claim_boundary", "framework_mappings_v2.json", index)
        if item.get("mapping_type") != "framework-inspired":
            raise ValueError(f"framework_mappings_v2.json[{index}].mapping_type must be 'framework-inspired'.")
    return items


@lru_cache(maxsize=None)
def load_review_questions_v2() -> list[dict[str, Any]]:
    items = _read_json_list("review_questions_v2.json")
    _validate_items(items, REVIEW_QUESTION_KEYS, "review_questions_v2.json")
    _validate_unique(items, "id", "review_questions_v2.json")
    _validate_reference_only(items, "review_questions_v2.json")
    for index, item in enumerate(items):
        _require_string(item, "factor", "review_questions_v2.json", index)
        question = _require_string(item, "question", "review_questions_v2.json", index)
        if not question.endswith("?"):
            raise ValueError(f"review_questions_v2.json[{index}].question must remain a question.")
    return items


def validate_knowledge_base() -> None:
    patterns = load_risk_patterns(enabled_only=False)
    controls = load_control_library(enabled_only=False)
    factor_groups = load_risk_factors_v2()
    effects = load_control_effects_v2()
    load_framework_mappings_v2()
    questions = load_review_questions_v2()
    load_data_categories()
    load_explanation_cards()

    control_ids = {str(control["id"]) for control in controls}
    known_factors = {
        str(factor)
        for pattern in patterns
        for factor in pattern["risk_factor_mapping"]
    }
    known_factors.update(
        str(factor)
        for group in factor_groups
        for factor in group["factors"]
    )

    for pattern in patterns:
        unknown_controls = set(pattern["recommended_control_ids"]) - control_ids
        if unknown_controls:
            raise ValueError(f"{pattern['id']} references unknown controls: {sorted(unknown_controls)}")
    for control in controls:
        unknown_factors = set(control["reduced_risk_factors"]) - known_factors
        if unknown_factors:
            raise ValueError(f"{control['id']} references unknown factors: {sorted(unknown_factors)}")
    for effect in effects:
        if effect["control_id"] not in control_ids:
            raise ValueError(f"control_effects_v2.json references unknown control: {effect['control_id']}")
        unknown_factors = set(effect["mapped_factors"]) - known_factors
        if unknown_factors:
            raise ValueError(f"{effect['control_id']} maps unknown factors: {sorted(unknown_factors)}")
    for question in questions:
        if question["factor"] not in known_factors:
            raise ValueError(f"{question['id']} references unknown factor: {question['factor']}")


def load_knowledge_base() -> dict[str, list[dict[str, Any]]]:
    validate_knowledge_base()
    return {
        "risk_patterns": load_risk_patterns(),
        "control_library": load_control_library(),
        "data_categories": load_data_categories(),
        "workflow_templates": load_workflow_templates(),
        "demo_scenarios": load_demo_scenarios(),
        "explanation_cards": load_explanation_cards(),
        "risk_factors_v2": load_risk_factors_v2(),
        "control_effects_v2": load_control_effects_v2(),
        "framework_mappings_v2": load_framework_mappings_v2(),
        "review_questions_v2": load_review_questions_v2(),
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
