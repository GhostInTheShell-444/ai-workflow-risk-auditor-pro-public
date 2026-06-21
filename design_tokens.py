from __future__ import annotations

from typing import Any

from i18n import t


FONT_STACK = 'Lato, Inter, "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif'

THEME_OPTIONS = ("light", "dark", "system")

REQUIRED_THEME_KEYS = {
    "bg",
    "surface",
    "surface_alt",
    "text",
    "muted",
    "border",
    "shadow",
    "primary",
    "primary_soft",
    "critical",
    "high",
    "medium",
    "low",
}

THEMES: dict[str, dict[str, str]] = {
    "light": {
        "bg": "#F6F8FB",
        "surface": "#FFFFFF",
        "surface_alt": "#F1F5F9",
        "text": "#0F172A",
        "muted": "#64748B",
        "border": "#CBD5E1",
        "shadow": "rgba(15, 23, 42, 0.08)",
        "primary": "#2563EB",
        "primary_soft": "#DBEAFE",
        "critical": "#DC2626",
        "high": "#EA580C",
        "medium": "#D97706",
        "low": "#16A34A",
        "critical_soft": "#FEF2F2",
        "high_soft": "#FFF7ED",
        "medium_soft": "#FFFBEB",
        "low_soft": "#ECFDF5",
        "critical_border": "#FCA5A5",
        "high_border": "#FDBA74",
        "medium_border": "#FCD34D",
        "low_border": "#A7F3D0",
        "calculated": "#6D28D9",
        "calculated_soft": "#F5F3FF",
        "calculated_border": "#DDD6FE",
        "uncertain": "#64748B",
        "uncertain_soft": "#F8FAFC",
        "uncertain_border": "#CBD5E1",
    },
    "dark": {
        "bg": "#0B1120",
        "surface": "#111827",
        "surface_alt": "#1E293B",
        "text": "#E5E7EB",
        "muted": "#94A3B8",
        "border": "#334155",
        "shadow": "rgba(0, 0, 0, 0.35)",
        "primary": "#60A5FA",
        "primary_soft": "#1E3A8A",
        "critical": "#F87171",
        "high": "#FB923C",
        "medium": "#FBBF24",
        "low": "#4ADE80",
        "critical_soft": "rgba(248, 113, 113, 0.16)",
        "high_soft": "rgba(251, 146, 60, 0.16)",
        "medium_soft": "rgba(251, 191, 36, 0.16)",
        "low_soft": "rgba(74, 222, 128, 0.16)",
        "critical_border": "rgba(248, 113, 113, 0.46)",
        "high_border": "rgba(251, 146, 60, 0.46)",
        "medium_border": "rgba(251, 191, 36, 0.46)",
        "low_border": "rgba(74, 222, 128, 0.46)",
        "calculated": "#C084FC",
        "calculated_soft": "rgba(192, 132, 252, 0.16)",
        "calculated_border": "rgba(192, 132, 252, 0.44)",
        "uncertain": "#CBD5E1",
        "uncertain_soft": "rgba(148, 163, 184, 0.14)",
        "uncertain_border": "rgba(148, 163, 184, 0.40)",
    },
}
THEMES["system"] = dict(THEMES["light"])

COLORS: dict[str, str] = {
    "surface": "var(--aiwra-surface)",
    "surface_soft": "var(--aiwra-surface-alt)",
    "surface_muted": "var(--aiwra-surface-alt)",
    "border": "var(--aiwra-border)",
    "border_soft": "var(--aiwra-border)",
    "text": "var(--aiwra-text)",
    "muted": "var(--aiwra-muted)",
    "blue": "var(--aiwra-primary)",
    "blue_soft": "var(--aiwra-primary-soft)",
    "green": "var(--aiwra-low)",
    "green_soft": "var(--aiwra-low-soft)",
    "amber": "var(--aiwra-medium)",
    "amber_soft": "var(--aiwra-medium-soft)",
    "red": "var(--aiwra-critical)",
    "red_soft": "var(--aiwra-critical-soft)",
    "purple": "var(--aiwra-calculated)",
    "purple_soft": "var(--aiwra-calculated-soft)",
    "gray": "var(--aiwra-uncertain)",
    "gray_soft": "var(--aiwra-uncertain-soft)",
}


SEVERITY_TOKENS: dict[str, dict[str, str]] = {
    "low": {
        "label_key": "risk_level_low",
        "description_key": "severity_low_description",
        "color": COLORS["green"],
        "background": COLORS["green_soft"],
        "border": "var(--aiwra-low-border)",
    },
    "medium": {
        "label_key": "risk_level_medium",
        "description_key": "severity_medium_description",
        "color": COLORS["amber"],
        "background": COLORS["amber_soft"],
        "border": "var(--aiwra-medium-border)",
    },
    "high": {
        "label_key": "risk_level_high",
        "description_key": "severity_high_description",
        "color": "var(--aiwra-high)",
        "background": "var(--aiwra-high-soft)",
        "border": "var(--aiwra-high-border)",
    },
    "critical": {
        "label_key": "risk_level_critical",
        "description_key": "severity_critical_description",
        "color": COLORS["red"],
        "background": COLORS["red_soft"],
        "border": "var(--aiwra-critical-border)",
    },
    "unknown": {
        "label_key": "risk_level_unknown",
        "description_key": "severity_unknown_description",
        "color": COLORS["gray"],
        "background": COLORS["gray_soft"],
        "border": "var(--aiwra-uncertain-border)",
    },
}


