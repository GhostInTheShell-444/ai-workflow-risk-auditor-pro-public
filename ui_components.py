from __future__ import annotations

import html
import textwrap
from collections import Counter, defaultdict
from typing import Any

import streamlit as st

from design_tokens import COLORS, FONT_STACK, color_css_variables, severity_token, status_token
from i18n import is_rtl, t, translate_category


SEVERITY_ORDER = ("critical", "high", "medium", "low", "unknown")


def _escape(value: object) -> str:
    return html.escape(str(value or ""))


def render_html(markup: str, target: Any | None = None) -> None:
    """Render custom HTML after normalizing indentation for Streamlit."""
    renderer = target if target is not None else st
    renderer.markdown(textwrap.dedent(str(markup)).strip(), unsafe_allow_html=True)


def humanize_key(value: object) -> str:
    return str(value or "unknown").replace("_", " ").strip().title()


def apply_global_styles(language: str, theme: str = "light") -> None:
    direction = "rtl" if is_rtl(language) else "ltr"
    align = "right" if is_rtl(language) else "left"
    selected_theme = str(theme or "system").casefold()
    base_theme = "light" if selected_theme == "system" else selected_theme
    system_theme_css = ""
    if selected_theme == "system":
        system_theme_css = f"""
        @media (prefers-color-scheme: dark) {{
            :root {{
                {color_css_variables("dark")}
                color-scheme: dark;
            }}
        }}
        """
    rtl_css = ""
    if is_rtl(language):
        rtl_css = """
        .aiwra-shell-header,
        .aiwra-settings-bar,
        .aiwra-hero,
        .aiwra-workbench,
        .aiwra-workbench-frame,
        .aiwra-mission-pulse,
        .aiwra-pipeline-strip,
        .aiwra-command-cockpit,
        .aiwra-status-strip,
        .aiwra-bento,
        .aiwra-cockpit,
        .aiwra-card,
        .aiwra-state-panel,
        .aiwra-section,
        .aiwra-detail-grid,
        .aiwra-timeline-item,
        .aiwra-loading-panel {
            direction: rtl;
            text-align: right;
        }
        [data-testid="stTextArea"] textarea,
        [data-testid="stTextAreaRootElement"] textarea {
            direction: rtl;
            text-align: right;
            unicode-bidi: plaintext;
        }
        .aiwra-code,
        .aiwra-prompt,
        .aiwra-technical,
        .st-key-sidebar_ollama_model input,
        .st-key-sidebar_ollama_model [data-baseweb="select"],
        .st-key-local_ai_selected_model input,
        .st-key-local_ai_selected_model [data-baseweb="select"],
        bdi,
        pre,
        code {
            direction: ltr;
            text-align: left;
            unicode-bidi: isolate;
        }
        """
    render_html(
        f"""
        <style>
        :root {{
            {color_css_variables(base_theme)}
            --aiwra-font-stack: {FONT_STACK};
            --aiwra-radius: var(--aiwra-radius-md);
            --aiwra-focus: 0 0 0 3px color-mix(in srgb, var(--aiwra-focus-ring) 34%, transparent);
            color-scheme: {"dark" if base_theme == "dark" else "light"};
        }}
        {system_theme_css}
        html, body, .stApp {{
            font-family: var(--aiwra-font-stack);
            color: var(--aiwra-text-primary);
            font-size: 15px;
            line-height: 1.6;
        }}
        [data-testid="stMarkdownContainer"],
        [data-testid="stWidgetLabel"],
        [data-testid="stTextInput"],
        [data-testid="stTextArea"],
        [data-testid="stSelectbox"],
        [data-testid="stRadio"],
        [data-testid="stCheckbox"],
        [data-testid="stToggle"],
        [data-testid="stButton"],
        [data-testid="stDownloadButton"] {{
            font-family: var(--aiwra-font-stack);
        }}
        .stApp,
        [data-testid="stAppViewContainer"] {{
            background:
                linear-gradient(180deg, color-mix(in srgb, var(--aiwra-shell-bg) 74%, var(--aiwra-page-bg)) 0%, var(--aiwra-page-bg) 18rem),
                var(--aiwra-page-bg);
            color: var(--aiwra-text-primary);
        }}
        [data-testid="stSidebar"] {{
            background:
                linear-gradient(180deg, color-mix(in srgb, var(--aiwra-primary) 7%, var(--aiwra-sidebar-bg)), var(--aiwra-sidebar-bg));
            border-inline-end: 1px solid var(--aiwra-border);
            box-shadow: 12px 0 36px color-mix(in srgb, var(--aiwra-shadow) 64%, transparent);
            color: var(--aiwra-text-primary) !important;
        }}
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarHeader"],
        [data-testid="stSidebar"] > div {{
            background: var(--aiwra-sidebar-bg) !important;
            color: var(--aiwra-text-primary) !important;
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [role="radiogroup"] label,
        [data-testid="stSidebar"] [data-baseweb="select"] *,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] *,
        [data-testid="stSidebar"] [data-testid="stCheckbox"] *,
        [data-testid="stSidebar"] [data-testid="stToggle"] * {{
            color: var(--aiwra-text-primary) !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea {{
            background: var(--aiwra-input-bg) !important;
            border-color: var(--aiwra-input-border) !important;
            color: var(--aiwra-text-primary) !important;
        }}
        [data-testid="stSidebar"] [role="radiogroup"],
        [data-testid="stSidebar"] [data-testid="stCheckbox"],
        [data-testid="stSidebar"] [data-testid="stToggle"] {{
            color: var(--aiwra-text-primary) !important;
        }}
        [data-testid="stSidebar"] button,
        [data-testid="stSidebarHeader"] button,
        [data-testid="collapsedControl"] button {{
            min-height: 2.25rem;
            color: var(--aiwra-text-primary) !important;
            background: color-mix(in srgb, var(--aiwra-elevated-card-bg) 88%, transparent) !important;
            border: 1px solid var(--aiwra-border) !important;
            border-radius: var(--aiwra-radius-sm) !important;
            box-shadow: none !important;
        }}
        [data-testid="stSidebar"] button:hover,
        [data-testid="stSidebarHeader"] button:hover,
        [data-testid="collapsedControl"] button:hover {{
            border-color: var(--aiwra-primary) !important;
            background: var(--aiwra-primary-soft) !important;
        }}
        [data-testid="stSidebar"] hr {{
            border-color: var(--aiwra-border);
        }}
        .aiwra-sidebar-brand {{
            margin: 0.35rem 0 1rem;
            padding: 0.9rem;
            border: 1px solid color-mix(in srgb, var(--aiwra-primary) 34%, var(--aiwra-border));
            border-radius: var(--aiwra-radius);
            background:
                linear-gradient(140deg, color-mix(in srgb, var(--aiwra-primary-soft) 70%, transparent), transparent),
                var(--aiwra-card-bg);
            box-shadow: 0 12px 28px color-mix(in srgb, var(--aiwra-shadow) 60%, transparent);
        }}
        .aiwra-sidebar-brand strong {{
            display: block;
            color: var(--aiwra-text-primary);
            font-size: 0.96rem;
            line-height: 1.35;
        }}
        .aiwra-sidebar-brand span {{
            display: block;
            margin-top: 0.32rem;
            color: var(--aiwra-muted);
            font-size: 0.76rem;
            line-height: 1.4;
        }}
        .aiwra-sidebar-divider {{
            margin: 1rem 0 0.7rem;
            padding-top: 0.72rem;
            border-top: 1px solid var(--aiwra-border);
            color: var(--aiwra-muted);
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0;
            text-transform: uppercase;
        }}
        [data-testid="stHeader"] {{
            background: color-mix(in srgb, var(--aiwra-page-bg) 92%, transparent) !important;
            backdrop-filter: blur(14px);
            border-bottom: 1px solid color-mix(in srgb, var(--aiwra-border) 70%, transparent);
            color: var(--aiwra-text-primary) !important;
        }}
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {{
            background: transparent !important;
            color: var(--aiwra-text-primary) !important;
        }}
        #MainMenu,
        [data-testid="stMainMenu"],
        [data-testid="stMainMenuButton"],
        footer,
        [data-testid="stStatusWidget"] {{
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }}
        [data-testid="stToolbar"] {{
            opacity: 0.34;
            transform: scale(0.92);
            transform-origin: top right;
            transition: opacity 160ms ease;
        }}
        [data-testid="stToolbar"]:hover {{
            opacity: 1;
        }}
        .block-container {{
            padding-top: 1.1rem;
            padding-bottom: 3rem;
            max-width: 1520px;
        }}
        .aiwra-root {{
            direction: {direction};
            text-align: {align};
        }}
        .aiwra-shell-header {{
            display: grid;
            grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
            gap: 0.9rem;
            align-items: stretch;
            margin: 0.15rem 0 0.9rem;
            padding: clamp(0.85rem, 1.4vw, 1.15rem);
            border: 1px solid color-mix(in srgb, var(--aiwra-primary) 32%, var(--aiwra-border));
            border-radius: var(--aiwra-radius-lg);
            background:
                linear-gradient(120deg, color-mix(in srgb, var(--aiwra-primary-soft) 76%, transparent), transparent 64%),
                linear-gradient(155deg, var(--aiwra-elevated-card-bg), var(--aiwra-shell-bg));
            box-shadow: var(--aiwra-shadow-md, 0 18px 46px var(--aiwra-shadow));
        }}
        .aiwra-shell-product {{
            min-width: 0;
        }}
        .aiwra-shell-kicker {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            color: var(--aiwra-low);
            background: var(--aiwra-low-soft);
            border: 1px solid var(--aiwra-low-border);
            border-radius: 999px;
            padding: 0.25rem 0.62rem;
            font-size: 0.75rem;
            font-weight: 800;
            line-height: 1.25;
        }}
        .aiwra-shell-heartbeat {{
            width: 0.48rem;
            height: 0.48rem;
            border-radius: 999px;
            background: currentColor;
            box-shadow: 0 0 0 0 color-mix(in srgb, currentColor 40%, transparent);
            animation: aiwra-local-heartbeat 3.4s ease-in-out infinite;
        }}
        .aiwra-shell-title {{
            margin: 0.55rem 0 0.3rem;
            color: var(--aiwra-text-primary);
            font-size: clamp(1.75rem, 2.2vw, 2.125rem);
            line-height: 1.08;
            font-weight: 850;
            letter-spacing: 0;
        }}
        .aiwra-shell-subtitle {{
            max-width: 880px;
            margin: 0;
            color: var(--aiwra-text-secondary);
            font-size: 0.98rem;
            line-height: 1.55;
        }}
        .aiwra-status-strip {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 12rem), 1fr));
            gap: 0.55rem;
        }}
        .aiwra-status-item {{
            min-width: 0;
            padding: 0.72rem;
            border: 1px solid var(--aiwra-border);
            border-radius: var(--aiwra-radius);
            background: color-mix(in srgb, var(--aiwra-card-bg) 86%, transparent);
        }}
        .aiwra-status-item span {{
            display: block;
            color: var(--aiwra-muted);
            font-size: 0.72rem;
            font-weight: 800;
            line-height: 1.25;
            text-transform: uppercase;
            letter-spacing: 0;
        }}
        .aiwra-status-item strong {{
            display: block;
            margin-top: 0.24rem;
            color: var(--aiwra-text-primary);
            font-size: 0.9rem;
            line-height: 1.3;
            overflow-wrap: anywhere;
        }}
        .aiwra-native-header {{
            margin: 0.1rem 0 0.5rem;
        }}
        .aiwra-native-header h1 {{
            margin-bottom: 0.15rem;
            font-size: clamp(1.75rem, 2.1vw, 2.125rem);
            line-height: 1.08;
            letter-spacing: 0;
        }}
        .aiwra-native-header p {{
            max-width: 940px;
            margin: 0;
            color: var(--aiwra-text-secondary);
            line-height: 1.45;
        }}
        .aiwra-status-native [data-testid="stVerticalBlock"] {{
            gap: 0.2rem;
        }}
        .aiwra-workbench {{
            margin: 0.55rem 0 1rem;
            padding: clamp(0.75rem, 1.4vw, 1rem);
            border: 1px solid color-mix(in srgb, var(--aiwra-primary) 34%, var(--aiwra-border));
            border-radius: var(--aiwra-radius-lg);
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--aiwra-primary-soft) 58%, transparent), transparent 52%),
                var(--aiwra-workbench-bg);
            box-shadow: 0 18px 46px color-mix(in srgb, var(--aiwra-shadow) 64%, transparent);
        }}
        .aiwra-workbench-title {{
            margin: 0 0 0.35rem;
            font-size: clamp(1.18rem, 1.7vw, 1.55rem);
            line-height: 1.18;
            color: var(--aiwra-text-primary);
            font-weight: 850;
        }}
        .aiwra-workbench p {{
            margin: 0 0 0.65rem;
            color: var(--aiwra-text-secondary);
            line-height: 1.5;
        }}
        .aiwra-workbench-support {{
            padding: 0.75rem;
            border: 1px solid var(--aiwra-border);
            border-radius: var(--aiwra-radius);
            background: var(--aiwra-elevated-card-bg);
        }}
        .aiwra-workbench-support h4 {{
            margin: 0 0 0.35rem;
            font-size: 0.98rem;
        }}
        .aiwra-command-cockpit {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 15rem), 1fr));
            gap: 0.7rem;
            align-items: stretch;
            margin: 0.65rem 0 0.85rem;
        }}
        .aiwra-command-card {{
            min-width: 0;
            min-height: 142px;
            padding: 0.85rem;
            border: 1px solid var(--command-border, var(--aiwra-border));
            border-radius: var(--aiwra-radius);
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--command-color, var(--aiwra-primary)) 8%, transparent), transparent 46%),
                var(--aiwra-card-bg);
            box-shadow: 0 10px 26px color-mix(in srgb, var(--aiwra-shadow) 55%, transparent);
            overflow-wrap: break-word;
            word-break: normal;
        }}
        .aiwra-command-title {{
            margin: 0 0 0.35rem;
            color: var(--aiwra-text-primary);
            font-size: 0.98rem;
            line-height: 1.28;
            font-weight: 820;
        }}
        .aiwra-command-card strong {{
            display: block;
            margin: 0.35rem 0;
            color: var(--command-color, var(--aiwra-primary));
            font-size: 1.12rem;
            line-height: 1.25;
        }}
        .aiwra-command-card p {{
            margin: 0;
            color: var(--aiwra-text-secondary);
            font-size: 0.85rem;
            line-height: 1.42;
        }}
        .aiwra-command-card .aiwra-technical {{
            max-width: 100%;
            overflow-wrap: anywhere;
        }}
        .aiwra-workbench-frame {{
            margin: 0.65rem 0 0.7rem;
            padding: clamp(0.85rem, 1.5vw, 1.15rem);
            border: 1px solid color-mix(in srgb, var(--aiwra-primary) 34%, var(--aiwra-border));
            border-radius: var(--aiwra-radius-lg);
            background:
                linear-gradient(145deg, color-mix(in srgb, var(--aiwra-primary-soft) 66%, transparent), transparent 58%),
                var(--aiwra-panel-bg);
            box-shadow: 0 18px 46px color-mix(in srgb, var(--aiwra-shadow) 60%, transparent);
        }}
        .aiwra-workbench-frame-title {{
            margin: 0 0 0.35rem;
            color: var(--aiwra-text-primary);
            font-size: clamp(1.22rem, 1.9vw, 1.75rem);
            line-height: 1.15;
            font-weight: 850;
        }}
        .aiwra-workbench-frame p {{
            margin: 0;
            max-width: 900px;
            color: var(--aiwra-text-secondary);
            line-height: 1.52;
        }}
        .aiwra-workbench-checks {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.72rem;
        }}
        .aiwra-workbench-check {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.32rem 0.62rem;
            border: 1px solid var(--aiwra-border);
            border-radius: 999px;
            color: var(--aiwra-text-secondary);
            background: var(--aiwra-surface-alt);
            font-size: 0.8rem;
            font-weight: 720;
        }}
        .aiwra-action-hint {{
            color: var(--aiwra-muted);
            font-size: 0.82rem;
            line-height: 1.35;
        }}
        .aiwra-state-panel {{
            display: grid;
            grid-template-columns: auto minmax(0, 1fr);
            gap: 0.7rem;
            align-items: flex-start;
            padding: 0.85rem;
            margin: 0.55rem 0 0.85rem;
            border: 1px solid var(--state-border, var(--aiwra-border));
            border-inline-start: 4px solid var(--state-color, var(--aiwra-primary));
            border-radius: var(--aiwra-radius);
            background: color-mix(in srgb, var(--state-bg, var(--aiwra-surface-alt)) 78%, var(--aiwra-card-bg));
        }}
        .aiwra-state-icon {{
            width: 2rem;
            height: 2rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: var(--aiwra-radius-sm);
            color: var(--state-color, var(--aiwra-primary));
            background: var(--state-bg, var(--aiwra-primary-soft));
            font-weight: 850;
        }}
        .aiwra-state-title {{
            margin: 0 0 0.2rem;
            color: var(--aiwra-text-primary);
            font-size: 0.98rem;
            line-height: 1.25;
            font-weight: 800;
        }}
        .aiwra-state-panel p {{
            margin: 0;
            color: var(--aiwra-text-secondary);
            line-height: 1.45;
            font-size: 0.9rem;
        }}
        .aiwra-state-panel small {{
            display: block;
            margin-top: 0.35rem;
            color: var(--aiwra-muted);
            line-height: 1.35;
        }}
        .st-key-settings_toolbar_header,
        .aiwra-settings-toolbar {{
            margin: 0 0 0.56rem;
            padding: 0;
            border: 0;
            background: transparent;
            direction: ltr !important;
            text-align: left;
        }}
        .st-key-settings_toolbar_header [data-testid="stHorizontalBlock"] {{
            align-items: center;
            gap: 0.4rem;
            direction: ltr !important;
        }}
        .st-key-language_control_cluster,
        .st-key-theme_control_cluster {{
            min-width: 0;
            margin-bottom: 0;
            direction: ltr !important;
        }}
        .st-key-language_control_cluster [data-testid="stHorizontalBlock"] {{
            width: fit-content;
            max-width: 100%;
            gap: 0.2rem;
            padding: 0.17rem;
            border: 1px solid var(--aiwra-border-soft);
            border-radius: 999px;
            background: color-mix(in srgb, var(--aiwra-elevated-card-bg) 82%, transparent);
        }}
        .st-key-theme_control_cluster [data-testid="stButton"] {{
            width: fit-content;
            margin-left: auto;
        }}
        .st-key-language_action_en button,
        .st-key-language_action_fr button,
        .st-key-language_action_he button,
        .st-key-theme_action_toggle_header button {{
            min-height: 2.12rem !important;
            margin: 0;
            padding: 0.18rem 0.72rem !important;
            border-radius: 999px !important;
            border: 1px solid var(--aiwra-border-soft) !important;
            color: var(--aiwra-text-primary) !important;
            background: color-mix(in srgb, var(--aiwra-card-bg) 82%, transparent) !important;
            box-shadow: none !important;
            font-size: 0.8rem;
            font-weight: 820;
            line-height: 1.15;
            white-space: nowrap;
            direction: ltr !important;
            unicode-bidi: isolate;
        }}
        .st-key-language_action_en button[kind="primary"],
        .st-key-language_action_fr button[kind="primary"],
        .st-key-language_action_he button[kind="primary"] {{
            border-color: color-mix(in srgb, var(--aiwra-primary) 42%, var(--aiwra-border)) !important;
            background: color-mix(in srgb, var(--aiwra-primary) 14%, var(--aiwra-elevated-card-bg)) !important;
            color: var(--aiwra-text-primary) !important;
            box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--aiwra-primary) 14%, transparent) !important;
        }}
        .st-key-theme_action_toggle_header button {{
            border-color: color-mix(in srgb, var(--aiwra-primary) 34%, var(--aiwra-border-soft)) !important;
            background: color-mix(in srgb, var(--aiwra-elevated-card-bg) 88%, transparent) !important;
            color: var(--aiwra-text-primary) !important;
            min-width: 7rem;
        }}
        .st-key-language_action_en button:hover:not(:disabled),
        .st-key-language_action_fr button:hover:not(:disabled),
        .st-key-language_action_he button:hover:not(:disabled),
        .st-key-theme_action_toggle_header button:hover:not(:disabled) {{
            border-color: var(--aiwra-primary) !important;
            background: color-mix(in srgb, var(--aiwra-primary-soft) 72%, var(--aiwra-card-bg)) !important;
        }}

        .stAppHeader,
        header[data-testid="stHeader"] {{
            height: 0 !important;
            min-height: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            pointer-events: none !important;
        }}
        .stAppHeader [data-testid="stToolbar"],
        header[data-testid="stHeader"] [data-testid="stToolbar"],
        span#MainMenu,
        .stMainMenu {{
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }}
        .st-key-settings_toolbar_header,
        .aiwra-settings-toolbar {{
            position: sticky;
            top: 0.42rem;
            z-index: 100;
            margin: 0.12rem 0 0.72rem;
            padding: 0.1rem 0;
            border: 0;
            background: transparent;
            direction: ltr !important;
            text-align: left;
        }}
        .st-key-settings_toolbar_header [data-testid="stHorizontalBlock"] {{
            align-items: center;
            gap: 0.46rem;
            direction: ltr !important;
        }}
        .st-key-language_control_cluster,
        .st-key-theme_control_cluster {{
            min-width: 0;
            margin-bottom: 0;
            direction: ltr !important;
        }}
        .st-key-language_control_cluster [data-testid="stHorizontalBlock"] {{
            width: fit-content;
            max-width: 100%;
            gap: 0.18rem;
            padding: 0.18rem;
            border: 1px solid color-mix(in srgb, var(--aiwra-primary) 24%, var(--aiwra-border-soft));
            border-radius: 999px;
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--aiwra-primary) 7%, transparent), transparent 68%),
                color-mix(in srgb, var(--aiwra-elevated-card-bg) 86%, transparent);
            box-shadow: 0 10px 26px color-mix(in srgb, var(--aiwra-shadow) 14%, transparent);
            backdrop-filter: blur(14px);
        }}
        .st-key-theme_control_cluster [data-testid="stButton"] {{
            width: fit-content;
            margin-left: auto;
        }}
        .st-key-language_action_en button,
        .st-key-language_action_fr button,
        .st-key-language_action_he button,
        .st-key-theme_action_toggle_header button {{
            min-height: 2.02rem !important;
            margin: 0;
            padding: 0.16rem 0.7rem !important;
            border-radius: 999px !important;
            border: 1px solid transparent !important;
            color: var(--aiwra-text-primary) !important;
            background: transparent !important;
            box-shadow: none !important;
            font-size: 0.76rem !important;
            font-weight: 850 !important;
            letter-spacing: 0.02em;
            line-height: 1.1 !important;
            white-space: nowrap;
            direction: ltr !important;
            unicode-bidi: isolate;
        }}
        .st-key-language_action_en button[kind="primary"],
        .st-key-language_action_fr button[kind="primary"],
        .st-key-language_action_he button[kind="primary"] {{
            border-color: color-mix(in srgb, var(--aiwra-primary) 36%, var(--aiwra-border)) !important;
            background:
                radial-gradient(circle at 35% 0%, color-mix(in srgb, var(--aiwra-primary) 20%, transparent), transparent 45%),
                color-mix(in srgb, var(--aiwra-primary) 13%, var(--aiwra-elevated-card-bg)) !important;
            color: var(--aiwra-text-primary) !important;
            box-shadow:
                inset 0 0 0 1px color-mix(in srgb, var(--aiwra-primary) 12%, transparent),
                0 8px 18px color-mix(in srgb, var(--aiwra-shadow) 12%, transparent) !important;
        }}
        .st-key-theme_action_toggle_header button {{
            min-width: 6.85rem;
            border-color: color-mix(in srgb, var(--aiwra-primary) 30%, var(--aiwra-border-soft)) !important;
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--aiwra-primary) 10%, transparent), transparent 65%),
                color-mix(in srgb, var(--aiwra-elevated-card-bg) 90%, transparent) !important;
            color: var(--aiwra-text-primary) !important;
            box-shadow: 0 8px 18px color-mix(in srgb, var(--aiwra-shadow) 12%, transparent) !important;
        }}
        .st-key-language_action_en button:hover:not(:disabled),
        .st-key-language_action_fr button:hover:not(:disabled),
        .st-key-language_action_he button:hover:not(:disabled),
        .st-key-theme_action_toggle_header button:hover:not(:disabled) {{
            transform: translateY(-1px);
            border-color: var(--aiwra-primary) !important;
            background:
                radial-gradient(circle at 40% 0%, color-mix(in srgb, var(--aiwra-primary) 24%, transparent), transparent 46%),
                color-mix(in srgb, var(--aiwra-primary-soft) 72%, var(--aiwra-card-bg)) !important;
        }}
        .st-key-main_example_selector_mode [role="radiogroup"],
        .st-key-main_example_selector [role="radiogroup"] {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.42rem;
            padding: 0.34rem;
            border: 1px solid var(--aiwra-border-soft);
            border-radius: var(--aiwra-radius);
            background: var(--aiwra-card-bg);
        }}
        .st-key-main_example_selector_mode [role="radiogroup"] label,
        .st-key-main_example_selector [role="radiogroup"] label {{
            min-height: 2.35rem;
            margin: 0;
            padding: 0.32rem 0.7rem;
            border: 1px solid transparent;
            border-radius: var(--aiwra-radius-sm);
            color: var(--aiwra-text-primary) !important;
            background: transparent;
            font-weight: 760;
            line-height: 1.25;
        }}
        .st-key-main_example_selector_mode [role="radiogroup"] label:has(input:checked),
        .st-key-main_example_selector [role="radiogroup"] label:has(input:checked) {{
            border-color: color-mix(in srgb, var(--aiwra-primary) 54%, var(--aiwra-border));
            background: var(--aiwra-primary-soft);
            box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--aiwra-primary) 24%, transparent);
        }}
        .aiwra-loading-panel {{
            display: grid;
            grid-template-columns: auto minmax(0, 1fr);
            gap: 0.75rem;
            align-items: center;
            padding: 0.9rem 1rem;
            margin: 0.65rem 0 0.85rem;
            border: 1px solid var(--loading-border, var(--aiwra-border));
            border-radius: var(--aiwra-radius);
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--loading-color, var(--aiwra-primary)) 10%, transparent), transparent 60%),
                var(--aiwra-card-bg);
            box-shadow: 0 12px 30px color-mix(in srgb, var(--aiwra-shadow) 48%, transparent);
        }}
        .aiwra-loading-orb {{
            width: 2.25rem;
            height: 2.25rem;
            border-radius: 999px;
            border: 3px solid color-mix(in srgb, var(--loading-color, var(--aiwra-primary)) 24%, var(--aiwra-border));
            border-top-color: var(--loading-color, var(--aiwra-primary));
            animation: aiwra-spin 920ms linear infinite;
        }}
        .aiwra-loading-title {{
            margin: 0 0 0.2rem;
            color: var(--aiwra-text-primary);
            font-size: 1rem;
            line-height: 1.25;
            font-weight: 800;
        }}
        .aiwra-loading-panel p {{
            margin: 0;
            color: var(--aiwra-text-secondary);
            line-height: 1.45;
        }}
        .aiwra-loading-panel small {{
            display: block;
            margin-top: 0.28rem;
            color: var(--aiwra-muted);
            line-height: 1.35;
        }}
        .aiwra-loading-status {{
            display: inline-flex;
            width: fit-content;
            margin-bottom: 0.2rem;
            padding: 0.14rem 0.45rem;
            border: 1px solid var(--loading-border, var(--aiwra-border));
            border-radius: 999px;
            color: var(--loading-color, var(--aiwra-primary));
            background: color-mix(in srgb, var(--loading-color, var(--aiwra-primary)) 10%, transparent);
            font-size: 0.72rem;
            font-weight: 800;
            line-height: 1.25;
        }}
        .aiwra-mission-pulse {{
            position: relative;
            isolation: isolate;
            display: grid;
            grid-template-columns: auto minmax(0, 1fr);
            gap: 0.9rem;
            align-items: center;
            min-height: 5.65rem;
            padding: 0.98rem 1.05rem;
            margin: 0.72rem 0 0.72rem;
            overflow: hidden;
            border: 1px solid color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 44%, var(--mission-border, var(--aiwra-border)));
            border-radius: var(--aiwra-radius);
            background:
                radial-gradient(circle at 12% 24%, color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 24%, transparent), transparent 36%),
                linear-gradient(135deg, color-mix(in srgb, var(--mission-bg, var(--aiwra-primary-soft)) 82%, transparent), transparent 62%),
                color-mix(in srgb, var(--aiwra-card-bg) 92%, var(--aiwra-shell-bg));
            box-shadow:
                0 0 0 1px color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 8%, transparent),
                0 16px 38px color-mix(in srgb, var(--aiwra-shadow) 50%, transparent);
        }}
        .aiwra-mission-pulse::before {{
            content: "";
            position: absolute;
            inset: 0;
            z-index: -1;
            opacity: 0.48;
            background:
                linear-gradient(90deg, transparent 0%, color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 24%, transparent) 50%, transparent 100%);
            transform: translateX(-78%);
            animation: aiwra-mission-scan 4.8s ease-in-out infinite;
        }}
        .aiwra-mission-visual {{
            position: relative;
            width: 3.4rem;
            height: 3.4rem;
            display: grid;
            place-items: center;
            flex: 0 0 auto;
        }}
        .aiwra-mission-orbit {{
            position: absolute;
            inset: 0.25rem;
            border: 1px solid color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 44%, transparent);
            border-block-color: transparent;
            border-radius: 999px;
            animation: aiwra-mission-orbit 7.5s linear infinite;
        }}
        .aiwra-mission-orbit::after {{
            content: "";
            position: absolute;
            top: 0.05rem;
            inset-inline-end: 0.42rem;
            width: 0.42rem;
            height: 0.42rem;
            border-radius: 999px;
            background: var(--mission-color, var(--aiwra-primary));
            box-shadow: 0 0 14px color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 62%, transparent);
        }}
        .aiwra-mission-core {{
            position: relative;
            width: 2.15rem;
            height: 2.15rem;
            display: grid;
            place-items: center;
            border: 1px solid color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 42%, var(--aiwra-border));
            border-radius: 999px;
            background:
                radial-gradient(circle, color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 18%, transparent), transparent 68%),
                var(--aiwra-elevated-card-bg);
            box-shadow:
                0 0 0 4px color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 8%, transparent),
                0 0 24px color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 28%, transparent);
            animation: aiwra-mission-glow 2.8s ease-in-out infinite;
        }}
        .aiwra-mission-rocket {{
            position: relative;
            width: 0.72rem;
            height: 1.42rem;
            border-radius: 999px 999px 0.28rem 0.28rem;
            background: linear-gradient(180deg, var(--aiwra-text-primary), color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 58%, var(--aiwra-text-primary)));
            transform: translateY(-0.08rem);
            box-shadow: inset 0 -0.18rem 0 color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 44%, transparent);
        }}
        .aiwra-mission-rocket::before,
        .aiwra-mission-rocket::after {{
            content: "";
            position: absolute;
            bottom: 0.08rem;
            width: 0.32rem;
            height: 0.48rem;
            background: color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 56%, var(--aiwra-border));
        }}
        .aiwra-mission-rocket::before {{
            inset-inline-start: -0.24rem;
            border-radius: 0.25rem 0 0.2rem 0.25rem;
        }}
        .aiwra-mission-rocket::after {{
            inset-inline-end: -0.24rem;
            border-radius: 0 0.25rem 0.25rem 0.2rem;
        }}
        .aiwra-mission-flame {{
            position: absolute;
            bottom: -0.26rem;
            width: 0.42rem;
            height: 0.7rem;
            border-radius: 999px;
            background: linear-gradient(180deg, color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 72%, #ffffff), transparent);
            filter: drop-shadow(0 0 10px color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 52%, transparent));
            transform-origin: top;
            animation: aiwra-mission-flame 1.25s ease-in-out infinite;
        }}
        .aiwra-mission-copy {{
            min-width: 0;
        }}
        .aiwra-mission-status {{
            display: inline-flex;
            width: fit-content;
            margin-bottom: 0.22rem;
            padding: 0.14rem 0.48rem;
            border: 1px solid var(--mission-border, var(--aiwra-border));
            border-radius: 999px;
            color: var(--mission-color, var(--aiwra-primary));
            background: color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 9%, transparent);
            font-size: 0.72rem;
            font-weight: 820;
            line-height: 1.25;
        }}
        .aiwra-mission-title {{
            margin: 0 0 0.16rem;
            color: var(--aiwra-text-primary);
            font-size: 1.02rem;
            line-height: 1.22;
            font-weight: 840;
        }}
        .aiwra-mission-pulse p {{
            margin: 0;
            color: var(--aiwra-text-secondary);
            font-size: 0.9rem;
            line-height: 1.42;
        }}
        .aiwra-mission-pulse small {{
            display: block;
            margin-top: 0.34rem;
            color: var(--aiwra-muted);
            line-height: 1.35;
        }}
        .aiwra-compact-note {{
            display: inline-flex;
            align-items: center;
            width: fit-content;
            max-width: 100%;
            margin: 0.2rem 0 0.65rem;
            padding: 0.34rem 0.58rem;
            border: 1px solid color-mix(in srgb, var(--aiwra-advisory) 30%, var(--aiwra-border));
            border-radius: var(--aiwra-radius-sm);
            color: var(--aiwra-text-secondary);
            background: color-mix(in srgb, var(--aiwra-advisory) 7%, transparent);
            font-size: 0.82rem;
            line-height: 1.35;
        }}
        .aiwra-compact-note--advisory::before {{
            content: "";
            width: 0.45rem;
            height: 0.45rem;
            margin-inline-end: 0.42rem;
            border-radius: 999px;
            background: var(--aiwra-advisory);
            box-shadow: 0 0 10px color-mix(in srgb, var(--aiwra-advisory) 42%, transparent);
            flex: 0 0 auto;
        }}
        .aiwra-pipeline-strip {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.48rem;
            margin: 0.05rem 0 1rem;
            padding: 0.58rem 0.68rem;
            border: 1px solid color-mix(in srgb, var(--aiwra-local) 38%, var(--aiwra-border));
            border-radius: var(--aiwra-radius);
            background:
                linear-gradient(120deg, color-mix(in srgb, var(--aiwra-local) 12%, transparent), transparent 58%),
                color-mix(in srgb, var(--aiwra-card-bg) 94%, var(--aiwra-shell-bg));
            box-shadow: 0 10px 24px color-mix(in srgb, var(--aiwra-shadow) 34%, transparent);
        }}
        .aiwra-pipeline-step {{
            display: inline-flex;
            align-items: center;
            gap: 0.38rem;
            min-height: 1.72rem;
            min-width: fit-content;
            padding: 0.24rem 0.5rem;
            border: 1px solid color-mix(in srgb, var(--aiwra-border) 76%, transparent);
            border-radius: 999px;
            color: var(--aiwra-muted);
            background: color-mix(in srgb, var(--aiwra-elevated-card-bg) 76%, transparent);
            font-size: 0.78rem;
            font-weight: 780;
            line-height: 1.2;
            white-space: normal;
            word-break: normal;
            overflow-wrap: anywhere;
            transition: border-color 140ms ease, background 140ms ease, color 140ms ease;
        }}
        .aiwra-pipeline-step--done {{
            color: var(--aiwra-low);
            border-color: color-mix(in srgb, var(--aiwra-low) 34%, var(--aiwra-border));
            background: color-mix(in srgb, var(--aiwra-low) 8%, transparent);
        }}
        .aiwra-pipeline-step--active {{
            color: var(--aiwra-text-primary);
            border-color: color-mix(in srgb, var(--aiwra-local) 64%, var(--aiwra-border));
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--aiwra-local) 18%, transparent), transparent 70%),
                var(--aiwra-elevated-card-bg);
            box-shadow:
                0 0 0 3px color-mix(in srgb, var(--aiwra-local) 10%, transparent),
                0 0 18px color-mix(in srgb, var(--aiwra-local) 14%, transparent);
        }}
        .aiwra-pipeline-connector {{
            flex: 1 1 1.15rem;
            min-width: 0.7rem;
            max-width: 2.5rem;
            height: 1px;
            background: linear-gradient(90deg, color-mix(in srgb, var(--aiwra-local) 50%, transparent), color-mix(in srgb, var(--aiwra-border) 72%, transparent));
        }}
        .aiwra-pipeline-orb {{
            width: 0.6rem;
            height: 0.6rem;
            border: 1px solid currentColor;
            border-radius: 999px;
            background: transparent;
            box-shadow: 0 0 0 0 color-mix(in srgb, currentColor 40%, transparent);
            flex: 0 0 auto;
        }}
        .aiwra-pipeline-step--done .aiwra-pipeline-orb {{
            background: currentColor;
        }}
        .aiwra-pipeline-step--active .aiwra-pipeline-orb {{
            background: var(--aiwra-local);
            box-shadow: 0 0 12px color-mix(in srgb, var(--aiwra-local) 44%, transparent);
            animation: aiwra-pipeline-orb 2.6s ease-out infinite;
        }}
        .aiwra-mission-pulse--idle {{
            opacity: 0.82;
        }}
        .aiwra-mission-pulse--idle .aiwra-mission-flame,
        .aiwra-mission-pulse--ready_to_analyze .aiwra-mission-flame {{
            opacity: 0.52;
            animation-duration: 2.4s;
        }}
        .aiwra-mission-pulse--deterministic_ready .aiwra-mission-orbit {{
            animation-duration: 10s;
        }}
        .aiwra-mission-pulse--advisory_unavailable {{
            box-shadow: 0 10px 24px color-mix(in srgb, var(--aiwra-shadow) 34%, transparent);
        }}
        .aiwra-mission-pulse--advisory_unavailable::before,
        .aiwra-mission-pulse--error::before {{
            animation: none;
            opacity: 0.2;
        }}
        .aiwra-mission-pulse--advisory_unavailable .aiwra-mission-flame {{
            display: none;
        }}
        @keyframes aiwra-mission-scan {{
            0%, 52% {{ transform: translateX(-78%); }}
            78%, 100% {{ transform: translateX(78%); }}
        }}
        @keyframes aiwra-mission-orbit {{
            to {{ transform: rotate(360deg); }}
        }}
        @keyframes aiwra-mission-glow {{
            0%, 100% {{ box-shadow: 0 0 0 4px color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 8%, transparent), 0 0 20px color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 22%, transparent); }}
            50% {{ box-shadow: 0 0 0 6px color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 11%, transparent), 0 0 28px color-mix(in srgb, var(--mission-color, var(--aiwra-primary)) 34%, transparent); }}
        }}
        @keyframes aiwra-mission-flame {{
            0%, 100% {{ transform: scaleY(0.72); opacity: 0.58; }}
            50% {{ transform: scaleY(1); opacity: 0.92; }}
        }}
        @keyframes aiwra-pipeline-orb {{
            0% {{ box-shadow: 0 0 0 0 color-mix(in srgb, var(--aiwra-local) 34%, transparent); }}
            65%, 100% {{ box-shadow: 0 0 0 7px transparent; }}
        }}
        @keyframes aiwra-spin {{
            to {{ transform: rotate(360deg); }}
        }}
        h1, h2, h3, h4, h5, h6, p, label, span {{
            text-rendering: optimizeLegibility;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: var(--aiwra-text-primary);
            letter-spacing: 0;
        }}
        h1 {{
            font-size: clamp(1.75rem, 2.2vw, 2.125rem);
            line-height: 1.1;
        }}
        h2 {{
            font-size: clamp(1.25rem, 1.65vw, 1.5rem);
            line-height: 1.18;
        }}
        h3 {{
            font-size: clamp(1rem, 1.3vw, 1.125rem);
            line-height: 1.25;
        }}
        p, li, label, .stCaptionContainer, [data-testid="stCaptionContainer"] {{
            color: var(--aiwra-text-secondary);
        }}
        a {{
            color: var(--aiwra-primary) !important;
            text-underline-offset: 0.18em;
        }}
        a:hover {{
            color: var(--aiwra-accent) !important;
        }}
        .aiwra-hero {{
            position: relative;
            overflow: hidden;
            isolation: isolate;
            border: 1px solid color-mix(in srgb, var(--aiwra-primary) 34%, var(--aiwra-border));
            background:
                linear-gradient(90deg, color-mix(in srgb, var(--aiwra-primary-soft) 80%, transparent), transparent 70%),
                linear-gradient(160deg, var(--aiwra-elevated-card-bg), var(--aiwra-card-bg));
            border-radius: var(--aiwra-radius-lg);
            padding: clamp(0.8rem, 1.5vw, 1.05rem);
            margin: 0.15rem 0 0.7rem 0;
            box-shadow: 0 12px 34px color-mix(in srgb, var(--aiwra-shadow) 66%, transparent);
        }}
        .aiwra-hero::after {{
            content: "";
            position: absolute;
            inset: 0;
            z-index: -1;
            background-image: linear-gradient(color-mix(in srgb, var(--aiwra-border) 28%, transparent) 1px, transparent 1px),
                              linear-gradient(90deg, color-mix(in srgb, var(--aiwra-border) 28%, transparent) 1px, transparent 1px);
            background-size: 32px 32px;
            mask-image: linear-gradient(90deg, transparent, black);
            opacity: 0.18;
        }}
        .aiwra-hero-title {{
            margin: 0 0 0.45rem 0;
            max-width: 880px;
            font-size: clamp(1.18rem, 2vw, 1.65rem);
            line-height: 1.18;
            letter-spacing: 0;
            color: var(--aiwra-text-primary);
            font-weight: 850;
        }}
        .aiwra-hero p {{
            max-width: 980px;
            margin: 0 0 0.65rem 0;
            color: var(--aiwra-text-secondary);
            line-height: 1.62;
            font-size: 1.02rem;
        }}
        .aiwra-hero-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: center;
        }}
        .aiwra-card {{
            border: 1px solid var(--aiwra-border);
            background: var(--aiwra-card-bg);
            border-radius: var(--aiwra-radius);
            padding: 1rem;
            margin: 0.3rem 0 0.75rem 0;
            box-shadow: 0 8px 20px color-mix(in srgb, var(--aiwra-shadow) 56%, transparent);
            transition: border-color 180ms ease, box-shadow 180ms ease;
        }}
        .aiwra-card-title {{
            margin: 0 0 0.4rem 0;
            color: var(--aiwra-text-primary);
            font-size: 1rem;
            line-height: 1.28;
            font-weight: 820;
        }}
        .aiwra-card p {{
            margin: 0.35rem 0;
            color: var(--aiwra-text-secondary);
            line-height: 1.55;
            font-size: 0.92rem;
        }}
        .aiwra-kpi-value {{
            display: block;
            color: var(--aiwra-text-primary);
            font-size: clamp(1.45rem, 2.2vw, 2rem);
            font-weight: 780;
            line-height: 1.2;
            margin: 0.35rem 0;
        }}
        .aiwra-label {{
            font-size: 0.88rem;
            font-weight: 700;
            color: var(--aiwra-text-primary);
        }}
        .aiwra-muted {{
            color: var(--aiwra-muted);
        }}
        .aiwra-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            max-width: 100%;
            white-space: normal;
            border-radius: 999px;
            border: 1px solid var(--aiwra-border);
            padding: 0.25rem 0.65rem;
            margin: 0.1rem 0.2rem 0.1rem 0;
            font-size: 0.78rem;
            font-weight: 760;
            line-height: 1.35;
            letter-spacing: 0;
        }}
        .aiwra-section {{
            border-bottom: 1px solid color-mix(in srgb, var(--aiwra-border) 78%, transparent);
            padding-bottom: 0.62rem;
            margin: 1.35rem 0 0.8rem 0;
        }}
        .aiwra-section-title {{
            margin: 0;
            font-size: 1.28rem;
            color: var(--aiwra-text-primary);
            line-height: 1.22;
            font-weight: 830;
        }}
        .aiwra-section p {{
            margin: 0.3rem 0 0;
        }}
        .aiwra-grid {{
            display: grid;
            gap: 0.75rem;
        }}
        .aiwra-grid-3 {{
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        }}
        .aiwra-bento {{
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.55rem 0 1rem 0;
        }}
        .aiwra-bento-card {{
            grid-column: span 2;
            min-height: 180px;
            border: 1px solid var(--aiwra-border);
            background: var(--aiwra-card-bg);
            border-radius: var(--aiwra-radius);
            padding: 1rem;
            box-shadow: 0 8px 20px color-mix(in srgb, var(--aiwra-shadow) 56%, transparent);
            display: flex;
            flex-direction: column;
            gap: 0.42rem;
            transition: border-color 180ms ease;
        }}
        .aiwra-bento-wide {{
            grid-column: span 3;
        }}
        .aiwra-bento-title {{
            color: var(--aiwra-muted);
            font-size: 0.84rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0;
        }}
        .aiwra-bento-value {{
            color: var(--aiwra-text-primary);
            font-size: 1.45rem;
            line-height: 1.2;
            font-weight: 800;
        }}
        .aiwra-severity-strip {{
            width: 100%;
            height: 0.28rem;
            border-radius: 999px;
            background: var(--aiwra-primary);
            margin-bottom: 0.15rem;
        }}
        .aiwra-card-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.65rem;
            margin: 0.4rem 0 0.85rem 0;
        }}
        .aiwra-heatmap {{
            display: grid;
            gap: 0.45rem;
            margin: 0.5rem 0 1rem 0;
            overflow-x: auto;
        }}
        .aiwra-heatmap-row {{
            display: grid;
            grid-template-columns: minmax(150px, 1.15fr) repeat(5, minmax(118px, 1fr));
            gap: 0.45rem;
            min-width: 760px;
        }}
        .aiwra-heatmap-head,
        .aiwra-heatmap-label,
        .aiwra-heatmap-cell {{
            border: 1px solid var(--aiwra-border-soft);
            border-radius: var(--aiwra-radius-sm);
            padding: 0.62rem;
            background: var(--aiwra-card-bg);
            line-height: 1.32;
        }}
        .aiwra-heatmap-head {{
            font-weight: 700;
            color: var(--aiwra-text-primary);
            background: var(--aiwra-surface-muted);
        }}
        .aiwra-heatmap-label {{
            font-weight: 700;
            color: var(--aiwra-text-primary);
            background: var(--aiwra-surface-soft);
        }}
        .aiwra-heatmap-cell strong {{
            display: block;
            color: var(--aiwra-text-primary);
        }}
        .aiwra-flow {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: stretch;
            margin: 0.65rem 0;
        }}
        .aiwra-flow-step {{
            border: 1px solid var(--aiwra-border);
            border-radius: var(--aiwra-radius-sm);
            background: var(--aiwra-card-bg);
            padding: 0.7rem 0.85rem;
            min-width: 150px;
            flex: 1 1 150px;
            transition: border-color 180ms ease;
        }}
        .aiwra-flow-step small {{
            display: block;
            color: var(--aiwra-muted);
            margin-top: 0.25rem;
        }}
        .aiwra-timeline-item {{
            border-inline-start: 3px solid var(--aiwra-primary);
            padding: 0.35rem 0.75rem;
            margin: 0.45rem 0;
            background: var(--aiwra-card-bg);
            border-radius: var(--aiwra-radius-sm);
        }}
        .aiwra-cockpit {{
            position: relative;
            overflow: hidden;
            display: grid;
            grid-template-columns: minmax(250px, 1.35fr) repeat(5, minmax(120px, 0.72fr));
            gap: 0.7rem;
            padding: 0.75rem;
            margin: 0.7rem 0 1rem;
            border: 1px solid color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 58%, var(--aiwra-border));
            border-radius: var(--aiwra-radius-lg);
            background:
                radial-gradient(circle at 8% 14%, color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 16%, transparent), transparent 34%),
                linear-gradient(120deg, color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 14%, transparent), transparent 42%),
                linear-gradient(155deg, var(--aiwra-elevated-card-bg), var(--aiwra-card-bg));
            box-shadow:
                0 0 0 1px color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 10%, transparent),
                0 24px 64px var(--aiwra-shadow);
        }}
        .aiwra-cockpit--live {{
            border-color: color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 68%, var(--aiwra-border));
            box-shadow:
                0 0 0 1px color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 18%, transparent),
                0 0 28px color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 14%, transparent),
                0 24px 64px var(--aiwra-shadow);
        }}
        .aiwra-cockpit::before {{
            content: "";
            position: absolute;
            top: 0;
            inset-inline-start: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--cockpit-color, var(--aiwra-primary)), var(--aiwra-accent));
        }}
        .aiwra-cockpit-scan {{
            position: absolute;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            opacity: 0.23;
            background: repeating-linear-gradient(
                180deg,
                transparent 0,
                transparent 9px,
                color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 28%, transparent) 10px
            );
            animation: aiwra-cockpit-scan 8.5s linear infinite;
        }}
        .aiwra-cockpit-cell {{
            position: relative;
            z-index: 1;
            min-height: 116px;
            padding: 0.9rem;
            border: 1px solid color-mix(in srgb, var(--aiwra-border) 82%, transparent);
            border-radius: var(--aiwra-radius);
            background: color-mix(in srgb, var(--aiwra-elevated-card-bg) 92%, transparent);
        }}
        .aiwra-cockpit-main {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background:
                linear-gradient(145deg, color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 18%, transparent), transparent),
                var(--aiwra-elevated-card-bg);
        }}
        .aiwra-cockpit-label {{
            color: var(--aiwra-muted);
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0;
            text-transform: uppercase;
        }}
        .aiwra-cockpit-score {{
            color: var(--cockpit-color, var(--aiwra-primary));
            font-size: clamp(2.2rem, 5vw, 4.2rem);
            line-height: 0.95;
            font-weight: 850;
            letter-spacing: 0;
        }}
        .aiwra-cockpit-score-glow {{
            display: inline-flex;
            width: fit-content;
            margin-top: 0.3rem;
            border-radius: var(--aiwra-radius);
            text-shadow:
                0 0 12px color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 48%, transparent),
                0 0 26px color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 28%, transparent);
            filter: drop-shadow(0 0 22px color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 34%, transparent));
            animation: aiwra-score-glow 3.4s ease-in-out infinite;
        }}
        .aiwra-cockpit-value {{
            display: block;
            margin-top: 0.55rem;
            color: var(--aiwra-text-primary);
            font-size: 1.05rem;
            font-weight: 780;
            line-height: 1.25;
        }}
        .aiwra-cockpit-note {{
            display: block;
            margin-top: 0.42rem;
            color: var(--aiwra-muted);
            font-size: 0.78rem;
            line-height: 1.35;
        }}
        .aiwra-status-dot {{
            display: inline-block;
            width: 0.62rem;
            height: 0.62rem;
            margin-inline-end: 0.35rem;
            border-radius: 999px;
            background: currentColor;
            box-shadow:
                0 0 0 0 color-mix(in srgb, currentColor 50%, transparent),
                0 0 12px color-mix(in srgb, currentColor 34%, transparent);
            animation: aiwra-pulse 2.8s ease-out infinite;
        }}
        @keyframes aiwra-pulse {{
            0% {{ box-shadow: 0 0 0 0 color-mix(in srgb, currentColor 42%, transparent); }}
            60%, 100% {{ box-shadow: 0 0 0 8px transparent; }}
        }}
        @keyframes aiwra-local-heartbeat {{
            0%, 100% {{ transform: scale(1); box-shadow: 0 0 0 0 color-mix(in srgb, currentColor 34%, transparent); }}
            45% {{ transform: scale(1.18); box-shadow: 0 0 0 6px transparent; }}
        }}
        @keyframes aiwra-cockpit-scan {{
            to {{ transform: translateY(18px); }}
        }}
        @keyframes aiwra-score-glow {{
            0%, 100% {{ filter: drop-shadow(0 0 18px color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 28%, transparent)); }}
            50% {{ filter: drop-shadow(0 0 28px color-mix(in srgb, var(--cockpit-color, var(--aiwra-primary)) 42%, transparent)); }}
        }}
        .aiwra-finding-card {{
            border-inline-start: 5px solid var(--finding-color, var(--aiwra-primary));
            background:
                linear-gradient(110deg, color-mix(in srgb, var(--finding-color, var(--aiwra-primary)) 9%, transparent), transparent 38%),
                var(--aiwra-card-bg);
        }}
        .aiwra-control-card {{
            border-inline-start: 5px solid var(--aiwra-recommended);
            background:
                linear-gradient(110deg, color-mix(in srgb, var(--aiwra-recommended) 8%, transparent), transparent 42%),
                var(--aiwra-card-bg);
        }}
        .aiwra-control-meta {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.55rem;
            margin-top: 0.65rem;
        }}
        .aiwra-finding-head {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.65rem;
            margin-bottom: 0.75rem;
        }}
        .aiwra-finding-title {{
            margin: 0;
            font-size: 1.08rem;
        }}
        .aiwra-evidence-quote {{
            padding: 0.75rem 0.85rem;
            border: 1px solid color-mix(in srgb, var(--finding-color, var(--aiwra-primary)) 34%, var(--aiwra-border));
            border-radius: var(--aiwra-radius-sm);
            background: color-mix(in srgb, var(--finding-color, var(--aiwra-primary)) 7%, var(--aiwra-surface-alt));
            color: var(--aiwra-text-primary);
            font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
            font-size: 0.84rem;
            line-height: 1.55;
            overflow-wrap: anywhere;
        }}
        .aiwra-detail-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.55rem;
            margin-top: 0.65rem;
        }}
        .aiwra-detail {{
            padding: 0.65rem;
            border-radius: var(--aiwra-radius-sm);
            background: var(--aiwra-surface-alt);
        }}
        .aiwra-detail strong {{
            display: block;
            color: var(--aiwra-text-primary);
            font-size: 0.78rem;
            margin-bottom: 0.2rem;
        }}
        .aiwra-detail span {{
            color: var(--aiwra-text-secondary);
            font-size: 0.85rem;
            line-height: 1.45;
        }}
        .aiwra-simulation-shell,
        .aiwra-ai-brain {{
            position: relative;
            overflow: hidden;
            border: 1px solid color-mix(in srgb, var(--aiwra-accent) 40%, var(--aiwra-border));
            border-radius: var(--aiwra-radius-lg);
            background:
                linear-gradient(155deg, var(--aiwra-elevated-card-bg), var(--aiwra-card-bg));
            padding: 1.1rem;
            margin: 0.7rem 0 1rem;
            box-shadow: 0 20px 52px var(--aiwra-shadow);
        }}
        .aiwra-simulation-grid {{
            display: grid;
            grid-template-columns: 1fr auto 1fr 1fr;
            gap: 0.75rem;
            align-items: stretch;
        }}
        .aiwra-score-panel {{
            padding: 0.9rem;
            border-radius: var(--aiwra-radius);
            border: 1px solid var(--aiwra-border);
            background: var(--aiwra-surface-alt);
        }}
        .aiwra-score-panel strong {{
            display: block;
            margin: 0.2rem 0;
            font-size: 1.65rem;
            color: var(--score-color, var(--aiwra-primary));
        }}
        .aiwra-simulation-arrow {{
            align-self: center;
            color: var(--aiwra-accent);
            font-size: 1.6rem;
            font-weight: 800;
        }}
        .aiwra-assumption-banner {{
            margin-top: 0.8rem;
            padding: 0.75rem 0.85rem;
            border: 1px solid var(--aiwra-medium-border);
            border-radius: var(--aiwra-radius-sm);
            color: var(--aiwra-medium);
            background: var(--aiwra-medium-soft);
            font-weight: 760;
        }}
        .aiwra-ai-brain {{
            border-color: color-mix(in srgb, var(--aiwra-primary) 46%, var(--aiwra-border));
        }}
        .aiwra-ai-brain-head {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 0.75rem;
            align-items: center;
        }}
        .aiwra-ai-brain-title {{
            margin: 0;
            color: var(--aiwra-text-primary);
            font-size: 1.1rem;
            line-height: 1.25;
            font-weight: 830;
        }}
        .aiwra-ai-boundaries {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.65rem;
            margin-top: 0.9rem;
        }}
        .aiwra-ai-boundary {{
            min-height: 92px;
            padding: 0.75rem;
            border: 1px solid var(--aiwra-border);
            border-radius: var(--aiwra-radius-sm);
            background: var(--aiwra-surface-alt);
        }}
        .aiwra-ai-boundary strong {{
            display: block;
            color: var(--aiwra-text-primary);
            margin-bottom: 0.3rem;
        }}
        .aiwra-ai-boundary span {{
            color: var(--aiwra-muted);
            font-size: 0.82rem;
            line-height: 1.4;
        }}
        .aiwra-code,
        .aiwra-technical,
        bdi {{
            direction: ltr;
            text-align: left;
            unicode-bidi: isolate;
            white-space: normal;
        }}
        .aiwra-technical {{
            display: inline-block;
            max-width: 100%;
            font-family: var(--aiwra-font-mono, ui-monospace, SFMono-Regular, Consolas, monospace);
        }}
        [data-testid="stDataFrame"],
        [data-testid="stTable"] {{
            border: 1px solid var(--aiwra-border);
            border-radius: var(--aiwra-radius);
            overflow: hidden;
            background: var(--aiwra-card-bg);
        }}
        [data-testid="stCodeBlock"],
        pre,
        code {{
            background: var(--aiwra-surface-alt) !important;
            color: var(--aiwra-text-primary) !important;
            border-color: var(--aiwra-border) !important;
        }}
        [data-testid="stAlert"] {{
            border: 1px solid var(--aiwra-border);
            border-radius: var(--aiwra-radius) !important;
            background: color-mix(in srgb, var(--aiwra-elevated-card-bg) 92%, transparent);
            color: var(--aiwra-text-primary);
        }}
        [data-testid="stExpander"] {{
            border: 1px solid var(--aiwra-border) !important;
            border-radius: var(--aiwra-radius) !important;
            background: var(--aiwra-card-bg) !important;
            box-shadow: 0 9px 24px color-mix(in srgb, var(--aiwra-shadow) 55%, transparent);
            overflow: hidden;
        }}
        [data-testid="stExpander"] details,
        [data-testid="stExpander"] summary {{
            background: var(--aiwra-card-bg) !important;
            color: var(--aiwra-text-primary) !important;
        }}
        [data-testid="stExpander"] summary:hover {{
            background: var(--aiwra-surface-alt) !important;
        }}
        [data-testid="stFileUploader"] section {{
            border: 1px dashed color-mix(in srgb, var(--aiwra-primary) 44%, var(--aiwra-border)) !important;
            border-radius: var(--aiwra-radius) !important;
            background: color-mix(in srgb, var(--aiwra-primary-soft) 45%, var(--aiwra-input-bg)) !important;
        }}
        [data-testid="stFileUploader"] section div,
        [data-testid="stFileUploader"] section span,
        [data-testid="stFileUploader"] section small {{
            color: var(--aiwra-text-secondary) !important;
        }}
        [data-testid="stTabs"] [data-baseweb="tab-list"] {{
            gap: 0.35rem;
            padding: 0.3rem;
            border: 1px solid var(--aiwra-border);
            border-radius: var(--aiwra-radius);
            background: var(--aiwra-card-bg);
        }}
        [data-testid="stTabs"] [data-baseweb="tab"] {{
            min-height: 2.65rem;
            padding-inline: 0.9rem;
            border-radius: var(--aiwra-radius-sm);
            color: var(--aiwra-muted);
            background: transparent;
        }}
        [data-testid="stTabs"] [aria-selected="true"] {{
            color: var(--aiwra-text-primary) !important;
            background: var(--aiwra-primary-soft) !important;
        }}
        [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
            background: var(--aiwra-primary);
        }}
        [data-baseweb="select"] > div,
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stTextAreaRootElement"] textarea,
        [data-testid="stNumberInput"] input {{
            color: var(--aiwra-text-primary) !important;
            background: var(--aiwra-input-bg) !important;
            border-color: var(--aiwra-input-border) !important;
            border-radius: var(--aiwra-radius-sm) !important;
        }}
        [data-baseweb="select"] > div:hover,
        [data-testid="stTextInput"] input:hover,
        [data-testid="stTextArea"] textarea:hover,
        [data-testid="stTextAreaRootElement"] textarea:hover {{
            border-color: color-mix(in srgb, var(--aiwra-primary) 58%, var(--aiwra-border)) !important;
        }}
        [data-testid="stTextArea"] textarea,
        [data-testid="stTextAreaRootElement"] textarea {{
            color: var(--aiwra-text-primary) !important;
            -webkit-text-fill-color: var(--aiwra-text-primary) !important;
            caret-color: var(--aiwra-primary) !important;
            background: var(--aiwra-input-bg) !important;
        }}
        [data-testid="stTextArea"] textarea::placeholder,
        [data-testid="stTextAreaRootElement"] textarea::placeholder {{
            color: var(--aiwra-muted) !important;
            -webkit-text-fill-color: var(--aiwra-muted) !important;
            opacity: 0.76 !important;
        }}
        [data-testid="stTextArea"] textarea::selection,
        [data-testid="stTextAreaRootElement"] textarea::selection {{
            color: var(--aiwra-text-primary) !important;
            -webkit-text-fill-color: var(--aiwra-text-primary) !important;
            background: color-mix(in srgb, var(--aiwra-primary) 34%, transparent) !important;
        }}
        [data-baseweb="popover"],
        ul[data-testid="stSelectboxVirtualDropdown"],
        [role="listbox"] {{
            color: var(--aiwra-text-primary) !important;
            background: var(--aiwra-elevated-card-bg) !important;
            border-color: var(--aiwra-border) !important;
            max-height: min(420px, 58vh) !important;
            overflow-y: auto !important;
            border-radius: var(--aiwra-radius) !important;
            box-shadow: 0 18px 46px color-mix(in srgb, var(--aiwra-shadow) 78%, transparent) !important;
        }}
        [role="listbox"] * {{
            color: var(--aiwra-text-primary) !important;
        }}
        [role="option"]:hover,
        [role="option"][aria-selected="true"] {{
            background: var(--aiwra-primary-soft) !important;
        }}
        button[kind],
        [data-testid="stButton"] button,
        [data-testid="stDownloadButton"] button,
        [data-testid="stFormSubmitButton"] button {{
            min-height: 2.72rem;
            border: 1px solid var(--aiwra-button-secondary-border) !important;
            border-radius: var(--aiwra-radius-sm) !important;
            color: var(--aiwra-button-secondary-text) !important;
            background: var(--aiwra-button-secondary-bg) !important;
            box-shadow: 0 8px 18px color-mix(in srgb, var(--aiwra-shadow) 50%, transparent);
            font-weight: 780;
            line-height: 1.2;
            justify-content: center;
            transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease, background 140ms ease;
        }}
        button[kind="primary"],
        [data-testid="stButton"] button[kind="primary"],
        [data-testid="stFormSubmitButton"] button[kind="primary"],
        .st-key-analyze_workflow_primary button {{
            min-height: 3rem;
            color: var(--aiwra-button-primary-text) !important;
            background: var(--aiwra-button-primary-bg) !important;
            border-color: transparent !important;
            box-shadow: 0 14px 32px color-mix(in srgb, var(--aiwra-primary) 30%, transparent);
        }}
        .st-key-clear_input_secondary button,
        .st-key-clear_session_secondary button,
        .st-key-save_report_secondary button,
        .st-key-save_simulation_secondary button,
        .st-key-save_simulation_secondary_simulation_page button,
        .st-key-load_example_secondary button,
        .st-key-create_project_secondary button {{
            color: var(--aiwra-button-secondary-text) !important;
            background: var(--aiwra-button-secondary-bg) !important;
            border-color: var(--aiwra-button-secondary-border) !important;
        }}
        .st-key-post_analysis_shortcut_evidence button,
        .st-key-post_analysis_shortcut_simulation button,
        .st-key-post_analysis_shortcut_reports button,
        .st-key-post_analysis_shortcut_local_ai button {{
            color: var(--aiwra-button-ghost-text) !important;
            background: var(--aiwra-button-ghost-bg) !important;
            border-color: var(--aiwra-button-ghost-border) !important;
            box-shadow: none;
        }}
        .st-key-post_analysis_shortcut_evidence button::before {{
            content: "▣";
            margin-inline-end: 0.38rem;
        }}
        .st-key-post_analysis_shortcut_simulation button::before {{
            content: "◎";
            margin-inline-end: 0.38rem;
        }}
        .st-key-post_analysis_shortcut_reports button::before {{
            content: "↗";
            margin-inline-end: 0.38rem;
        }}
        .st-key-post_analysis_shortcut_local_ai button::before {{
            content: "✦";
            margin-inline-end: 0.38rem;
        }}
        .st-key-simulate_residual_risk_action button,
        .st-key-simulate_residual_risk_action_simulation_page button,
        .st-key-local_ai_generate_action button,
        .st-key-local_ai_synthetic_test_action button {{
            color: var(--aiwra-button-secondary-text) !important;
            background: linear-gradient(145deg, var(--aiwra-accent-soft), var(--aiwra-button-secondary-bg)) !important;
            border-color: color-mix(in srgb, var(--aiwra-accent) 54%, var(--aiwra-border)) !important;
        }}
        .st-key-delete_project_danger button,
        .st-key-reset_demo_database_danger button {{
            color: var(--aiwra-button-danger-text) !important;
            background: var(--aiwra-button-danger-bg) !important;
            border-color: var(--aiwra-button-danger-border) !important;
            box-shadow: 0 10px 24px color-mix(in srgb, var(--aiwra-critical) 18%, transparent);
        }}
        [data-testid="stDownloadButton"] button {{
            color: var(--aiwra-button-download-text) !important;
            background: var(--aiwra-button-download-bg) !important;
            border-color: var(--aiwra-button-download-border) !important;
        }}
        .st-key-download_markdown_action button,
        .st-key-download_json_action button {{
            color: var(--aiwra-button-download-text) !important;
            background: var(--aiwra-button-download-bg) !important;
            border-color: var(--aiwra-button-download-border) !important;
        }}
        button[kind]:hover:not(:disabled),
        [data-testid="stButton"] button:hover:not(:disabled),
        [data-testid="stDownloadButton"] button:hover:not(:disabled) {{
            transform: translateY(-1px);
            border-color: var(--aiwra-primary) !important;
            box-shadow: 0 13px 28px var(--aiwra-shadow);
        }}
        button[kind]:active:not(:disabled),
        [data-testid="stButton"] button:active:not(:disabled),
        [data-testid="stDownloadButton"] button:active:not(:disabled) {{
            transform: translateY(0);
            box-shadow: 0 7px 16px color-mix(in srgb, var(--aiwra-shadow) 70%, transparent);
        }}
        button:disabled,
        [data-testid="stButton"] button:disabled,
        [data-testid="stDownloadButton"] button:disabled {{
            opacity: 1 !important;
            color: var(--aiwra-button-disabled-text) !important;
            background: var(--aiwra-button-disabled-bg) !important;
            border-color: var(--aiwra-button-disabled-border) !important;
            box-shadow: none !important;
            cursor: not-allowed;
        }}
        button:focus-visible,
        input:focus-visible,
        textarea:focus-visible,
        [role="combobox"]:focus-visible,
        [role="tab"]:focus-visible {{
            outline: 2px solid var(--aiwra-primary) !important;
            outline-offset: 2px;
            box-shadow: var(--aiwra-focus) !important;
        }}
        [data-testid="stMetric"] {{
            padding: 0.85rem;
            border: 1px solid var(--aiwra-border);
            border-radius: var(--aiwra-radius);
            background: var(--aiwra-card-bg);
        }}
        [data-testid="stMetric"] label,
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {{
            color: var(--aiwra-text-primary) !important;
        }}
        [data-testid="stToggle"] label,
        [data-testid="stCheckbox"] label,
        [data-testid="stRadio"] label {{
            color: var(--aiwra-text-secondary) !important;
        }}
        @media (max-width: 1180px) {{
            .aiwra-shell-header {{
                grid-template-columns: 1fr;
            }}
            .aiwra-command-cockpit {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
            .aiwra-cockpit {{
                grid-template-columns: repeat(3, minmax(0, 1fr));
            }}
            .aiwra-cockpit-main {{
                grid-column: span 3;
            }}
            .aiwra-ai-boundaries {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}
        @media (max-width: 900px) {{
            .aiwra-bento {{
                grid-template-columns: 1fr;
            }}
            .aiwra-bento-card,
            .aiwra-bento-wide {{
                grid-column: span 1;
            }}
            .aiwra-cockpit {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
            .aiwra-cockpit-main {{
                grid-column: span 2;
            }}
            .aiwra-simulation-grid {{
                grid-template-columns: 1fr;
            }}
            .aiwra-simulation-arrow {{
                transform: rotate(90deg);
                justify-self: center;
            }}
            .aiwra-detail-grid {{
                grid-template-columns: 1fr;
            }}
            .aiwra-control-meta {{
                grid-template-columns: 1fr;
            }}
        }}
        @media (max-width: 600px) {{
            .block-container {{
                padding-inline: 0.75rem;
            }}
            .st-key-settings_toolbar_header {{
                margin-top: 0;
            }}
            .st-key-settings_toolbar_header [data-testid="stHorizontalBlock"] {{
                gap: 0.35rem;
            }}
            .st-key-language_control_cluster [data-testid="stHorizontalBlock"] {{
                width: 100%;
            }}
            .st-key-theme_control_cluster [data-testid="stButton"] {{
                margin-left: 0;
            }}
            .aiwra-status-strip {{
                grid-template-columns: 1fr;
            }}
            .aiwra-command-cockpit {{
                grid-template-columns: 1fr;
            }}
            .aiwra-cockpit,
            .aiwra-mission-pulse,
            .aiwra-pipeline-strip,
            .aiwra-ai-boundaries {{
                grid-template-columns: 1fr;
            }}
            .aiwra-mission-visual {{
                width: 3rem;
                height: 3rem;
            }}
            .aiwra-cockpit-main {{
                grid-column: span 1;
            }}
            .aiwra-hero {{
                border-radius: var(--aiwra-radius);
            }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{
                scroll-behavior: auto !important;
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
            .aiwra-loading-orb {{
                animation: none;
                border-top-color: color-mix(in srgb, var(--loading-color, var(--aiwra-primary)) 60%, var(--aiwra-border));
            }}
            .aiwra-mission-pulse::before,
            .aiwra-mission-orbit,
            .aiwra-mission-core,
            .aiwra-mission-flame,
            .aiwra-pipeline-strip,
            .aiwra-pipeline-step,
            .aiwra-pipeline-orb,
            .aiwra-shell-heartbeat,
            .aiwra-status-dot,
            .aiwra-loading-orb,
            .aiwra-cockpit-scan,
            .aiwra-cockpit-score-glow {{
                animation: none !important;
                transition-duration: 0.01ms !important;
            }}
        }}
        {rtl_css}
        /* AIWRA_P14_HUMAN_HEADER_DOCK_BEGIN */
        [data-testid="stHeader"] {{
            height: 0 !important;
            min-height: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            pointer-events: none !important;
            visibility: hidden !important;
        }}
        [data-testid="stToolbar"],
        [data-testid="stToolbarActions"],
        #MainMenu,
        .stMainMenu {{
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            min-width: 0 !important;
            min-height: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
            visibility: hidden !important;
        }}
        .main .block-container,
        [data-testid="stAppViewContainer"] .main .block-container {{
            padding-top: clamp(0.7rem, 0.9vw, 1.05rem) !important;
        }}
        .st-key-settings_toolbar_header {{
            position: sticky;
            top: 0.42rem;
            z-index: 997;
            margin: 0 0 0.82rem !important;
            padding: 0.24rem 0 !important;
            border: 0 !important;
            background: transparent !important;
            direction: ltr !important;
            text-align: left !important;
            pointer-events: auto !important;
        }}
        .st-key-settings_toolbar_header,
        .st-key-settings_toolbar_header * {{
            direction: ltr !important;
            unicode-bidi: isolate;
        }}
        .st-key-settings_toolbar_header [data-testid="stHorizontalBlock"]:has(.st-key-language_control_cluster):has(.st-key-theme_control_cluster) {{
            width: fit-content !important;
            max-width: min(100%, 31rem) !important;
            margin-inline-start: auto !important;
            margin-inline-end: 0 !important;
            padding: 0.24rem !important;
            gap: 0.26rem !important;
            align-items: center !important;
            justify-content: end !important;
            border: 1px solid color-mix(in srgb, var(--aiwra-border-soft) 68%, transparent) !important;
            border-radius: 999px !important;
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--aiwra-primary) 6%, transparent), transparent 62%),
                color-mix(in srgb, var(--aiwra-elevated-card-bg) 88%, transparent) !important;
            backdrop-filter: blur(18px) saturate(145%);
            -webkit-backdrop-filter: blur(18px) saturate(145%);
            box-shadow:
                0 14px 34px color-mix(in srgb, var(--aiwra-shadow) 18%, transparent),
                inset 0 1px 0 color-mix(in srgb, var(--aiwra-text-inverse) 6%, transparent) !important;
        }}
        .st-key-settings_toolbar_header [data-testid="stHorizontalBlock"]:has(.st-key-language_control_cluster):has(.st-key-theme_control_cluster) > [data-testid="column"] {{
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: 0 !important;
            padding: 0 !important;
        }}
        .st-key-language_control_cluster,
        .st-key-theme_control_cluster {{
            min-width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .st-key-language_control_cluster [data-testid="stHorizontalBlock"] {{
            width: fit-content !important;
            max-width: 100% !important;
            gap: 0.14rem !important;
            padding: 0 !important;
            border: 0 !important;
            border-radius: 999px !important;
            background: transparent !important;
            box-shadow: none !important;
        }}
        .st-key-language_control_cluster [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: 0 !important;
            padding: 0 !important;
        }}
        .st-key-language_action_en button,
        .st-key-language_action_fr button,
        .st-key-language_action_he button,
        .st-key-theme_action_toggle_header button {{
            min-height: 1.82rem !important;
            height: 1.82rem !important;
            margin: 0 !important;
            padding: 0.12rem 0.54rem !important;
            border-radius: 999px !important;
            border: 1px solid transparent !important;
            color: var(--aiwra-text-primary) !important;
            background: transparent !important;
            box-shadow: none !important;
            font-size: 0.76rem !important;
            font-weight: 860 !important;
            letter-spacing: 0.015em !important;
            line-height: 1 !important;
            white-space: nowrap !important;
            text-transform: uppercase !important;
            transition: transform 160ms ease, background 160ms ease, border-color 160ms ease, box-shadow 160ms ease !important;
        }}
        .st-key-language_action_en button[kind="primary"],
        .st-key-language_action_fr button[kind="primary"],
        .st-key-language_action_he button[kind="primary"] {{
            border-color: color-mix(in srgb, var(--aiwra-primary) 46%, var(--aiwra-border-soft)) !important;
            background:
                radial-gradient(circle at 30% 15%, color-mix(in srgb, var(--aiwra-text-inverse) 12%, transparent), transparent 35%),
                color-mix(in srgb, var(--aiwra-primary) 18%, var(--aiwra-elevated-card-bg)) !important;
            box-shadow:
                inset 0 0 0 1px color-mix(in srgb, var(--aiwra-primary) 16%, transparent),
                0 7px 18px color-mix(in srgb, var(--aiwra-primary) 14%, transparent) !important;
        }}
        .st-key-theme_action_toggle_header button {{
            min-width: 5.4rem !important;
            padding-inline: 0.68rem !important;
            border-color: color-mix(in srgb, var(--aiwra-primary) 35%, var(--aiwra-border-soft)) !important;
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--aiwra-primary) 12%, transparent), transparent 74%),
                color-mix(in srgb, var(--aiwra-card-bg) 90%, transparent) !important;
            box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--aiwra-text-inverse) 5%, transparent) !important;
        }}
        .st-key-language_action_en button:hover:not(:disabled),
        .st-key-language_action_fr button:hover:not(:disabled),
        .st-key-language_action_he button:hover:not(:disabled),
        .st-key-theme_action_toggle_header button:hover:not(:disabled) {{
            transform: translateY(-1px);
            border-color: color-mix(in srgb, var(--aiwra-primary) 62%, var(--aiwra-border-soft)) !important;
            background: color-mix(in srgb, var(--aiwra-primary-soft) 56%, var(--aiwra-card-bg)) !important;
        }}
        .st-key-language_action_en button:focus-visible,
        .st-key-language_action_fr button:focus-visible,
        .st-key-language_action_he button:focus-visible,
        .st-key-theme_action_toggle_header button:focus-visible {{
            outline: var(--aiwra-focus) !important;
            outline-offset: 2px !important;
        }}
        @media (max-width: 760px) {{
            .st-key-settings_toolbar_header {{
                top: 0.28rem;
                margin-bottom: 0.72rem !important;
            }}
            .st-key-settings_toolbar_header [data-testid="stHorizontalBlock"]:has(.st-key-language_control_cluster):has(.st-key-theme_control_cluster) {{
                width: 100% !important;
                max-width: 100% !important;
                margin-inline-start: 0 !important;
                margin-inline-end: 0 !important;
                justify-content: center !important;
            }}
            .st-key-theme_action_toggle_header button {{
                min-width: 4.9rem !important;
            }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            .st-key-language_action_en button,
            .st-key-language_action_fr button,
            .st-key-language_action_he button,
            .st-key-theme_action_toggle_header button {{
                transition: none !important;
                transform: none !important;
            }}
        }}
        /* AIWRA_P14_HUMAN_HEADER_DOCK_END */

        /* AIWRA_P14_SIDEBAR_RESTORE_BEGIN */
        [data-testid="stHeader"]:has([data-testid="stExpandSidebarButton"]) {{
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
            pointer-events: none !important;
            overflow: visible !important;
        }}
        [data-testid="stHeader"]:has([data-testid="stExpandSidebarButton"]) [data-testid="stToolbar"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            width: 100% !important;
            min-width: 0 !important;
            overflow: visible !important;
            background: transparent !important;
            transform: none !important;
            pointer-events: none !important;
        }}
        [data-testid="stHeader"]:has([data-testid="stExpandSidebarButton"]) [data-testid="stToolbar"] > div,
        [data-testid="stHeader"]:has([data-testid="stExpandSidebarButton"]) [data-testid="stToolbar"] [class*="st-emotion-cache"] {{
            visibility: visible !important;
            overflow: visible !important;
        }}
        [data-testid="stExpandSidebarButton"],
        [data-testid="stHeader"]:has([data-testid="stExpandSidebarButton"]) [data-testid="stExpandSidebarButton"] {{
            position: fixed !important;
            inset-block-start: 0.78rem !important;
            inset-inline-start: 0.78rem !important;
            z-index: 1100 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 2.62rem !important;
            height: 2.62rem !important;
            min-width: 2.62rem !important;
            min-height: 2.62rem !important;
            padding: 0 !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            border: 1px solid color-mix(in srgb, var(--aiwra-primary) 36%, var(--aiwra-border-soft)) !important;
            border-radius: 999px !important;
            color: var(--aiwra-text-primary) !important;
            background:
                radial-gradient(circle at 30% 15%, color-mix(in srgb, var(--aiwra-primary) 18%, transparent), transparent 46%),
                color-mix(in srgb, var(--aiwra-elevated-card-bg) 92%, transparent) !important;
            box-shadow:
                0 12px 30px color-mix(in srgb, var(--aiwra-shadow) 24%, transparent),
                inset 0 0 0 1px color-mix(in srgb, var(--aiwra-text-primary) 5%, transparent) !important;
            backdrop-filter: blur(16px) saturate(140%);
            -webkit-backdrop-filter: blur(16px) saturate(140%);
            transform: none !important;
        }}
        [data-testid="stExpandSidebarButton"] *,
        [data-testid="stHeader"]:has([data-testid="stExpandSidebarButton"]) [data-testid="stExpandSidebarButton"] * {{
            visibility: visible !important;
            opacity: 1 !important;
            color: var(--aiwra-text-primary) !important;
            fill: currentColor !important;
            pointer-events: none !important;
        }}
        [data-testid="stExpandSidebarButton"]:hover,
        [data-testid="stHeader"]:has([data-testid="stExpandSidebarButton"]) [data-testid="stExpandSidebarButton"]:hover {{
            border-color: color-mix(in srgb, var(--aiwra-primary) 66%, var(--aiwra-border-soft)) !important;
            background:
                radial-gradient(circle at 30% 15%, color-mix(in srgb, var(--aiwra-primary) 26%, transparent), transparent 48%),
                color-mix(in srgb, var(--aiwra-primary-soft) 66%, var(--aiwra-elevated-card-bg)) !important;
            box-shadow:
                0 15px 36px color-mix(in srgb, var(--aiwra-shadow) 28%, transparent),
                0 0 0 3px color-mix(in srgb, var(--aiwra-primary) 10%, transparent) !important;
        }}
        [data-testid="stExpandSidebarButton"]:focus-visible {{
            outline: 2px solid var(--aiwra-primary) !important;
            outline-offset: 2px !important;
            box-shadow: var(--aiwra-focus) !important;
        }}
        #MainMenu,
        [data-testid="stMainMenu"],
        [data-testid="stMainMenuButton"] {{
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }}
        @media (max-width: 760px) {{
            [data-testid="stExpandSidebarButton"],
            [data-testid="stHeader"]:has([data-testid="stExpandSidebarButton"]) [data-testid="stExpandSidebarButton"] {{
                inset-block-start: 0.62rem !important;
                inset-inline-start: 0.62rem !important;
                width: 2.5rem !important;
                height: 2.5rem !important;
                min-width: 2.5rem !important;
                min-height: 2.5rem !important;
            }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            [data-testid="stExpandSidebarButton"] {{
                transition: none !important;
                transform: none !important;
            }}
        }}
        /* AIWRA_P14_SIDEBAR_RESTORE_END */


        /* AIWRA_P15_VISUAL_EXPERT_DARK_FIX_BEGIN */

        /*
         * P15 visual hardening.
         * Scope:
         * - dark/light-safe Streamlit selectboxes and virtual dropdowns;
         * - sidebar project selector readability;
         * - collapsed/expanded sidebar control visibility;
         * - disabled controls readable without looking active.
         *
         * Accessibility targets:
         * - normal text aims for WCAG AA 4.5:1;
         * - UI component borders/focus/interactive states aim for 3:1.
         */

        [data-baseweb="select"] > div,
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        .st-key-sidebar_ollama_model [data-baseweb="select"] > div {{
            min-height: 2.75rem !important;
            background:
                linear-gradient(
                    180deg,
                    color-mix(in srgb, var(--aiwra-input-bg) 92%, var(--aiwra-surface-alt) 8%),
                    var(--aiwra-input-bg)
                ) !important;
            border: 1px solid var(--aiwra-input-border) !important;
            border-radius: 0.72rem !important;
            color: var(--aiwra-text-primary) !important;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.055),
                0 0 0 1px rgba(0, 0, 0, 0.08) !important;
            opacity: 1 !important;
        }}

        [data-baseweb="select"] *,
        [data-testid="stSelectbox"] [data-baseweb="select"] *,
        [data-testid="stSidebar"] [data-baseweb="select"] *,
        .st-key-sidebar_ollama_model [data-baseweb="select"] * {{
            color: var(--aiwra-text-primary) !important;
            opacity: 1 !important;
        }}

        [data-baseweb="select"] svg,
        [data-testid="stSelectbox"] svg,
        [data-testid="stSidebar"] [data-baseweb="select"] svg {{
            color: var(--aiwra-text-secondary) !important;
            fill: currentColor !important;
            opacity: 1 !important;
        }}

        [data-baseweb="select"] > div:hover,
        [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
        [data-testid="stSidebar"] [data-baseweb="select"] > div:hover {{
            border-color: color-mix(in srgb, var(--aiwra-focus-ring) 72%, var(--aiwra-input-border)) !important;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.07),
                0 0 0 1px color-mix(in srgb, var(--aiwra-focus-ring) 38%, transparent),
                0 10px 24px rgba(0, 0, 0, 0.16) !important;
        }}

        [data-baseweb="select"] > div:focus-within,
        [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
        [data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {{
            border-color: var(--aiwra-focus-ring) !important;
            box-shadow:
                0 0 0 3px color-mix(in srgb, var(--aiwra-focus-ring) 34%, transparent),
                0 12px 28px rgba(0, 0, 0, 0.18) !important;
            outline: none !important;
        }}

        ul[data-testid="stSelectboxVirtualDropdown"],
        div[data-baseweb="popover"] ul,
        div[role="listbox"] {{
            background:
                linear-gradient(
                    180deg,
                    color-mix(in srgb, var(--aiwra-elevated-card-bg) 94%, #000000 6%),
                    color-mix(in srgb, var(--aiwra-card-bg) 96%, #000000 4%)
                ) !important;
            border: 1px solid var(--aiwra-input-border) !important;
            border-radius: 0.84rem !important;
            box-shadow:
                0 22px 48px rgba(0, 0, 0, 0.34),
                0 0 0 1px rgba(255, 255, 255, 0.04) !important;
            padding: 0.34rem !important;
            overflow: hidden !important;
        }}

        ul[data-testid="stSelectboxVirtualDropdown"] li,
        ul[data-testid="stSelectboxVirtualDropdown"] [role="option"],
        div[data-baseweb="popover"] li,
        div[role="listbox"] [role="option"] {{
            color: var(--aiwra-text-primary) !important;
            background: transparent !important;
            border-radius: 0.56rem !important;
            margin: 0.10rem 0 !important;
            min-height: 2.15rem !important;
            line-height: 1.35 !important;
            opacity: 1 !important;
        }}

        ul[data-testid="stSelectboxVirtualDropdown"] li:hover,
        ul[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
        div[data-baseweb="popover"] li:hover,
        div[role="listbox"] [role="option"]:hover {{
            background: color-mix(in srgb, var(--aiwra-primary) 18%, var(--aiwra-elevated-card-bg)) !important;
            color: var(--aiwra-text-primary) !important;
        }}

        ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"],
        ul[data-testid="stSelectboxVirtualDropdown"] [aria-selected="true"],
        div[role="listbox"] [aria-selected="true"] {{
            background:
                linear-gradient(
                    135deg,
                    color-mix(in srgb, var(--aiwra-primary) 28%, var(--aiwra-elevated-card-bg)),
                    color-mix(in srgb, var(--aiwra-accent) 18%, var(--aiwra-elevated-card-bg))
                ) !important;
            color: var(--aiwra-text-primary) !important;
            box-shadow: inset 3px 0 0 var(--aiwra-focus-ring) !important;
            font-weight: 760 !important;
        }}

        ul[data-testid="stSelectboxVirtualDropdown"] li[aria-disabled="true"],
        ul[data-testid="stSelectboxVirtualDropdown"] [aria-disabled="true"],
        div[role="listbox"] [aria-disabled="true"] {{
            color: var(--aiwra-disabled-text) !important;
            background: transparent !important;
            opacity: 0.86 !important;
        }}

        button:disabled,
        [data-testid="stButton"] button:disabled,
        [data-testid="stDownloadButton"] button:disabled {{
            color: var(--aiwra-button-disabled-text) !important;
            background: var(--aiwra-button-disabled-bg) !important;
            border-color: var(--aiwra-button-disabled-border) !important;
            opacity: 1 !important;
            box-shadow: none !important;
            cursor: not-allowed !important;
        }}

        [data-testid="collapsedControl"] button,
        [data-testid="stExpandSidebarButton"],
        [data-testid="stHeader"] [data-testid="stExpandSidebarButton"] {{
            min-width: 2.45rem !important;
            min-height: 2.45rem !important;
            border-radius: 0.72rem !important;
            border: 1px solid color-mix(in srgb, var(--aiwra-focus-ring) 46%, var(--aiwra-border)) !important;
            background:
                linear-gradient(
                    180deg,
                    color-mix(in srgb, var(--aiwra-elevated-card-bg) 84%, var(--aiwra-primary) 16%),
                    color-mix(in srgb, var(--aiwra-surface) 88%, var(--aiwra-primary) 12%)
                ) !important;
            color: var(--aiwra-text-primary) !important;
            opacity: 1 !important;
            box-shadow:
                0 8px 22px rgba(0, 0, 0, 0.22),
                inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
        }}

        [data-testid="collapsedControl"] button *,
        [data-testid="stExpandSidebarButton"] *,
        [data-testid="stHeader"] [data-testid="stExpandSidebarButton"] * {{
            color: var(--aiwra-text-primary) !important;
            fill: currentColor !important;
            stroke: currentColor !important;
            opacity: 1 !important;
        }}

        [data-testid="collapsedControl"] button:hover,
        [data-testid="stExpandSidebarButton"]:hover,
        [data-testid="stHeader"] [data-testid="stExpandSidebarButton"]:hover {{
            border-color: var(--aiwra-focus-ring) !important;
            background:
                linear-gradient(
                    180deg,
                    color-mix(in srgb, var(--aiwra-primary) 24%, var(--aiwra-elevated-card-bg)),
                    color-mix(in srgb, var(--aiwra-accent) 18%, var(--aiwra-surface))
                ) !important;
            transform: translateY(-1px) !important;
            box-shadow:
                0 14px 30px rgba(0, 0, 0, 0.28),
                0 0 0 3px color-mix(in srgb, var(--aiwra-focus-ring) 22%, transparent) !important;
        }}

        [data-testid="collapsedControl"] button:focus-visible,
        [data-testid="stExpandSidebarButton"]:focus-visible,
        [data-testid="stHeader"] [data-testid="stExpandSidebarButton"]:focus-visible {{
            outline: none !important;
            border-color: var(--aiwra-focus-ring) !important;
            box-shadow:
                0 0 0 3px color-mix(in srgb, var(--aiwra-focus-ring) 42%, transparent),
                0 14px 30px rgba(0, 0, 0, 0.28) !important;
        }}

        /* AIWRA_P15_VISUAL_EXPERT_DARK_FIX_END */


        /* AIWRA_P17_EXACT_DOM_SIDEBAR_BUTTON_BEGIN */

        /*
         * P17 exact DOM emergency patch.
         * Target provided from browser inspector:
         *
         * <div data-testid="stSidebarCollapseButton" class="st-emotion-cache-1gwooyg eelgd2m10">
         *   <button kind="headerNoPadding" data-testid="stBaseButton-headerNoPadding">
         *     <span color="rgba(16, 32, 51, 0.6)">
         *       <span data-testid="stIconMaterial">keyboard_double_arrow_left</span>
         *     </span>
         *   </button>
         * </div>
         *
         * Purpose: make only this collapse control unmistakably visible.
         */

        div[data-testid="stSidebarHeader"] > div[data-testid="stSidebarCollapseButton"],
        div[data-testid="stSidebarCollapseButton"],
        div[data-testid="stSidebarCollapseButton"].st-emotion-cache-1gwooyg,
        .st-emotion-cache-1gwooyg[data-testid="stSidebarCollapseButton"] {{
            position: relative !important;
            z-index: 99999 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;

            width: 2.65rem !important;
            height: 2.65rem !important;
            min-width: 2.65rem !important;
            min-height: 2.65rem !important;
            max-width: 2.65rem !important;
            max-height: 2.65rem !important;

            padding: 0 !important;
            margin: 0 0 0 auto !important;
            overflow: visible !important;

            border-radius: 999px !important;
            border: 2px solid #FCFEFF !important;
            outline: 1px solid rgba(15, 74, 90, 0.72) !important;
            outline-offset: 1px !important;

            background:
                radial-gradient(circle at 30% 18%, rgba(255, 255, 255, 0.92), rgba(245, 188, 74, 0.92) 42%, rgba(232, 149, 69, 0.96) 100%) !important;

            color: #09131F !important;
            box-shadow:
                0 0 0 4px rgba(245, 188, 74, 0.28),
                0 14px 34px rgba(0, 0, 0, 0.34),
                inset 0 1px 0 rgba(255, 255, 255, 0.82) !important;

            transform: none !important;
            transition:
                transform 120ms ease,
                box-shadow 120ms ease,
                border-color 120ms ease,
                background 120ms ease !important;
        }}

        div[data-testid="stSidebarCollapseButton"] button,
        div[data-testid="stSidebarCollapseButton"] button[kind="headerNoPadding"],
        div[data-testid="stSidebarCollapseButton"] button[data-testid="stBaseButton-headerNoPadding"],
        div[data-testid="stSidebarHeader"] div[data-testid="stSidebarCollapseButton"] button[data-testid="stBaseButton-headerNoPadding"] {{
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;

            width: 100% !important;
            height: 100% !important;
            min-width: 100% !important;
            min-height: 100% !important;

            padding: 0 !important;
            margin: 0 !important;

            background: transparent !important;
            border: 0 !important;
            border-radius: inherit !important;
            box-shadow: none !important;

            color: #09131F !important;
            opacity: 1 !important;
            visibility: visible !important;
            pointer-events: auto !important;
        }}

        div[data-testid="stSidebarCollapseButton"] span,
        div[data-testid="stSidebarCollapseButton"] span[color],
        div[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
        div[data-testid="stSidebarCollapseButton"] .st-emotion-cache-snk3wv,
        div[data-testid="stSidebarCollapseButton"] button[data-testid="stBaseButton-headerNoPadding"] span,
        div[data-testid="stSidebarCollapseButton"] button[data-testid="stBaseButton-headerNoPadding"] [data-testid="stIconMaterial"] {{
            color: #09131F !important;
            fill: #09131F !important;
            stroke: #09131F !important;
            opacity: 1 !important;
            visibility: visible !important;
            font-weight: 900 !important;
            text-shadow: 0 1px 0 rgba(255, 255, 255, 0.22) !important;
        }}

        div[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {{
            font-size: 1.58rem !important;
            line-height: 1 !important;
            width: 1.58rem !important;
            height: 1.58rem !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        div[data-testid="stSidebarCollapseButton"]::after {{
            content: "" !important;
            position: absolute !important;
            inset: -0.32rem !important;
            border-radius: 999px !important;
            border: 1px solid rgba(245, 188, 74, 0.42) !important;
            pointer-events: none !important;
        }}

        div[data-testid="stSidebarCollapseButton"]:hover,
        div[data-testid="stSidebarCollapseButton"]:has(button:hover) {{
            border-color: #FFFFFF !important;
            outline-color: rgba(15, 74, 90, 0.96) !important;
            background:
                radial-gradient(circle at 30% 18%, rgba(255, 255, 255, 1), rgba(255, 204, 92, 1) 42%, rgba(232, 149, 69, 1) 100%) !important;
            box-shadow:
                0 0 0 5px rgba(245, 188, 74, 0.38),
                0 18px 42px rgba(0, 0, 0, 0.42),
                inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
            transform: translateY(-1px) scale(1.03) !important;
        }}

        div[data-testid="stSidebarCollapseButton"]:focus-within,
        div[data-testid="stSidebarCollapseButton"] button:focus-visible {{
            outline: 3px solid #8DB8FF !important;
            outline-offset: 3px !important;
            box-shadow:
                0 0 0 6px rgba(141, 184, 255, 0.34),
                0 18px 42px rgba(0, 0, 0, 0.42) !important;
        }}

        @media (prefers-reduced-motion: reduce) {{
            div[data-testid="stSidebarCollapseButton"],
            div[data-testid="stSidebarCollapseButton"]:hover {{
                transition: none !important;
                transform: none !important;
            }}
        }}

        /* AIWRA_P17_EXACT_DOM_SIDEBAR_BUTTON_END */

/* AIWRA_2026_VISUAL_SYSTEM_BEGIN
   P18.7 Visual System Consolidation.
   Scope: presentation only. Theme comes from AIWRA tokens.
   Icon rule: normal text inherits Lato stack; Material glyphs keep icon fonts.
   Shutdown rule: one compact top-left sidebar control, no hover displacement.
*/

html, body, .stApp, [data-testid="stAppViewContainer"] {{
  font-family: var(--aiwra-font-stack);
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--aiwra-primary) 7%, transparent), transparent 32rem),
    radial-gradient(circle at top right, color-mix(in srgb, var(--aiwra-accent) 7%, transparent), transparent 30rem),
    var(--aiwra-page-bg) !important;
  color: var(--aiwra-text-primary) !important;
}}

:where(
  [data-testid="stMarkdownContainer"],
  [data-testid="stWidgetLabel"],
  [data-testid="stTextInput"],
  [data-testid="stTextArea"],
  [data-testid="stSelectbox"],
  [data-testid="stRadio"],
  [data-testid="stCheckbox"],
  [data-testid="stToggle"],
  [data-testid="stButton"] button,
  [data-testid="stDownloadButton"] button,
  [data-baseweb="select"],
  [data-baseweb="popover"],
  [role="listbox"],
  [role="option"],
  button,
  input,
  textarea,
  label
) {{
  font-family: var(--aiwra-font-stack) !important;
}}

[data-testid="stIconMaterial"],
[data-testid="collapsedControl"] [data-testid="stIconMaterial"],
div[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
[data-testid="stExpander"] details summary [data-testid="stIconMaterial"],
[data-testid="stExpander"] summary [data-testid="stIconMaterial"],
details summary [data-testid="stIconMaterial"],
.material-symbols-outlined,
.material-symbols-rounded,
.material-symbols-sharp,
.material-icons,
.material-icons-outlined,
.material-icons-round,
.material-icons-sharp,
.material-icons-two-tone {{
  font-family:
    "Material Symbols Rounded",
    "Material Symbols Outlined",
    "Material Symbols Sharp",
    "Material Icons",
    "Material Icons Outlined",
    "Material Icons Round",
    "Material Icons Sharp",
    "Material Icons Two Tone" !important;
  font-weight: normal !important;
  font-style: normal !important;
  line-height: 1 !important;
  letter-spacing: 0 !important;
  text-transform: none !important;
  white-space: nowrap !important;
  word-wrap: normal !important;
  direction: ltr !important;
  unicode-bidi: isolate !important;
  -webkit-font-feature-settings: "liga" !important;
  font-feature-settings: "liga" !important;
  -webkit-font-smoothing: antialiased !important;
  text-rendering: optimizeLegibility !important;
}}

[data-testid="stHeader"] {{
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--aiwra-page-bg) 92%, transparent),
    color-mix(in srgb, var(--aiwra-page-bg) 64%, transparent),
    transparent
  ) !important;
  border-bottom: 1px solid color-mix(in srgb, var(--aiwra-border-soft) 72%, transparent) !important;
  backdrop-filter: blur(18px) saturate(130%) !important;
}}

[data-testid="stToolbar"] {{
  opacity: 0.16 !important;
  transform: scale(0.94) !important;
  transform-origin: top right !important;
  transition: opacity 140ms ease, transform 140ms ease !important;
}}
[data-testid="stToolbar"]:hover,
[data-testid="stToolbar"]:focus-within {{
  opacity: 0.88 !important;
  transform: scale(1) !important;
}}

[data-testid="stSidebar"] {{
  background: var(--aiwra-sidebar-bg) !important;
  color: var(--aiwra-text-primary) !important;
  border-right: 1px solid var(--aiwra-border) !important;
  box-shadow: 14px 0 42px color-mix(in srgb, var(--aiwra-shadow) 24%, transparent) !important;
}}
[data-testid="stSidebarContent"] {{
  background: transparent !important;
  color: var(--aiwra-text-primary) !important;
  padding-block: 3.95rem 1rem !important;
}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not([data-testid="stIconMaterial"]),
[data-testid="stSidebar"] small {{
  color: var(--aiwra-text-secondary) !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong,
[data-testid="stSidebar"] b {{
  color: var(--aiwra-text-primary) !important;
}}
[data-testid="stSidebarHeader"] {{
  min-height: 3.15rem !important;
  border-bottom: 1px solid var(--aiwra-border-soft) !important;
}}

[data-testid="collapsedControl"],
div[data-testid="stSidebarHeader"] > div[data-testid="stSidebarCollapseButton"],
div[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"] {{
  opacity: 1 !important;
  visibility: visible !important;
  pointer-events: auto !important;
  z-index: 999999 !important;
}}

[data-testid="collapsedControl"] button,
div[data-testid="stSidebarCollapseButton"] button[data-testid="stBaseButton-headerNoPadding"],
[data-testid="stExpandSidebarButton"] button,
[data-testid="stExpandSidebarButton"] [data-testid="stBaseButton-headerNoPadding"] {{
  display: grid !important;
  place-items: center !important;
  width: 2.35rem !important;
  height: 2.35rem !important;
  min-width: 2.35rem !important;
  min-height: 2.35rem !important;
  padding: 0 !important;
  border-radius: 999px !important;
  background: var(--aiwra-button-secondary-bg, var(--aiwra-card-bg)) !important;
  color: var(--aiwra-text-primary) !important;
  border: 1px solid var(--aiwra-border) !important;
  box-shadow: var(--aiwra-shadow-sm) !important;
}}

[data-testid="collapsedControl"] [data-testid="stIconMaterial"],
div[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {{
  color: var(--aiwra-text-primary) !important;
  font-size: 1.28rem !important;
}}

[data-testid="stMarkdownContainer"] {{
  color: var(--aiwra-text-secondary) !important;
}}
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {{
  color: var(--aiwra-text-primary) !important;
  letter-spacing: 0 !important;
}}

.aiwra-card,
.aiwra-panel,
.aiwra-kpi-card,
.aiwra-cockpit-card,
.aiwra-evidence-card,
.aiwra-control-card,
.aiwra-local-ai-card,
.aiwra-risk-card,
[data-testid="stMetric"],
[data-testid="stExpander"] details {{
  background: var(--aiwra-card-bg) !important;
  color: var(--aiwra-text-primary) !important;
  border: 1px solid var(--aiwra-border) !important;
  border-radius: var(--aiwra-radius-lg) !important;
  box-shadow: var(--aiwra-shadow-sm) !important;
}}

.aiwra-badge,
.aiwra-status-chip,
.aiwra-local-chip,
.aiwra-risk-chip,
.aiwra-pill {{
  display: inline-flex !important;
  align-items: center !important;
  gap: 0.38rem !important;
  border-radius: 999px !important;
  border: 1px solid var(--aiwra-border) !important;
  background: var(--aiwra-surface-alt) !important;
  color: var(--aiwra-text-primary) !important;
  font-weight: 700 !important;
  letter-spacing: 0 !important;
}}

[data-testid="stButton"] button,
[data-testid="stBaseButton-secondary"],
button[kind="secondary"],
button[kind="primary"] {{
  border-radius: var(--aiwra-radius-md) !important;
  border: 1px solid var(--aiwra-border) !important;
  color: var(--aiwra-text-primary) !important;
  background: var(--aiwra-button-secondary-bg, var(--aiwra-card-bg)) !important;
  box-shadow: var(--aiwra-shadow-sm) !important;
  font-weight: 800 !important;
  transition: transform 120ms ease, border-color 120ms ease, box-shadow 120ms ease, background 120ms ease !important;
}}
[data-testid="stButton"] button:hover,
[data-testid="stBaseButton-secondary"]:hover,
button[kind="secondary"]:hover,
button[kind="primary"]:hover {{
  transform: translateY(-1px) !important;
  border-color: var(--aiwra-primary) !important;
}}
[data-testid="stButton"] button:disabled,
button:disabled,
[aria-disabled="true"] {{
  opacity: 0.55 !important;
  cursor: not-allowed !important;
  transform: none !important;
  box-shadow: none !important;
}}

button:focus-visible,
[role="button"]:focus-visible,
a:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
[data-baseweb="select"] div:focus-visible,
[data-testid="stBaseButton-secondary"]:focus-visible,
div[role="combobox"]:focus-visible {{
  outline: none !important;
  box-shadow:
    0 0 0 3px color-mix(in srgb, var(--aiwra-primary) 30%, transparent),
    0 0 0 1px var(--aiwra-primary) !important;
}}

[data-testid="stSelectbox"],
[data-testid="stRadio"],
[data-testid="stCheckbox"],
[data-testid="stTextArea"],
[data-testid="stTextInput"] {{
  color: var(--aiwra-text-primary) !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-baseweb="select"] {{
  background: var(--aiwra-input-bg) !important;
  border-radius: var(--aiwra-radius-md) !important;
}}
[data-baseweb="select"] > div,
[data-baseweb="select"] div[role="combobox"],
textarea,
input {{
  background: var(--aiwra-input-bg) !important;
  border-color: var(--aiwra-input-border) !important;
  color: var(--aiwra-text-primary) !important;
  border-radius: var(--aiwra-radius-md) !important;
}}
textarea::placeholder,
input::placeholder {{
  color: var(--aiwra-muted) !important;
}}
ul[data-testid="stSelectboxVirtualDropdown"],
div[role="listbox"] {{
  background: var(--aiwra-input-bg) !important;
  color: var(--aiwra-text-primary) !important;
  border: 1px solid var(--aiwra-input-border) !important;
  border-radius: var(--aiwra-radius-md) !important;
  box-shadow: var(--aiwra-shadow-md) !important;
}}
ul[data-testid="stSelectboxVirtualDropdown"] li,
ul[data-testid="stSelectboxVirtualDropdown"] [role="option"],
div[role="listbox"] [role="option"] {{
  color: var(--aiwra-text-primary) !important;
  background: transparent !important;
}}
ul[data-testid="stSelectboxVirtualDropdown"] li:hover,
ul[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
div[role="listbox"] [role="option"]:hover {{
  background: color-mix(in srgb, var(--aiwra-primary) 12%, var(--aiwra-input-bg)) !important;
  color: var(--aiwra-text-primary) !important;
}}
ul[data-testid="stSelectboxVirtualDropdown"] [aria-selected="true"],
div[role="listbox"] [aria-selected="true"] {{
  background: color-mix(in srgb, var(--aiwra-primary) 18%, var(--aiwra-input-bg)) !important;
  color: var(--aiwra-text-primary) !important;
}}

[data-testid="stExpander"] details summary,
[data-testid="stExpander"] summary,
details summary {{
  color: var(--aiwra-text-primary) !important;
  font-weight: 800 !important;
  letter-spacing: 0 !important;
}}
[data-testid="stExpander"] details summary [data-testid="stIconMaterial"],
[data-testid="stExpander"] summary [data-testid="stIconMaterial"],
details summary [data-testid="stIconMaterial"] {{
  color: var(--aiwra-text-primary) !important;
  font-size: 1.22rem !important;
}}

.aiwra-danger,
.aiwra-danger-zone,
.aiwra-reset-zone,
[data-testid="stAlert"] {{
  border-radius: var(--aiwra-radius-lg) !important;
}}
.aiwra-danger-zone,
.aiwra-reset-zone {{
  background: color-mix(in srgb, var(--aiwra-danger) 10%, var(--aiwra-card-bg)) !important;
  border: 1px solid color-mix(in srgb, var(--aiwra-danger) 34%, transparent) !important;
}}
.aiwra-danger-zone button,
.aiwra-reset-zone button {{
  border-color: color-mix(in srgb, var(--aiwra-danger) 55%, transparent) !important;
}}

.st-key-aiwra_power_shutdown_zone {{
  position: fixed !important;
  top: 0.88rem !important;
  left: 1.05rem !important;
  width: 3.25rem !important;
  min-width: 3.25rem !important;
  max-width: 3.25rem !important;
  z-index: 1000002 !important;
  margin: 0 !important;
  padding: 0 !important;
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}}

.st-key-aiwra_power_shutdown_zone [data-testid="stCaptionContainer"] {{
  display: none !important;
}}

.st-key-aiwra_power_shutdown_button [data-testid="stButton"] {{
  display: grid !important;
  place-items: center !important;
  width: 3.25rem !important;
  min-width: 3.25rem !important;
  max-width: 3.25rem !important;
  margin: 0 !important;
  padding: 0 !important;
}}

.st-key-aiwra_power_shutdown_button button {{
  display: grid !important;
  place-items: center !important;
  width: 2.82rem !important;
  min-width: 2.82rem !important;
  max-width: 2.82rem !important;
  height: 2.82rem !important;
  min-height: 2.82rem !important;
  max-height: 2.82rem !important;
  margin: 0 !important;
  padding: 0 !important;
  border-radius: 1.05rem !important;
  background: var(--aiwra-card-bg) !important;
  color: var(--aiwra-text-primary) !important;
  border: 1px solid var(--aiwra-border) !important;
  box-shadow: var(--aiwra-shadow-md) !important;
  transform: none !important;
  overflow: visible !important;
}}

.st-key-aiwra_power_shutdown_button button:hover,
.st-key-aiwra_power_shutdown_button button:focus,
.st-key-aiwra_power_shutdown_button button:active {{
  transform: none !important;
  background: var(--aiwra-card-bg) !important;
  color: var(--aiwra-text-primary) !important;
  border-color: color-mix(in srgb, var(--aiwra-danger) 48%, var(--aiwra-border)) !important;
}}

.st-key-aiwra_power_shutdown_button button [data-testid="stMarkdownContainer"],
.st-key-aiwra_power_shutdown_button button [data-testid="stMarkdownContainer"] p,
.st-key-aiwra_power_shutdown_button button p,
.st-key-aiwra_power_shutdown_button button span:not([data-testid="stIconMaterial"]) {{
  display: inline-grid !important;
  place-items: center !important;
  width: auto !important;
  min-width: 0 !important;
  height: auto !important;
  margin: 0 !important;
  padding: 0 !important;
  color: var(--aiwra-text-primary) !important;
  font-family: var(--aiwra-font-stack) !important;
  font-size: 1.42rem !important;
  font-weight: 900 !important;
  line-height: 1 !important;
  text-align: center !important;
  opacity: 1 !important;
  visibility: visible !important;
  text-indent: 0 !important;
  white-space: nowrap !important;
}}

[dir="rtl"] .aiwra-card,
[dir="rtl"] .aiwra-panel,
[dir="rtl"] .aiwra-cockpit-card,
[dir="rtl"] [data-testid="stMarkdownContainer"] {{
  text-align: start !important;
}}
[dir="rtl"] code,
[dir="rtl"] pre,
[dir="rtl"] .aiwra-code,
[dir="rtl"] .aiwra-ltr,
[dir="rtl"] .aiwra-model-name,
[dir="rtl"] .aiwra-endpoint,
[dir="rtl"] [data-aiwra-ltr="true"] {{
  direction: ltr !important;
  unicode-bidi: isolate !important;
  text-align: left !important;
}}

@media (max-width: 900px) {{
  .aiwra-card,
  .aiwra-panel,
  .aiwra-cockpit-card {{
    border-radius: var(--aiwra-radius-md) !important;
  }}
}}

@media (prefers-reduced-motion: reduce) {{
  [data-testid="stToolbar"],
  [data-testid="stButton"] button,
  [data-testid="stDownloadButton"] button,
  div[data-testid="stSidebarCollapseButton"],
  [data-testid="stExpandSidebarButton"] {{
    transition: none !important;
    transform: none !important;
  }}
}}

/* AIWRA_2026_VISUAL_SYSTEM_END */
</style>
        """
    )


