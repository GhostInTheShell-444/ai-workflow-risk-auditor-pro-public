from __future__ import annotations

import re
from pathlib import Path

from analyzer import analyze_workflow
from design_tokens import REQUIRED_2026_TOKEN_KEYS, REQUIRED_THEME_KEYS, THEME_OPTIONS, THEMES, color_css_variables
from examples import get_example_text
from score_explainability import build_explainability_payload


ROOT = Path(__file__).resolve().parents[1]


def test_theme_options_and_css_variables_exist():
    assert set(THEME_OPTIONS) == {"light", "dark", "system"}
    for theme in ("light", "dark", "system"):
        assert theme in THEMES
    for theme in ("light", "dark"):
        assert REQUIRED_THEME_KEYS.issubset(THEMES[theme])
        assert REQUIRED_2026_TOKEN_KEYS.issubset(THEMES[theme])

    css = color_css_variables("dark")
    assert "--aiwra-bg" in css
    assert "--aiwra-page-bg" in css
    assert "--aiwra-sidebar-bg" in css
    assert "--aiwra-card-bg" in css
    assert "--aiwra-elevated-card-bg" in css
    assert "--aiwra-panel-bg" in css
    assert "--aiwra-input-bg" in css
    assert "--aiwra-button-primary-bg" in css
    assert "--aiwra-button-secondary-bg" in css
    assert "--aiwra-button-ghost-bg" in css
    assert "--aiwra-button-danger-bg" in css
    assert "--aiwra-button-disabled-bg" in css
    assert "--aiwra-button-download-bg" in css
    assert "--aiwra-focus-ring" in css
    assert "--aiwra-state-warning-bg" in css
    assert "--aiwra-gradient" in css
    assert "--aiwra-surface" in css
    assert "--aiwra-text" in css
    assert "--aiwra-bg-app-light" in css
    assert "--aiwra-bg-app-dark" in css
    assert "--aiwra-primary-action" in css
    assert "--aiwra-danger-action" in css
    assert "--aiwra-radius-md" in css
    assert "--aiwra-spacing-md" in css
    assert "--aiwra-font-mono" in css


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


def test_no_visible_css_local_copy_in_locales():
    blocked = ["CSS local", "local CSS", "CSS מקומי"]
    offenders = []
    for path in (ROOT / "locales").glob("*.json"):
        text = path.read_text(encoding="utf-8")
        for phrase in blocked:
            if phrase in text:
                offenders.append((path.name, phrase))

    assert offenders == []


def test_theme_tokens_include_premium_color_roles():
    required_roles = {
        "page_bg",
        "shell_bg",
        "sidebar_bg",
        "workbench_bg",
        "panel_bg",
        "card_bg",
        "elevated_card_bg",
        "input_bg",
        "text_primary",
        "text_secondary",
        "muted",
        "disabled_text",
        "border",
        "border_soft",
        "focus_ring",
        "primary",
        "accent",
        "local",
        "advisory",
        "info",
        "success",
        "warning",
        "danger",
        "critical",
        "high",
        "medium",
        "low",
    }
    for theme in ("light", "dark"):
        assert required_roles.issubset(THEMES[theme])

    css = color_css_variables("light")
    for variable in (
        "--aiwra-page-bg",
        "--aiwra-shell-bg",
        "--aiwra-workbench-bg",
        "--aiwra-disabled-text",
        "--aiwra-border-soft",
        "--aiwra-local",
        "--aiwra-advisory",
        "--aiwra-danger",
    ):
        assert variable in css


def test_theme_tokens_include_loading_and_advisory_roles():
    for theme in ("light", "dark"):
        assert THEMES[theme]["advisory"]
        assert THEMES[theme]["loading"]
        assert THEMES[theme]["loading_border"]
        assert THEMES[theme]["loading_deterministic"]
        assert THEMES[theme]["loading_local_ai"]
        assert THEMES[theme]["loading_simulation"]
        assert THEMES[theme]["loading_export"]

    css = color_css_variables("dark")
    assert "--aiwra-loading" in css
    assert "--aiwra-loading-border" in css
    assert "--aiwra-loading-deterministic" in css
    assert "--aiwra-loading-local-ai" in css
    assert "--aiwra-loading-simulation" in css
    assert "--aiwra-loading-export" in css
    assert "--aiwra-advisory" in css


def test_header_theme_toggle_replaces_legacy_theme_selector():
    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    theme_block = re.search(r"def _theme_selector\(language: str\).*?(?=\ndef _scenario_options)", app_source, flags=re.S)

    assert theme_block is not None
    assert 'theme_mode_selector' not in app_source
    assert 'THEME_MODE_TOGGLE_KEY = "theme_mode_toggle_header"' in app_source
    assert "st.button(" in theme_block.group(0)
    assert 'key="theme_action_toggle_header"' in theme_block.group(0)
    assert "st.toggle(" not in theme_block.group(0)
    assert "st.radio(" not in theme_block.group(0)
    assert "index=" not in theme_block.group(0)
    assert "value=" not in theme_block.group(0)
    assert "theme_label" in theme_block.group(0)
    assert "on_click=_toggle_theme_header" in theme_block.group(0)


def test_generated_theme_css_has_no_critical_duplicate_variables():
    for theme in ("light", "dark"):
        css = color_css_variables(theme)
        for variable in ("--aiwra-border-soft", "--aiwra-radius-sm", "--aiwra-font-mono"):
            assert css.count(f"{variable}:") == 1