STATUS_TOKENS: dict[str, dict[str, str]] = {
    "detected": {
        "label_key": "status_detected_label",
        "description_key": "status_detected_description",
        "color": COLORS["blue"],
        "background": COLORS["blue_soft"],
        "border": "var(--aiwra-primary)",
    },
    "calculated": {
        "label_key": "status_calculated_label",
        "description_key": "status_calculated_description",
        "color": COLORS["purple"],
        "background": COLORS["purple_soft"],
        "border": "var(--aiwra-calculated-border)",
    },
    "simulated": {
        "label_key": "status_simulated_label",
        "description_key": "status_simulated_description",
        "color": COLORS["amber"],
        "background": COLORS["amber_soft"],
        "border": "var(--aiwra-medium-border)",
    },
    "recommended": {
        "label_key": "status_recommended_label",
        "description_key": "status_recommended_description",
        "color": COLORS["green"],
        "background": COLORS["green_soft"],
        "border": "var(--aiwra-low-border)",
    },
    "uncertain": {
        "label_key": "status_uncertain_label",
        "description_key": "status_uncertain_description",
        "color": COLORS["gray"],
        "background": COLORS["gray_soft"],
        "border": "var(--aiwra-uncertain-border)",
    },
    "needs_human_review": {
        "label_key": "status_needs_human_review_label",
        "description_key": "status_needs_human_review_description",
        "color": COLORS["amber"],
        "background": COLORS["amber_soft"],
        "border": "var(--aiwra-medium-border)",
    },
    "read_only": {
        "label_key": "status_read_only_label",
        "description_key": "status_read_only_description",
        "color": COLORS["gray"],
        "background": COLORS["gray_soft"],
        "border": "var(--aiwra-uncertain-border)",
    },
    "demo": {
        "label_key": "status_demo_label",
        "description_key": "status_demo_description",
        "color": COLORS["blue"],
        "background": COLORS["blue_soft"],
        "border": "var(--aiwra-primary)",
    },
    "local_only": {
        "label_key": "status_local_only_label",
        "description_key": "status_local_only_description",
        "color": COLORS["green"],
        "background": COLORS["green_soft"],
        "border": "var(--aiwra-low-border)",
    },
    "not_available": {
        "label_key": "status_not_available_label",
        "description_key": "status_not_available_description",
        "color": COLORS["gray"],
        "background": COLORS["gray_soft"],
        "border": "var(--aiwra-uncertain-border)",
    },
}


def normalize_severity(severity: object) -> str:
    key = str(severity or "unknown").casefold().strip()
    return key if key in SEVERITY_TOKENS else "unknown"


def normalize_status(status: object) -> str:
    key = str(status or "uncertain").casefold().strip().replace("-", "_").replace(" ", "_")
    return key if key in STATUS_TOKENS else "uncertain"


def normalize_theme(theme: object) -> str:
    key = str(theme or "system").casefold().strip()
    return key if key in THEME_OPTIONS else "system"


def resolved_theme(theme: object) -> str:
    key = normalize_theme(theme)
    return "light" if key == "system" else key


def theme_tokens(theme: object = "light") -> dict[str, str]:
    return THEMES[resolved_theme(theme)].copy()


def theme_label(theme: object, language: str = "en") -> str:
    key = normalize_theme(theme)
    return t(f"theme_{key}", language, key.title())


def severity_token(severity: object, language: str = "en") -> dict[str, Any]:
    key = normalize_severity(severity)
    token = dict(SEVERITY_TOKENS[key])
    token.update(
        {
            "key": key,
            "label": t(token["label_key"], language, key.title()),
            "description": t(token["description_key"], language, ""),
        }
    )
    return token


def status_token(status: object, language: str = "en") -> dict[str, Any]:
    key = normalize_status(status)
    token = dict(STATUS_TOKENS[key])
    token.update(
        {
            "key": key,
            "label": t(token["label_key"], language, key.replace("_", " ").title()),
            "description": t(token["description_key"], language, ""),
        }
    )
    return token


def color_css_variables(theme: object = "light") -> str:
    tokens = theme_tokens(theme)
    aliases = {
        "surface-soft": tokens["surface_alt"],
        "surface-muted": tokens["surface_alt"],
        "border-soft": tokens["border"],
        "blue": tokens["primary"],
        "blue-soft": tokens["primary_soft"],
        "green": tokens["low"],
        "green-soft": tokens["low_soft"],
        "amber": tokens["medium"],
        "amber-soft": tokens["medium_soft"],
        "red": tokens["critical"],
        "red-soft": tokens["critical_soft"],
        "purple": tokens["calculated"],
        "purple-soft": tokens["calculated_soft"],
        "gray": tokens["uncertain"],
        "gray-soft": tokens["uncertain_soft"],
    }
    variables = [f"--aiwra-{name.replace('_', '-')}: {value};" for name, value in tokens.items()]
    variables.extend(f"--aiwra-{name}: {value};" for name, value in aliases.items())
    return "\n".join(variables)