def render_badge(prefix: str, label: str, token: dict[str, Any], description: str = "") -> None:
    title = f"{prefix}: {label}"
    if description:
        title = f"{title} - {description}"
    render_html(
        f"""<span class="aiwra-badge" title="{_escape(title)}" style="color:{token['color']}; background:{token['background']}; border-color:{token['border']};">{_escape(prefix)}: {_escape(label)}</span>"""
    )


def render_severity_badge(severity: object, language: str = "en") -> None:
    token = severity_token(severity, language)
    render_badge(t("severity_label", language, "Severity"), token["label"], token, token["description"])


def render_status_badge(status: object, language: str = "en") -> None:
    token = status_token(status, language)
    render_badge(t("status_label", language, "Status"), token["label"], token, token["description"])


def render_source_status_chip(status: object, language: str = "en") -> None:
    token = status_token(status, language)
    render_badge(t("source_label", language, "Source"), token["label"], token, token["description"])


def render_metric_card(
    label: str,
    value: object,
    source: str,
    meaning: str,
    limit: str,
    status: str = "calculated",
    language: str = "en",
) -> None:
    token = status_token(status, language)
    render_html(
        f"""
        <div class="aiwra-card">
            <div class="aiwra-label">{_escape(label)}</div>
            <span class="aiwra-kpi-value">{_escape(value)}</span>
            <span class="aiwra-badge"
                  style="color:{token['color']}; background:{token['background']}; border-color:{token['border']};">
                {_escape(t('source_label', language, 'Source'))}: {_escape(token['label'])}
            </span>
            <p><strong>{_escape(t('meaning_label', language, 'Meaning'))}:</strong> {_escape(meaning)}</p>
            <p><strong>{_escape(t('limit_label', language, 'Limit'))}:</strong> {_escape(limit)}</p>
            <p><strong>{_escape(t('source_label', language, 'Source'))}:</strong> {_escape(source)}</p>
        </div>
        """
    )


