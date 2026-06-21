from __future__ import annotations

from pathlib import Path

from analyzer import analyze_workflow
from design_tokens import REQUIRED_THEME_KEYS, THEME_OPTIONS, THEMES, color_css_variables
from examples import get_example_text
from score_explainability import build_explainability_payload


ROOT = Path(__file__).resolve().parents[1]


def test_theme_options_and_css_variables_exist():
    assert set(THEME_OPTIONS) == {"light", "dark", "system"}
    for theme in ("light", "dark", "system"):
        assert theme in THEMES
    for theme in ("light", "dark"):
        assert REQUIRED_THEME_KEYS.issubset(THEMES[theme])

    css = color_css_variables("dark")
    assert "--aiwra-bg" in css
    assert "--aiwra-surface" in css
    assert "--aiwra-text" in css


def test_professional_copy_is_absent_from_ui_sources():
    blocked = [
        "Expliquer " + "comme",
        "enfant " + "de 12 ans",
        "Explain " + "like",
        "EL" + "I5",
        "du" + "mmy",
        "for " + "dummies",
        "ki" + "d",
        "chi" + "ld",
    ]
    source_paths = [ROOT / "app.py"]
    source_paths.extend(ROOT.glob("*.py"))
    source_paths.extend(path for path in (ROOT / "locales").glob("*.json"))
    source_paths.extend(path for path in (ROOT / "docs").rglob("*") if path.is_file())

    offenders = []
    for path in source_paths:
        if ".git" in path.parts or ".venv" in path.parts or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for phrase in blocked:
            if phrase in text:
                offenders.append((path.relative_to(ROOT).as_posix(), phrase))
    assert offenders == []


def test_french_score_explanation_has_no_english_fragments():
    analysis = analyze_workflow(get_example_text("customer_support"))
    explanation = build_explainability_payload(analysis, None, "fr")["score_explanation_simple"]
    blocked = [
        "Critical " + "estimated",
        "estimated " + "risk",
        "evidence " + "item",
        "mapped " + "from",
        "submitted " + "workflow",
    ]
    for phrase in blocked:
        assert phrase not in explanation
