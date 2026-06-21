from __future__ import annotations

import hashlib
import re
from typing import Any

from knowledge_loader import load_risk_patterns
from workflow_parser import detect_language, extract_workflow_steps, normalize_for_match


ACTION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "external_communication": ("email", "e-mail", "reply", "send", "notify", "notification", "réponse", "client"),
    "human_validation": ("approval", "review", "validation humaine", "approbation", "revue humaine", "validated"),
    "decision": ("decision", "ranking", "shortlist", "présélection", "décision", "candidate", "candidat"),
    "modification": ("modify", "update", "delete", "suppression", "close", "change", "route", "tournée"),
    "security_response": ("soc", "alert", "incident", "escalation", "escalade", "blocage", "blocking"),
}


def _stable_finding_id(rule_id: str, step_index: int, evidence: str) -> str:
    digest = hashlib.sha1(f"{rule_id}|{step_index}|{evidence}".encode("utf-8")).hexdigest()[:12]
    return f"finding_{digest}"


def _severity_confidence(severity: str, regex_match: bool, action_matches: int) -> float:
    base = {"low": 0.62, "medium": 0.72, "high": 0.8, "critical": 0.86}.get(severity, 0.7)
    if regex_match:
        base += 0.08
    base += min(action_matches, 2) * 0.03
    return round(min(base, 0.95), 2)


def classify_step_actions(step_text: str) -> list[str]:
    normalized = normalize_for_match(step_text)
    actions = []
    for action, keywords in ACTION_KEYWORDS.items():
        if any(normalize_for_match(keyword) in normalized for keyword in keywords):
            actions.append(action)
    return actions


def _keyword_evidence(step_text: str, keywords: list[str]) -> str | None:
    normalized_step = normalize_for_match(step_text)
    for keyword in keywords:
        normalized_keyword = normalize_for_match(str(keyword))
        if normalized_keyword and normalized_keyword in normalized_step:
            match = re.search(re.escape(str(keyword)), step_text, flags=re.IGNORECASE)
            if match:
                start = max(match.start() - 45, 0)
                end = min(match.end() + 45, len(step_text))
                return step_text[start:end].strip()
            return str(keyword)
    return None


def _regex_evidence(step_text: str, regex_pattern: str | None) -> str | None:
    if not regex_pattern:
        return None
    try:
        match = re.search(regex_pattern, step_text[:10000])
    except re.error:
        return None
    if not match:
        return None
    start = max(match.start() - 35, 0)
    end = min(match.end() + 35, len(step_text))
    return step_text[start:end].strip()


def find_evidence_for_pattern(step_text: str, pattern: dict[str, Any]) -> tuple[str | None, bool]:
    regex_evidence = _regex_evidence(step_text, pattern.get("regex_pattern"))
    if regex_evidence:
        return regex_evidence, True
    keywords = pattern.get("keywords", [])
    keyword_evidence = _keyword_evidence(step_text, [str(item) for item in keywords if str(item).strip()])
    return keyword_evidence, False


def run_evidence_engine(text: str | None, language: str | None = None) -> dict[str, Any]:
    steps = extract_workflow_steps(text)
    detected_language = language or detect_language(text)
    findings: list[dict[str, Any]] = []

    for step_index, step in enumerate(steps, start=1):
        actions = classify_step_actions(step)
        for pattern in load_risk_patterns():
            evidence, used_regex = find_evidence_for_pattern(step, pattern)
            if not evidence:
                continue
            severity = str(pattern.get("severity", "medium"))
            controls = [str(item) for item in pattern.get("recommended_control_ids", [])]
            factors = [str(item) for item in pattern.get("risk_factor_mapping", [])]
            finding = {
                "finding_id": _stable_finding_id(str(pattern["id"]), step_index, evidence),
                "category": str(pattern.get("category", "general")),
                "severity": severity,
                "confidence": _severity_confidence(severity, used_regex, len(actions)),
                "matched_text_evidence": evidence,
                "matched_rule_id": str(pattern["id"]),
                "workflow_step_reference": f"step_{step_index}",
                "workflow_step_text": step,
                "explanation": str(pattern.get("explanation", "")),
                "recommended_controls": controls,
                "risk_factor_mapping": factors,
                "language_detected_when_possible": detected_language,
                "action_classification": actions,
            }
            findings.append(finding)

    # Deterministic de-duplication preserves first evidence for the same rule on the same step.
    seen: set[tuple[str, str]] = set()
    unique_findings: list[dict[str, Any]] = []
    for finding in findings:
        key = (str(finding["matched_rule_id"]), str(finding["workflow_step_reference"]))
        if key in seen:
            continue
        seen.add(key)
        unique_findings.append(finding)

    return {
        "steps": steps,
        "language_detected": detected_language,
        "findings": unique_findings,
    }