def render_bento_cards(cards: list[dict[str, Any]], language: str = "en") -> None:
    html_cards = []
    for index, card in enumerate(cards, start=1):
        status = status_token(card.get("status", "calculated"), language)
        severity = card.get("severity")
        strip_color = "var(--aiwra-primary)"
        if severity:
            strip_color = severity_token(severity, language)["color"]
        card_class = "aiwra-bento-card aiwra-bento-wide" if index in {1, 6} else "aiwra-bento-card"
        html_cards.append(
            f"<div class=\"{card_class}\">"
            f"<div class=\"aiwra-severity-strip\" style=\"background:{strip_color};\"></div>"
            f"<div class=\"aiwra-bento-title\">{_escape(card.get('title', ''))}</div>"
            f"<div class=\"aiwra-bento-value\">{_escape(card.get('value', ''))}</div>"
            f"<span class=\"aiwra-badge\" style=\"color:{status['color']}; background:{status['background']}; border-color:{status['border']};\">"
            f"{_escape(t('source_label', language, 'Source'))}: {_escape(status['label'])}</span>"
            f"<p><strong>{_escape(t('meaning_label', language, 'Meaning'))}:</strong> {_escape(card.get('meaning', ''))}</p>"
            f"<p><strong>{_escape(t('limit_label', language, 'Limit'))}:</strong> {_escape(card.get('limit', ''))}</p>"
            f"<p><strong>{_escape(t('source_label', language, 'Source'))}:</strong> {_escape(card.get('source', ''))}</p>"
            "</div>"
        )
    render_html(f"<div class=\"aiwra-bento\">{''.join(html_cards)}</div>")


