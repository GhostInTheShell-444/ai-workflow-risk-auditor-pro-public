from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
LOCALES_DIR = BASE_DIR / "locales"

LANGUAGES: dict[str, dict[str, str | bool]] = {
    "en": {"name": "English", "native": "English", "rtl": False},
    "fr": {"name": "French", "native": "Français", "rtl": False},
    "he": {"name": "Hebrew", "native": "עברית", "rtl": True},
}

SEVERITY_KEYS = {"critical", "high", "medium", "low", "unknown"}
STATUS_KEYS = {
    "detected",
    "calculated",
    "simulated",
    "recommended",
    "uncertain",
    "needs_human_review",
    "read_only",
    "demo",
    "local_only",
    "not_available",
}

COUNT_FORMATS: dict[str, dict[str, str]] = {
    "en": {
        "evidence": "from {count} detected evidence signal(s)",
        "finding": "{count} finding(s)",
        "saved_report": "{count} local report(s)",
        "simulation": "{count} saved run(s)",
    },
    "fr": {
        "evidence": "à partir de {count} indice(s) détecté(s)",
        "finding": "{count} constat(s)",
        "saved_report": "{count} rapport(s) local(aux)",
        "simulation": "{count} simulation(s) sauvegardée(s)",
    },
    "he": {
        "evidence": "מתוך {count} ראיות שזוהו",
        "finding": "{count} ממצאים",
        "saved_report": "{count} דוחות מקומיים",
        "simulation": "{count} הרצות שמורות",
    },
}

SHOWING_RESULTS_FORMATS = {
    "en": "Displaying {visible} of {total} matching findings.",
    "fr": "Affichage de {visible} constat(s) sur {total} après filtrage.",
    "he": "מוצגים {visible} מתוך {total} ממצאים לאחר סינון.",
}


@lru_cache(maxsize=None)
def load_locale(language: str) -> dict[str, Any]:
    code = language if language in LANGUAGES else "en"
    path = LOCALES_DIR / f"{code}.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def available_languages() -> dict[str, dict[str, str | bool]]:
    return LANGUAGES.copy()


def language_label(language: str) -> str:
    meta = LANGUAGES.get(language, LANGUAGES["en"])
    return f"{meta['native']} ({meta['name']})"


def is_rtl(language: str) -> bool:
    return bool(LANGUAGES.get(language, LANGUAGES["en"])["rtl"])


def t(key: str, language: str = "en", default: str | None = None) -> str:
    locale = load_locale(language)
    if key in locale:
        return str(locale[key])
    fallback = load_locale("en")
    if key in fallback:
        return str(fallback[key])
    return default if default is not None else key


def _normalize_key(value: object, fallback: str = "unknown") -> str:
    key = str(value or fallback).casefold().strip().replace("-", "_").replace(" ", "_")
    return key or fallback


def translate_severity(value: object, language: str = "en") -> str:
    key = _normalize_key(value)
    if key not in SEVERITY_KEYS:
        key = "unknown"
    return t(f"risk_level_{key}", language, key.title())


def translate_status(value: object, language: str = "en") -> str:
    key = _normalize_key(value, "uncertain")
    if key not in STATUS_KEYS:
        key = "uncertain"
    return t(f"status_{key}_label", language, key.replace("_", " ").title())


def translate_category(value: object, language: str = "en") -> str:
    key = _normalize_key(value)
    if key == "all":
        return t("all_option", language, "All")
    translated = t(f"kb_category_{key}", language, default="")
    if translated:
        return translated
    translated = t(f"category_{key}", language, default="")
    if translated:
        return translated
    return key.replace("_", " ").title()


def translate_filter_option(value: object, language: str = "en") -> str:
    key = _normalize_key(value, "all")
    if key == "all":
        return t("all_option", language, "All")
    if key in SEVERITY_KEYS:
        return translate_severity(key, language)
    if key in STATUS_KEYS:
        return translate_status(key, language)
    return translate_category(key, language)


def format_count(key: str, count: int, language: str = "en") -> str:
    code = language if language in COUNT_FORMATS else "en"
    template = COUNT_FORMATS[code].get(key) or COUNT_FORMATS["en"].get(key) or "{count}"
    return template.format(count=count)


def format_showing_results(visible: int, total: int, language: str = "en") -> str:
    template = SHOWING_RESULTS_FORMATS.get(language, SHOWING_RESULTS_FORMATS["en"])
    return template.format(visible=visible, total=total)
