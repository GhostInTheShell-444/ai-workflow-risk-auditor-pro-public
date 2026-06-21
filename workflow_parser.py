from __future__ import annotations

import re
import unicodedata


FRENCH_HINTS = (
    "données",
    "candidat",
    "présélection",
    "validation humaine",
    "alerte sécurité",
    "livraison",
    "tournée",
)


def clean_workflow_text(text: str | None) -> str:
    if text is None:
        return ""
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def normalize_for_match(text: str) -> str:
    text = text.casefold().replace("’", "'").replace("״", '"')
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def extract_workflow_steps(text: str | None, max_steps: int = 16) -> list[str]:
    cleaned = clean_workflow_text(text)
    if not cleaned:
        return []

    chunks = re.split(r"\n+|(?<=[.!?])\s+", cleaned)
    steps: list[str] = []
    for chunk in chunks:
        chunk = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", chunk).strip(" -\t")
        if len(chunk) >= 8:
            steps.append(chunk)

    if len(steps) < 2:
        steps = [
            part.strip(" -\t")
            for part in re.split(r"\s+(?:then|and then|after that|puis|ensuite)\s+|;", cleaned, flags=re.I)
            if len(part.strip()) >= 8
        ]

    return steps[:max_steps] or ["Review the submitted workflow text."]


def detect_language(text: str | None) -> str:
    cleaned = clean_workflow_text(text)
    if not cleaned:
        return "unknown"
    if re.search(r"[\u0590-\u05FF]", cleaned):
        return "he"
    if re.search(r"[éèêàùçœ]", cleaned.casefold()):
        return "fr"
    normalized = normalize_for_match(cleaned)
    french_hits = 0
    for hint in FRENCH_HINTS:
        normalized_hint = normalize_for_match(hint)
        pattern = r"(?<!\w)" + re.escape(normalized_hint) + r"(?!\w)"
        if re.search(pattern, normalized):
            french_hits += 1
    if french_hits >= 2:
        return "fr"
    return "en"