def render_app_status_header(
    title: str,
    subtitle: str,
    status_items: list[dict[str, object]],
    language: str = "en",
) -> None:
    items_html = ""
    for item in status_items[:4]:
        items_html += (
            "<div class='aiwra-status-item'>"
            f"<span>{_escape(item.get('label', ''))}</span>"
            f"<strong>{_escape(item.get('value', ''))}</strong>"
            "</div>"
        )
    render_html(
        f"""
        <div class="aiwra-shell-header" aria-label="{_escape(title)}">
            <div class="aiwra-shell-product">
                <span class="aiwra-shell-kicker">
                    <span class="aiwra-shell-heartbeat" aria-hidden="true"></span><bdi class="aiwra-technical">127.0.0.1</bdi> · {_escape(t('shell_local_first_badge', language, 'Local-first'))} · {_escape(t('shell_advisory_ai_badge', language, 'Advisory AI only'))}
                </span>
                <div class="aiwra-shell-title">{_escape(title)}</div>
                <p class="aiwra-shell-subtitle">{_escape(subtitle)}</p>
            </div>
            <div class="aiwra-status-strip">
                {items_html}
            </div>
        </div>
        """
    )


def render_command_cockpit(cards: list[dict[str, object]], language: str = "en") -> None:
    html_cards = []
    for card in cards[:4]:
        token = status_token(card.get("status", "calculated"), language)
        value = _escape(card.get("value", ""))
        if card.get("technical_value"):
            value = f'<bdi class="aiwra-technical">{value}</bdi>'
        html_cards.append(
            "<div class=\"aiwra-command-card\" "
            f"style=\"--command-color:{token['color']}; --command-border:{token['border']};\">"
            f"<div class=\"aiwra-command-title\">{_escape(card.get('title', ''))}</div>"
            f"<span class=\"aiwra-badge\" style=\"color:{token['color']}; background:{token['background']}; border-color:{token['border']};\">"
            f"{_escape(token['label'])}</span>"
            f"<strong>{value}</strong>"
            f"<p>{_escape(card.get('body', ''))}</p>"
            "</div>"
        )
    render_html(f"<div class=\"aiwra-command-cockpit\">{''.join(html_cards)}</div>")


def render_workbench_frame(title: str, body: str, checks: list[str], language: str = "en") -> None:
    checks_html = "".join(
        f"<span class='aiwra-workbench-check'>✓ {_escape(item)}</span>"
        for item in checks[:5]
        if str(item).strip()
    )
    render_html(
        "<div class=\"aiwra-workbench-frame\" "
        f"aria-label=\"{_escape(title)}\">"
        f"<div class=\"aiwra-workbench-frame-title\">{_escape(title)}</div>"
        f"<p>{_escape(body)}</p>"
        f"<div class=\"aiwra-workbench-checks\">{checks_html}</div>"
        "</div>"
    )


def render_state_panel(
    title: str,
    body: str,
    state: str = "uncertain",
    detail: str = "",
    icon: str = "•",
    language: str = "en",
) -> None:
    token = status_token(state, language)
    detail_html = f"<small>{_escape(detail)}</small>" if detail else ""
    render_html(
        f"""
        <div class="aiwra-state-panel"
                 style="--state-color:{token['color']}; --state-bg:{token['background']}; --state-border:{token['border']};"
                 aria-label="{_escape(title)}">
            <span class="aiwra-state-icon" aria-hidden="true">{_escape(icon)}</span>
            <div>
                <div class="aiwra-state-title">{_escape(title)}</div>
                <p>{_escape(body)}</p>
                {detail_html}
            </div>
        </div>
        """
    )


MISSION_PULSE_STATES = {
    "idle": "not_available",
    "empty": "not_available",
    "ready_to_analyze": "recommended",
    "analyzing": "calculated",
    "deterministic_ready": "local_only",
    "advisory_unavailable": "not_available",
    "error": "needs_human_review",
}


PIPELINE_STAGE_IDS = ("input", "local_rules", "evidence", "human_review", "report")
PIPELINE_STAGE_LABEL_KEYS = {
    "input": ("pipeline_input", "Input"),
    "local_rules": ("pipeline_local_rules", "Local rules"),
    "evidence": ("pipeline_evidence", "Evidence"),
    "human_review": ("pipeline_human_review", "Human review"),
    "report": ("pipeline_report", "Report"),
}


def render_mission_pulse(
    status: str,
    title: str,
    body: str,
    language: str = "en",
    detail: str = "",
    target: Any | None = None,
) -> None:
    pulse_status = str(status or "idle").casefold().strip().replace("-", "_").replace(" ", "_")
    pulse_status = pulse_status if pulse_status in MISSION_PULSE_STATES else "idle"
    token = status_token(MISSION_PULSE_STATES[pulse_status], language)
    detail_html = f"<small>{_escape(detail)}</small>" if detail else ""
    render_html(
        f"""
        <div class="aiwra-mission-pulse aiwra-mission-pulse--{pulse_status}"
             style="--mission-color:{token['color']}; --mission-bg:{token['background']}; --mission-border:{token['border']};"
             aria-label="{_escape(title)}">
            <div class="aiwra-mission-visual" aria-hidden="true">
                <div class="aiwra-mission-orbit"></div>
                <div class="aiwra-mission-core">
                    <span class="aiwra-mission-rocket"></span>
                    <span class="aiwra-mission-flame"></span>
                </div>
            </div>
            <div class="aiwra-mission-copy">
                <span class="aiwra-mission-status">{_escape(token['label'])}</span>
                <div class="aiwra-mission-title">{_escape(title)}</div>
                <p>{_escape(body)}</p>
                {detail_html}
            </div>
        </div>
        """,
        target=target,
    )


def render_local_pipeline_strip(stage: str, language: str, target: Any | None = None) -> None:
    active_stage = str(stage or "input").casefold().strip().replace("-", "_").replace(" ", "_")
    if active_stage not in PIPELINE_STAGE_IDS:
        active_stage = "input"
    active_index = PIPELINE_STAGE_IDS.index(active_stage)
    steps_html: list[str] = []
    for index, stage_id in enumerate(PIPELINE_STAGE_IDS):
        label_key, fallback = PIPELINE_STAGE_LABEL_KEYS[stage_id]
        if index < active_index:
            state_class = "aiwra-pipeline-step--done"
            state_label = t("pipeline_done_label", language, "Done")
        elif index == active_index:
            state_class = "aiwra-pipeline-step--active"
            state_label = t("pipeline_running_label", language, "Active")
        else:
            state_class = ""
            state_label = t("pipeline_ready_label", language, "Ready")
        steps_html.append(
            f"<span class=\"aiwra-pipeline-step {state_class}\" title=\"{_escape(state_label)}\">"
            "<span class=\"aiwra-pipeline-orb\" aria-hidden=\"true\"></span>"
            f"{_escape(t(label_key, language, fallback))}"
            "</span>"
        )
        if index < len(PIPELINE_STAGE_IDS) - 1:
            steps_html.append("<span class=\"aiwra-pipeline-connector\" aria-hidden=\"true\"></span>")
    render_html(
        f"""
        <div class="aiwra-pipeline-strip" aria-label="{_escape(t('pipeline_stage_label', language, 'Local deterministic pipeline'))}">
            {''.join(steps_html)}
        </div>
        """,
        target=target,
    )


def render_loading_panel(
    title: str,
    body: str,
    status: str = "local_only",
    detail: str = "",
    language: str = "en",
    target: Any | None = None,
) -> None:
    status_key = normalize_status_for_loading(status)
    token = status_token(status_key, language)
    status_label = token["label"]
    if status == "advisory":
        status_label = t("shell_advisory_ai_badge", language, "Advisory AI only")
    loading_color = {
        "calculated": "var(--aiwra-loading-deterministic)",
        "local_only": "var(--aiwra-loading)",
        "advisory": "var(--aiwra-loading-local-ai)",
        "simulated": "var(--aiwra-loading-simulation)",
        "recommended": "var(--aiwra-loading-export)",
    }.get(status, token["color"])
    loading_border = "var(--aiwra-loading-border)"
    detail_html = f"<small>{_escape(detail)}</small>" if detail else ""
    render_html(
        f"""
        <div class="aiwra-loading-panel"
             style="--loading-color:{loading_color}; --loading-border:{loading_border};">
            <div class="aiwra-loading-orb" aria-hidden="true"></div>
            <div>
                <span class="aiwra-loading-status">{_escape(status_label)}</span>
                <div class="aiwra-loading-title">{_escape(title)}</div>
                <p>{_escape(body)}</p>
                {detail_html}
            </div>
        </div>
        """,
        target=target,
    )


def normalize_status_for_loading(status: str) -> str:
    if status in {"advisory", "simulated"}:
        return "local_only" if status == "advisory" else "simulated"
    return status


def render_deterministic_loading_panel(language: str, target: Any | None = None) -> None:
    if target is not None:
        with target.container():
            render_mission_pulse(
                "analyzing",
                t("loading_deterministic_title", language, "Analyzing locally..."),
                t(
                    "loading_deterministic_body",
                    language,
                    "The deterministic engine is reviewing evidence. No cloud call. No score is final yet.",
                ),
                language,
            )
            render_local_pipeline_strip("local_rules", language)
        return
    render_mission_pulse(
        "analyzing",
        t("loading_deterministic_title", language, "Analyzing locally..."),
        t(
            "loading_deterministic_body",
            language,
            "The deterministic engine is reviewing evidence. No cloud call. No score is final yet.",
        ),
        language,
        target=target,
    )
    render_local_pipeline_strip("local_rules", language, target=target)


def render_local_ai_loading_panel(language: str, target: Any | None = None) -> None:
    render_loading_panel(
        t("loading_local_ai_title", language, "Generating local advisory narrative..."),
        t(
            "loading_local_ai_body",
            language,
            "Local AI can draft wording only. Scores, findings, controls and simulation stay deterministic.",
        ),
        "advisory",
        "",
        language,
        target=target,
    )


def render_simulation_loading_panel(language: str, target: Any | None = None) -> None:
    render_loading_panel(
        t("loading_simulation_title", language, "Simulating residual risk locally..."),
        t(
            "loading_simulation_body",
            language,
            "Selected controls are hypothetical until implementation evidence proves they exist.",
        ),
        "simulated",
        "",
        language,
        target=target,
    )


def render_export_loading_panel(language: str, target: Any | None = None) -> None:
    render_loading_panel(
        t("loading_export_title", language, "Preparing local export..."),
        t(
            "loading_export_body",
            language,
            "Markdown and JSON are generated from deterministic local results.",
        ),
        "recommended",
        "",
        language,
        target=target,
    )


def render_risk_cockpit(
    score: object,
    severity: object,
    finding_count: int,
    human_review_required: bool,
    saved: bool,
    simulation_state: str,
    language: str = "en",
) -> None:
    severity_style = severity_token(severity, language)
    review_text = t("yes_label", language, "Yes") if human_review_required else t("no_label", language, "No")
    saved_text = t("saved_label", language, "Saved") if saved else t("not_saved_label", language, "Not saved")
    simulation_text = (
        t("simulation_active_label", language, "Hypothetical result available")
        if simulation_state == "simulated"
        else t("not_run_label", language, "Not run")
    )
    review_color = "var(--aiwra-medium)" if human_review_required else "var(--aiwra-low)"
    saved_color = "var(--aiwra-low)" if saved else "var(--aiwra-uncertain)"
    simulation_color = "var(--aiwra-simulated)" if simulation_state == "simulated" else "var(--aiwra-uncertain)"
    render_html(
        f"""
        <div class="aiwra-cockpit aiwra-cockpit--live" style="--cockpit-color:{severity_style['color']};"
                 aria-label="{_escape(t('risk_cockpit_title', language, 'Risk cockpit'))}">
            <div class="aiwra-cockpit-scan" aria-hidden="true"></div>
            <div class="aiwra-cockpit-cell aiwra-cockpit-main">
                <span class="aiwra-cockpit-label">{_escape(t('raw_risk_metric', language, 'Raw risk'))}</span>
                <span class="aiwra-cockpit-score-glow"><span class="aiwra-cockpit-score">{_escape(score)}</span></span>
                <span class="aiwra-cockpit-value">{_escape(severity_style['label'])}</span>
                <span class="aiwra-cockpit-note">{_escape(severity_style['description'])}</span>
            </div>
            <div class="aiwra-cockpit-cell">
                <span class="aiwra-cockpit-label">{_escape(t('finding_count_label', language, 'Findings'))}</span>
                <span class="aiwra-cockpit-value">{_escape(finding_count)}</span>
                <span class="aiwra-cockpit-note">{_escape(t('cockpit_findings_note', language, 'Evidence-linked attention points'))}</span>
            </div>
            <div class="aiwra-cockpit-cell">
                <span class="aiwra-cockpit-label">{_escape(t('human_review_required_label', language, 'Human review required'))}</span>
                <span class="aiwra-cockpit-value" style="color:{review_color};">◆ {_escape(review_text)}</span>
                <span class="aiwra-cockpit-note">{_escape(t('cockpit_human_note', language, 'The engine does not approve production use'))}</span>
            </div>
            <div class="aiwra-cockpit-cell">
                <span class="aiwra-cockpit-label">{_escape(t('exec_local_only_title', language, 'Local-only analysis'))}</span>
                <span class="aiwra-cockpit-value" style="color:var(--aiwra-low);"><i class="aiwra-status-dot"></i>{_escape(t('active_label', language, 'Active'))}</span>
                <span class="aiwra-cockpit-note"><bdi class="aiwra-technical">127.0.0.1</bdi> · {_escape(t('home_badge_no_cloud', language, 'No cloud required'))}</span>
            </div>
            <div class="aiwra-cockpit-cell">
                <span class="aiwra-cockpit-label">{_escape(t('cockpit_saved_state', language, 'Local history'))}</span>
                <span class="aiwra-cockpit-value" style="color:{saved_color};">● {_escape(saved_text)}</span>
                <span class="aiwra-cockpit-note">{_escape(t('cockpit_saved_note', language, 'Persistence occurs only after explicit save'))}</span>
            </div>
            <div class="aiwra-cockpit-cell">
                <span class="aiwra-cockpit-label">{_escape(t('exec_residual_simulation_title', language, 'Residual risk simulation'))}</span>
                <span class="aiwra-cockpit-value" style="color:{simulation_color};">△ {_escape(simulation_text)}</span>
                <span class="aiwra-cockpit-note">{_escape(t('cockpit_simulation_note', language, 'Selected controls remain assumptions'))}</span>
            </div>
        </div>
        """
    )


def render_simulation_comparison(simulation: dict[str, Any], language: str = "en") -> None:
    raw = simulation.get("raw_risk", {}) if isinstance(simulation.get("raw_risk"), dict) else {}
    residual = simulation.get("residual_risk", {}) if isinstance(simulation.get("residual_risk"), dict) else {}
    raw_style = severity_token(raw.get("severity", "unknown"), language)
    residual_style = severity_token(residual.get("severity", "unknown"), language)
    selected_controls = simulation.get("selected_controls", [])
    remaining = simulation.get("remaining_risks", [])
    render_html(
        f"""
        <div class="aiwra-simulation-shell" aria-label="{_escape(t('simulation_cockpit_title', language, 'Residual-risk simulation cockpit'))}">
            <div class="aiwra-simulation-grid">
                <div class="aiwra-score-panel" style="--score-color:{raw_style['color']};">
                    <span class="aiwra-cockpit-label">{_escape(t('simulation_before_label', language, 'Before controls'))}</span>
                    <strong>{_escape(raw.get('score', 0))}</strong>
                    <span>{_escape(raw_style['label'])}</span>
                </div>
                <div class="aiwra-simulation-arrow" aria-hidden="true">→</div>
                <div class="aiwra-score-panel" style="--score-color:{residual_style['color']};">
                    <span class="aiwra-cockpit-label">{_escape(t('simulation_after_label', language, 'Hypothetical after'))}</span>
                    <strong>{_escape(residual.get('score', 0))}</strong>
                    <span>{_escape(residual_style['label'])}</span>
                </div>
                <div class="aiwra-score-panel" style="--score-color:var(--aiwra-simulated);">
                    <span class="aiwra-cockpit-label">{_escape(t('reduction_metric', language, 'Reduction'))}</span>
                    <strong>−{_escape(simulation.get('score_reduction', 0))}</strong>
                    <span>{_escape(len(selected_controls))} {_escape(t('selected_controls_unit', language, 'selected control(s)'))} · {_escape(len(remaining))} {_escape(t('remaining_factors_unit', language, 'remaining factor(s)'))}</span>
                </div>
            </div>
            <div class="aiwra-assumption-banner">△ {_escape(t('simulation_assumptions_not_proof', language, 'Selected controls are assumptions, not proof. Verify evidence and implementation before relying on this result.'))}</div>
        </div>
        """
    )


def render_local_ai_brain_panel(
    available: bool,
    endpoint: str,
    local_model_count: int,
    blocked_model_count: int,
    language: str = "en",
) -> None:
    availability = t("available_label", language, "Available") if available else t("not_available_label", language, "Not available")
    availability_color = "var(--aiwra-low)" if available else "var(--aiwra-uncertain)"
    render_html(
        f"""
        <div class="aiwra-ai-brain" aria-label="{_escape(t('local_ai_brain_title', language, 'Controlled local AI reviewer module'))}">
            <div class="aiwra-ai-brain-head">
                <div>
                    <span class="aiwra-cockpit-label">{_escape(t('local_ai_module_label', language, 'Optional reviewer brain'))}</span>
                    <div class="aiwra-ai-brain-title">{_escape(t('local_ai_brain_title', language, 'Controlled local AI reviewer module'))}</div>
                </div>
                <span class="aiwra-badge" style="color:{availability_color}; background:var(--aiwra-surface-alt); border-color:{availability_color};">
                    <i class="aiwra-status-dot"></i>{_escape(availability)}
                </span>
            </div>
            <div class="aiwra-ai-boundaries">
                <div class="aiwra-ai-boundary">
                    <strong>01 · {_escape(t('local_ai_authority_title', language, 'Engine authority'))}</strong>
                    <span>{_escape(t('local_ai_authority_body', language, 'Deterministic findings and score remain the source of truth.'))}</span>
                </div>
                <div class="aiwra-ai-boundary">
                    <strong>02 · {_escape(t('local_ai_boundary_title', language, 'Network boundary'))}</strong>
                    <span><bdi class="aiwra-technical">{_escape(endpoint)} · 127.0.0.1</bdi> · {_escape(t('local_ai_cloud_block_short', language, 'cloud and proxy models blocked'))}</span>
                </div>
                <div class="aiwra-ai-boundary">
                    <strong>03 · {_escape(t('local_ai_capability_title', language, 'Allowed role'))}</strong>
                    <span>{_escape(t('local_ai_capability_body', language, 'Draft explanations, missing-context prompts, and reviewer questions.'))}</span>
                </div>
                <div class="aiwra-ai-boundary">
                    <strong>04 · {_escape(t('local_ai_inventory_title', language, 'Local inventory'))}</strong>
                    <span>{_escape(local_model_count)} {_escape(t('model_unit', language, 'model(s)'))} · {_escape(blocked_model_count)} {_escape(t('blocked_model_unit', language, 'blocked model(s)'))}</span>
                </div>
            </div>
        </div>
        """
    )


def render_info_card(title: str, body: str, status: str | None = None, language: str = "en") -> None:
    badge = ""
    if status:
        token = status_token(status, language)
        badge = (
            f"<span class='aiwra-badge' style='color:{token['color']}; "
            f"background:{token['background']}; border-color:{token['border']};'>"
            f"{_escape(t('status_label', language, 'Status'))}: {_escape(token['label'])}</span>"
        )
    render_html(
        f"""
        <div class="aiwra-card">
            <div class="aiwra-card-title">{_escape(title)}</div>
            {badge}
            <p>{_escape(body)}</p>
        </div>
        """
    )


def render_section_header(title: str, subtitle: str = "", status: str | None = None, language: str = "en") -> None:
    badge = ""
    if status:
        token = status_token(status, language)
        badge = (
            f"<span class='aiwra-badge' style='color:{token['color']}; "
            f"background:{token['background']}; border-color:{token['border']};'>"
            f"{_escape(token['label'])}</span>"
        )
    render_html(
        f"""
        <div class="aiwra-section">
            <div class="aiwra-section-title">{_escape(title)} {badge}</div>
            <p class="aiwra-muted">{_escape(subtitle)}</p>
        </div>
        """
    )


def render_legend(items: list[tuple[str, str]], title: str | None = None) -> None:
    if title:
        st.caption(title)
    if not items:
        return
    lines = "".join(f"<li><strong>{_escape(label)}</strong>: {_escape(body)}</li>" for label, body in items)
    render_html(f"<ul>{lines}</ul>")


def render_empty_state(title: str, body: str, action: str = "") -> None:
    action_html = f"<p><strong>{_escape(action)}</strong></p>" if action else ""
    render_html(
        f"""
        <div class="aiwra-card">
            <div class="aiwra-card-title">{_escape(title)}</div>
            <p>{_escape(body)}</p>
            {action_html}
        </div>
        """
    )


def build_heatmap_cells(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str]] = Counter()
    categories: set[str] = set()
    for finding in findings:
        category = str(finding.get("category") or "unknown")
        severity = str(finding.get("severity") or "unknown").casefold()
        severity = severity if severity in SEVERITY_ORDER else "unknown"
        categories.add(category)
        counts[(category, severity)] += int(finding.get("count") or 1)

    cells: list[dict[str, Any]] = []
    for category in sorted(categories):
        for severity in SEVERITY_ORDER:
            count = counts[(category, severity)]
            cells.append({"category": category, "severity": severity, "count": count})
    return cells


def render_heatmap(findings: list[dict[str, Any]], language: str = "en") -> None:
    cells = build_heatmap_cells(findings)
    if not cells:
        render_empty_state(
            t("heatmap_empty_title", language, "No heatmap data yet"),
            t("heatmap_empty_body", language, "Run or save an audit with detected findings to populate this text-first heatmap."),
        )
        return
    grouped: dict[str, dict[str, int]] = defaultdict(dict)
    for cell in cells:
        grouped[cell["category"]][cell["severity"]] = int(cell["count"])

    headers = [t("category_label", language, "Category")] + [
        severity_token(severity, language)["label"] for severity in SEVERITY_ORDER
    ]
    header_columns = st.columns([1.4, 1, 1, 1, 1])
    for column, header in zip(header_columns, headers):
        column.markdown(f"**{header}**")

    for category, severity_counts in grouped.items():
        row_columns = st.columns([1.4, 1, 1, 1, 1])
        row_columns[0].markdown(f"**{translate_category(category, language)}**")
        for column, severity in zip(row_columns[1:], SEVERITY_ORDER):
            token = severity_token(severity, language)
            count = int(severity_counts.get(severity, 0))
            text = t("heatmap_cell_text", language, "{count} finding(s)").format(count=count)
            column.metric(token["label"], count, help=f"{text}. {token['description']}")


def build_matrix_cells(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[tuple[int, int], dict[str, Any]] = {}
    for entry in entries:
        impact = int(entry.get("impact") or 0)
        likelihood = int(entry.get("likelihood") or 0)
        if impact <= 0 or likelihood <= 0:
            continue
        score = impact * likelihood
        if score >= 20:
            severity = "critical"
        elif score >= 12:
            severity = "high"
        elif score >= 6:
            severity = "medium"
        else:
            severity = "low"
        key = (impact, likelihood)
        current = buckets.setdefault(
            key,
            {
                "impact": impact,
                "likelihood": likelihood,
                "count": 0,
                "severity": severity,
                "factors": [],
            },
        )
        current["count"] += 1
        current["factors"].append(str(entry.get("factor") or "unknown"))
        if SEVERITY_ORDER.index(severity) < SEVERITY_ORDER.index(str(current["severity"])):
            current["severity"] = severity
    return sorted(buckets.values(), key=lambda item: (item["impact"], item["likelihood"]), reverse=True)


def render_risk_matrix(entries: list[dict[str, Any]], language: str = "en") -> None:
    cells = build_matrix_cells(entries)
    if not cells:
        render_empty_state(
            t("matrix_empty_title", language, "No matrix entries yet"),
            t("matrix_empty_body", language, "The matrix appears after evidence is mapped to local impact and likelihood attributes."),
        )
        return
    for cell in cells[:9]:
        token = severity_token(cell["severity"], language)
        factors = ", ".join(t(f"factor_{factor}", language, humanize_key(factor)) for factor in cell["factors"][:3])
        render_html(
            f"""
            <div class="aiwra-card" style="border-color:{token['border']}; background:{token['background']};">
                <strong>{_escape(t('matrix_cell_title', language, 'Impact {impact} x likelihood {likelihood}').format(impact=cell['impact'], likelihood=cell['likelihood']))}</strong>
                <p>{_escape(t('matrix_cell_count', language, '{count} mapped factor(s)').format(count=cell['count']))}</p>
                <p>{_escape(t('severity_label', language, 'Severity'))}: {_escape(token['label'])}</p>
                <p>{_escape(t('matrix_cell_factors', language, 'Factors'))}: {_escape(factors)}</p>
                <p>{_escape(t('matrix_cell_limit', language, 'Indicative matrix derived from local evidence counts and rule weights.'))}</p>
            </div>
            """
        )


def render_workflow_graph(language: str = "en") -> None:
    steps = [
        ("workflow_graph_input", "Input workflow"),
        ("workflow_graph_parser", "Local parser"),
        ("workflow_graph_evidence", "Evidence engine"),
        ("workflow_graph_scoring", "Risk scoring"),
        ("workflow_graph_controls", "Recommended controls"),
        ("workflow_graph_report", "Report export"),
        ("workflow_graph_ai", "Optional local AI narrative"),
    ]
    html_steps = ""
    for index, (key, fallback) in enumerate(steps, start=1):
        html_steps += (
            "<div class='aiwra-flow-step'>"
            f"<strong>{index}. {_escape(t(key, language, fallback))}</strong>"
            f"<small>{_escape(t(f'{key}_help', language, 'Local deterministic pipeline step.'))}</small>"
            "</div>"
        )
    render_html(f"<div class='aiwra-flow'>{html_steps}</div>")
    st.caption(
        t(
            "workflow_graph_required_note",
            language,
            "This graph shows how the local deterministic audit pipeline interprets the workflow. It is not a live production integration map.",
        )
    )


def render_evidence_card(finding: dict[str, Any], index: int, language: str = "en") -> None:
    severity = str(finding.get("severity", "unknown"))
    token = severity_token(severity, language)
    category = t(f"kb_category_{finding.get('category')}", language, humanize_key(finding.get("category")))
    controls = finding.get("recommended_controls", [])
    controls_text = ", ".join(str(item) for item in controls[:3]) if isinstance(controls, list) else str(controls)
    evidence = finding.get("matched_text_evidence", "")
    rule_id = finding.get("matched_rule_id", "")
    confidence = finding.get("confidence", "")
    impact = finding.get("score_impact", 0)
    why = finding.get("why_it_matters", "")
    question = finding.get("human_review_question", "")
    assumption = finding.get("residual_simulation_assumption", "")
    limitation = finding.get("limitation", "") or t(
        "evidence_card_limit",
        language,
        "This finding is detected from local text evidence and needs human review before action.",
    )
    render_html(
        f"""
        <div class="aiwra-card aiwra-finding-card" style="--finding-color:{token['color']}; border-color:{token['border']};">
            <div class="aiwra-finding-head">
                <div class="aiwra-finding-title">{index}. {_escape(category)}</div>
                <div>
                    <span class="aiwra-badge" style="color:{token['color']}; background:{token['background']}; border-color:{token['border']};">
                        ◆ {_escape(t('severity_label', language, 'Severity'))}: {_escape(token['label'])}
                    </span>
                    <span class="aiwra-badge" style="color:var(--aiwra-calculated); background:var(--aiwra-calculated-soft); border-color:var(--aiwra-calculated-border);">
                        {_escape(t('score_impact_label', language, 'Score impact'))}: +{_escape(impact)}
                    </span>
                </div>
            </div>
            <div class="aiwra-evidence-quote"><strong>{_escape(t('evidence_label', language, 'Evidence'))}:</strong> “{_escape(evidence)}”</div>
            <div class="aiwra-detail-grid">
                <div class="aiwra-detail"><strong>{_escape(t('rule_used_label', language, 'Rule used'))}</strong><span><bdi class="aiwra-technical">{_escape(rule_id)}</bdi></span></div>
                <div class="aiwra-detail"><strong>{_escape(t('confidence_label', language, 'Confidence'))}</strong><span>{_escape(confidence)}</span></div>
                <div class="aiwra-detail"><strong>{_escape(t('why_it_matters_label', language, 'Why it matters'))}</strong><span>{_escape(why)}</span></div>
                <div class="aiwra-detail"><strong>{_escape(t('recommended_action_label', language, 'Recommended action'))}</strong><span>{_escape(controls_text or t('none_detected', language, 'None detected.'))}</span></div>
                <div class="aiwra-detail"><strong>{_escape(t('human_review_question_label', language, 'Human review question'))}</strong><span>{_escape(question)}</span></div>
                <div class="aiwra-detail"><strong>{_escape(t('simulation_assumption_label', language, 'Residual simulation assumption'))}</strong><span>{_escape(assumption)}</span></div>
                <div class="aiwra-detail"><strong>{_escape(t('finding_specific_limit_label', language, 'Finding limitation'))}</strong><span>{_escape(limitation)}</span></div>
            </div>
        </div>
        """
    )


def render_control_card(control: dict[str, Any], index: int, language: str = "en") -> None:
    status = status_token("recommended", language)
    control_id = control.get("id", "")
    category = translate_category(control.get("category"), language)
    effectiveness = control.get("effectiveness", "")
    risk_factors = control.get("risk_factors", [])
    factors_text = ", ".join(str(item) for item in risk_factors[:4]) if isinstance(risk_factors, list) else str(risk_factors)
    render_html(
        f"""
        <div class="aiwra-card aiwra-control-card" aria-label="{_escape(t('control_card_title', language, 'Recommended control'))}">
            <div class="aiwra-finding-head">
                <div class="aiwra-finding-title">{index}. {_escape(control.get('name', t('control_card_title', language, 'Recommended control')))}</div>
                <span class="aiwra-badge" style="color:{status['color']}; background:{status['background']}; border-color:{status['border']};">
                    {_escape(t('checklist_status_recommended_not_verified', language, 'Recommended - not verified'))}
                </span>
            </div>
            <p>{_escape(control.get('description', ''))}</p>
            <div class="aiwra-control-meta">
                <div class="aiwra-detail"><strong>{_escape(t('column_rule_id', language, 'Rule ID'))}</strong><span><bdi class="aiwra-technical">{_escape(control_id)}</bdi></span></div>
                <div class="aiwra-detail"><strong>{_escape(t('category_label', language, 'Category'))}</strong><span>{_escape(category)}</span></div>
                <div class="aiwra-detail"><strong>{_escape(t('reduction_metric', language, 'Reduction'))}</strong><span>{_escape(effectiveness)} {_escape(t('score_point_unit', language, 'score point(s)'))}</span></div>
                <div class="aiwra-detail"><strong>{_escape(t('why_recommended_label', language, 'Why recommended'))}</strong><span>{_escape(control.get('reason', ''))}</span></div>
                <div class="aiwra-detail"><strong>{_escape(t('implementation_check_label', language, 'Implementation check'))}</strong><span>{_escape(control.get('implementation_guidance', ''))}</span></div>
                <div class="aiwra-detail"><strong>{_escape(t('mapped_risk_factors_label', language, 'Mapped risk factors'))}</strong><span><bdi class="aiwra-technical">{_escape(factors_text)}</bdi></span></div>
            </div>
            <p class="aiwra-muted"><strong>{_escape(t('limit_label', language, 'Limit'))}:</strong> {_escape(t('control_card_limit', language, 'This is a recommended control, not evidence that the control is implemented.'))}</p>
        </div>
        """
    )


def render_issue_card(issue: dict[str, Any], language: str = "en") -> None:
    severity = severity_token(issue.get("severity", "unknown"), language)
    status = status_token(issue.get("status", "recommended"), language)
    human_review = issue.get("human_review", True)
    human_review_label = (
        t("yes_label", language, "Yes")
        if human_review is True or str(human_review).casefold() == "yes"
        else str(human_review)
    )
    render_html(
        f"""
        <div class="aiwra-card">
            <div class="aiwra-card-title">{_escape(issue.get('title', t('issue_title_fallback', language, 'Local follow-up item')))}</div>
            <span class="aiwra-badge" style="color:{severity['color']}; background:{severity['background']}; border-color:{severity['border']};">
                {_escape(t('severity_label', language, 'Severity'))}: {_escape(severity['label'])}
            </span>
            <span class="aiwra-badge" style="color:{status['color']}; background:{status['background']}; border-color:{status['border']};">
                {_escape(t('status_label', language, 'Status'))}: {_escape(status['label'])}
            </span>
            <p><strong>{_escape(t('evidence_label', language, 'Evidence'))}:</strong> {_escape(issue.get('evidence', ''))}</p>
            <p><strong>{_escape(t('recommended_action_label', language, 'Recommended action'))}:</strong> {_escape(issue.get('control', ''))}</p>
            <p><strong>{_escape(t('human_review_required_label', language, 'Human review required'))}:</strong> {_escape(human_review_label)}</p>
        </div>
        """
    )


def render_timeline(events: list[dict[str, Any]], language: str = "en") -> None:
    if not events:
        render_empty_state(
            t("timeline_empty_title", language, "No local audit timeline yet"),
            t("timeline_empty_body", language, "Save an audit report locally to populate the audit timeline."),
        )
        return
    for event in events[:8]:
        render_html(
            f"""
            <div class="aiwra-timeline-item">
                <strong>{_escape(event.get('created_at', ''))}</strong><br>
                {_escape(t('timeline_event_label', language, 'Event'))}: {_escape(humanize_key(event.get('event_type')))}
                <br><span class="aiwra-muted">{_escape(event.get('entity_type', ''))} #{_escape(event.get('entity_id', ''))}</span>
            </div>
            """
        )


def render_ai_output_panel(
    prompt: str,
    response: str | None,
    deterministic_summary: str,
    language: str = "en",
) -> None:
    render_info_card(
        t("local_ai_comparison_title", language, "Deterministic report vs local AI narrative"),
        deterministic_summary,
        status="calculated",
        language=language,
    )
    st.markdown(f"**{t('local_ai_prompt_sent', language, 'Prompt sent')}**")
    st.code(prompt or t("local_ai_no_prompt", language, "No prompt generated."), language="text")
    st.markdown(f"**{t('local_ai_exact_response', language, 'Exact local AI response')}**")
    if response:
        st.code(response, language="text")
    else:
        render_empty_state(
            t("local_ai_no_response_title", language, "No local AI response"),
            t("local_ai_no_response_body", language, "Ollama may be unavailable, no local model may be installed, or the request was not run."),
        )


def render_accessibility_note(language: str = "en") -> None:
    render_info_card(
        t("accessibility_note_title", language, "Accessibility note"),
        t(
            "accessibility_note_body",
            language,
            "Colors are only a secondary signal. Badges, heatmap cells, and matrix cells include text labels, counts, source, meaning, and limits.",
        ),
        status="local_only",
        language=language,
    )


def render_how_to_read_panel(language: str, body_key: str, fallback: str) -> None:
    render_info_card(t("how_to_read_title", language, "How to read this page"), t(body_key, language, fallback), "local_only", language)


def render_read_only_notice(language: str = "en") -> None:
    render_info_card(
        t("kb_read_only_title", language, "Read-only local rule library"),
        t(
            "kb_read_only_body",
            language,
            "This Knowledge Base is loaded from local JSON files and seeded into local SQLite. It is not a cloud database and this screen does not edit rules.",
        ),
        "read_only",
        language,
    )
