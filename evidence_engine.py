from __future__ import annotations

import hashlib
import re
from typing import Any

from knowledge_loader import load_risk_patterns
from risk_rules import RISK_FACTORS
from workflow_parser import detect_language, extract_workflow_steps, normalize_for_match


ACTION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "external_communication": ("email", "e-mail", "reply", "send", "notify", "notification", "réponse", "client"),
    "human_validation": ("approval", "review", "validation humaine", "approbation", "revue humaine", "validated"),
    "decision": ("decision", "ranking", "shortlist", "présélection", "décision", "candidate", "candidat"),
    "modification": ("modify", "update", "delete", "suppression", "close", "change", "route", "tournée"),
    "security_response": ("soc", "alert", "incident", "escalation", "escalade", "blocage", "blocking"),
    "financial_action": ("refund", "payment", "billing", "chargeback", "remboursement", "invoice"),
    "tool_action": ("tool", "api", "webhook", "function call", "execute action", "agent"),
}

CONTROL_GAP_TERMS: dict[str, tuple[str, ...]] = {
    "human_review": ("human review", "approval", "manual review", "validation humaine", "approbation", "אישור אנושי"),
    "audit_trail": ("audit log", "audit trail", "record of decision", "logging", "journal d'audit", "יומן ביקורת"),
    "reviewer_identity": ("named reviewer", "named human reviewer", "assigned reviewer", "responsible reviewer", "process owner", "approver id"),
    "retention": ("retention", "delete after", "archive policy", "purge", "conservation"),
    "appeal": ("appeal", "recourse", "contest", "challenge decision", "manual exception", "recours"),
    "monitoring": ("monitoring", "sample review", "quality review", "drift", "alert on failure"),
    "fallback": ("fallback", "manual queue", "rollback", "safe stop", "safe-stop", "escalation path", "retry"),
    "access_control": ("least privilege", "access control", "role-based access", "rbac", "permission boundary"),
    "data_minimization": ("minimize", "data minimization", "minimum necessary", "only required", "least data"),
    "masking": ("mask", "masked", "redact", "redacted", "anonymize", "anonymized", "pseudonymize"),
    "grounding": ("grounded", "citation", "source record", "verified record", "policy source", "reference document"),
    "change_management": ("change management", "change review", "release approval", "version review", "rollback plan"),
    "incident_handling": ("incident handling", "incident response", "postmortem", "escalate incident", "breach"),
    "local_ai": ("ollama", "local ai", "local-only", "localhost", "no cloud", "offline model"),
}

CONTROL_GAP_RULES: tuple[dict[str, Any], ...] = (
    {
        "id": "gap_missing_human_validation",
        "category": "human_validation",
        "severity": "high",
        "factors": ["missing_human_validation"],
        "control_key": "human_review",
        "requires": {"high_impact"},
        "evidence": "No explicit human approval gate was found for the detected high-impact workflow.",
        "controls": ["ctrl_role_based_review", "ctrl_dual_control_high_risk"],
    },
    {
        "id": "gap_missing_audit_trail",
        "category": "auditability",
        "severity": "medium",
        "factors": ["missing_audit_trail"],
        "control_key": "audit_trail",
        "requires": {"high_impact"},
        "evidence": "No explicit audit trail, log, or record-of-decision wording was found.",
        "controls": ["ctrl_audit_trail", "ctrl_access_logging"],
    },
    {
        "id": "gap_missing_reviewer_identity",
        "category": "accountability",
        "severity": "medium",
        "factors": ["missing_reviewer_identity"],
        "control_key": "reviewer_identity",
        "requires": {"operational_high_impact"},
        "evidence": "No named reviewer, owner, or responsible approval role was found.",
        "controls": ["ctrl_role_based_review", "ctrl_human_feedback_loop"],
    },
    {
        "id": "gap_missing_retention_policy",
        "category": "privacy",
        "severity": "medium",
        "factors": ["missing_retention_policy"],
        "control_key": "retention",
        "requires": {"sensitive_data"},
        "evidence": "Sensitive or confidential data is indicated, but no retention or deletion policy was found.",
        "controls": ["ctrl_retention_policy", "ctrl_controlled_export"],
    },
    {
        "id": "gap_missing_data_masking",
        "category": "privacy",
        "severity": "medium",
        "factors": ["missing_data_masking"],
        "control_key": "masking",
        "requires": {"sensitive_data"},
        "evidence": "Sensitive or confidential data is indicated, but no masking, redaction, or anonymization control was found.",
        "controls": ["ctrl_redaction_before_analysis", "ctrl_data_minimization"],
    },
    {
        "id": "gap_missing_data_minimization",
        "category": "privacy",
        "severity": "medium",
        "factors": ["missing_data_minimization"],
        "control_key": "data_minimization",
        "requires": {"sensitive_data"},
        "evidence": "Sensitive or confidential data is indicated, but no data-minimization boundary was found.",
        "controls": ["ctrl_data_minimization", "ctrl_sensitive_data_warning"],
    },
    {
        "id": "gap_missing_appeal_process",
        "category": "governance",
        "severity": "high",
        "factors": ["missing_appeal_process"],
        "control_key": "appeal",
        "requires": {"decision"},
        "evidence": "A decision-like workflow is indicated, but no appeal, recourse, or exception process was found.",
        "controls": ["ctrl_management_exception_review", "ctrl_role_based_review"],
    },
    {
        "id": "gap_missing_fallback_plan",
        "category": "execution_boundary",
        "severity": "medium",
        "factors": ["missing_fallback_plan"],
        "control_key": "fallback",
        "requires": {"operational_high_impact"},
        "evidence": "No fallback, manual queue, rollback, escalation path, or safe-stop behavior was found.",
        "controls": ["ctrl_safe_failure_mode", "ctrl_escalation_policy"],
    },
    {
        "id": "gap_missing_monitoring",
        "category": "measurement",
        "severity": "medium",
        "factors": ["missing_monitoring"],
        "control_key": "monitoring",
        "requires": {"operational_high_impact"},
        "evidence": "No monitoring, sampling, quality review, or failure alerting was found.",
        "controls": ["ctrl_human_feedback_loop", "ctrl_test_regression_suite"],
    },
    {
        "id": "gap_missing_grounding",
        "category": "explainability",
        "severity": "medium",
        "factors": ["missing_grounding"],
        "control_key": "grounding",
        "requires": {"ai"},
        "evidence": "AI assistance is indicated, but no source grounding, verified record, or citation requirement was found.",
        "controls": ["ctrl_evidence_display", "ctrl_confidence_labeling"],
    },
    {
        "id": "gap_missing_access_control",
        "category": "security",
        "severity": "medium",
        "factors": ["missing_access_control"],
        "control_key": "access_control",
        "requires": {"system_access"},
        "evidence": "System access or tool/action use is indicated, but no access-control boundary was found.",
        "controls": ["ctrl_least_privilege", "ctrl_secure_configuration"],
    },
    {
        "id": "gap_missing_change_management",
        "category": "governance",
        "severity": "medium",
        "factors": ["missing_change_management"],
        "control_key": "change_management",
        "requires": {"operational_high_impact"},
        "evidence": "No change-management or release-review wording was found for the detected high-impact workflow.",
        "controls": ["ctrl_change_management", "ctrl_kb_version_review"],
    },
    {
        "id": "gap_missing_incident_handling",
        "category": "security",
        "severity": "medium",
        "factors": ["missing_incident_handling"],
        "control_key": "incident_handling",
        "requires": {"operational_high_impact"},
        "evidence": "No incident-handling path was found for incorrect, harmful, or failed automation behavior.",
        "controls": ["ctrl_safe_failure_mode", "ctrl_escalation_policy"],
    },
)

POSITIVE_CONTROL_RULES: tuple[dict[str, Any], ...] = (
    {
        "id": "ctrl_signal_fallback_present",
        "category": "execution_boundary",
        "severity": "low",
        "factors": ["fallback_present"],
        "control_key": "fallback",
        "evidence": "Fallback, manual queue, rollback, or safe-stop wording was found.",
        "controls": ["ctrl_safe_failure_mode"],
    },
    {
        "id": "ctrl_signal_local_ai_only",
        "category": "architecture",
        "severity": "low",
        "factors": ["local_ai_only_present"],
        "control_key": "local_ai",
        "evidence": "Local-only AI, Ollama, localhost, or no-cloud wording was found.",
        "controls": ["ctrl_local_only_operation"],
    },
)


def _stable_finding_id(rule_id: str, step_index: int, evidence: str) -> str:
    digest = hashlib.sha1(f"{rule_id}|{step_index}|{evidence}".encode("utf-8")).hexdigest()[:12]
    return f"finding_{digest}"


def _severity_confidence(severity: str, regex_match: bool, action_matches: int) -> float:
    base = {"low": 0.62, "medium": 0.72, "high": 0.8, "critical": 0.86}.get(severity, 0.7)
    if regex_match:
        base += 0.08
    base += min(action_matches, 2) * 0.03
    return round(min(base, 0.95), 2)


def _score_impact_for_factors(factors: list[str]) -> int:
    return sum(int(RISK_FACTORS.get(factor, {}).get("weight", 0)) for factor in factors)


def _primary_factor(factors: list[str]) -> str:
    weighted = sorted(
        (factor for factor in factors if factor in RISK_FACTORS),
        key=lambda factor: int(RISK_FACTORS[factor]["weight"]),
        reverse=True,
    )
    return weighted[0] if weighted else (factors[0] if factors else "general")


def _review_question(factors: list[str], category: str) -> str:
    factor = _primary_factor(factors)
    questions = {
        "automatic_financial_decision": "Who can approve, reverse, or challenge a refund/payment decision before it affects a customer?",
        "automatic_account_access_decision": "Who reviews account or access changes before they affect a person or security boundary?",
        "missing_human_validation": "Which named human role approves this workflow before any external, financial, or irreversible action?",
        "missing_audit_trail": "Where is the decision evidence, reviewer identity, timestamp, and final outcome recorded?",
        "missing_retention_policy": "What data is saved, why is it saved, and when is it deleted from local history?",
        "missing_appeal_process": "How can an affected customer, employee, or candidate request manual review or correction?",
        "missing_data_masking": "Which identifiers are masked or redacted before analysis and reporting?",
        "missing_fallback_plan": "What happens if the model, parser, integration, or reviewer path fails?",
        "prompt_injection_exposure": "How is untrusted input separated from system instructions and reviewed before reuse?",
        "tool_action_use": "Which actions are blocked, gated, logged, or limited to least privilege?",
        "model_decision_authority": "Is the model advising a human, or is it making the final decision?",
    }
    return questions.get(
        factor,
        f"Does this {category} finding apply in the real workflow, and what evidence proves the control exists?",
    )


def _why_it_matters(factors: list[str], category: str) -> str:
    factor = _primary_factor(factors)
    reasons = {
        "automatic_financial_decision": "Financial automation can directly affect customer money, billing state, and dispute handling.",
        "automatic_account_access_decision": "Access automation can lock people out, grant excessive permission, or change a security boundary.",
        "missing_human_validation": "High-impact automation without a named approval gate can move from assistance to unreviewed action.",
        "missing_audit_trail": "Without logs, reviewers may not be able to reconstruct evidence, decisions, or accountability.",
        "missing_retention_policy": "Sensitive data in local reports needs a retention boundary even when the tool is local-first.",
        "missing_appeal_process": "Affected people or customers may need a human path to correct an automated or AI-assisted outcome.",
        "missing_data_masking": "Sensitive identifiers can persist in screenshots, reports, or local history unless they are minimized.",
        "prompt_injection_exposure": "Untrusted text can try to manipulate model instructions or reviewer wording.",
        "missing_grounding": "Ungrounded AI output can sound confident while losing contact with the source workflow evidence.",
    }
    return reasons.get(
        factor,
        f"This {category} signal can change the review priority and should be verified against real operating controls.",
    )


def _recommended_control_sentence(controls: list[str], factors: list[str]) -> str:
    if controls:
        return f"Review and, if appropriate, implement mapped control(s): {', '.join(controls[:3])}."
    factor = _primary_factor(factors)
    return f"Define a local control for {factor.replace('_', ' ')} and document evidence before production use."


def _residual_assumption(factors: list[str]) -> str:
    factor = _primary_factor(factors)
    return (
        f"Residual-risk simulation may reduce only mapped factor '{factor}' if the selected control is actually implemented "
        "and evidence is available."
    )


def _finding_limitation() -> str:
    return "This is deterministic local text evidence. It can miss context, infer absence from missing wording, and does not prove real-world implementation."


def _augment_finding(finding: dict[str, Any]) -> dict[str, Any]:
    factors = [str(item) for item in finding.get("risk_factor_mapping", [])]
    controls = [str(item) for item in finding.get("recommended_controls", [])]
    category = str(finding.get("category", "general"))
    finding["score_impact"] = _score_impact_for_factors(factors)
    finding["why_it_matters"] = _why_it_matters(factors, category)
    finding["recommended_control"] = _recommended_control_sentence(controls, factors)
    finding["human_review_question"] = _review_question(factors, category)
    finding["residual_simulation_assumption"] = _residual_assumption(factors)
    finding["limitation"] = _finding_limitation()
    return finding


def _has_terms(normalized_text: str, terms: tuple[str, ...]) -> bool:
    return any(normalize_for_match(term) in normalized_text for term in terms)


def _control_present(normalized_text: str, control_key: str) -> bool:
    terms = CONTROL_GAP_TERMS[control_key]
    for segment in re.split(r"[.!?;\n]+", normalized_text):
        for term in terms:
            normalized_term = normalize_for_match(term)
            position = segment.find(normalized_term)
            if position < 0:
                continue
            prefix = segment[:position]
            if re.search(r"\b(?:no|without|missing|absent|sans|aucun|לא|בלי)\b", prefix):
                continue
            return True
    return False


def _context_flags(normalized_text: str, factors: set[str]) -> set[str]:
    sensitive_factors = {
        "personal_data",
        "customer_data",
        "employee_data",
        "hr_candidate_data",
        "financial_data",
        "refund_payment_data",
        "medical_health_data",
        "legal_compliance_data",
        "credentials_secrets",
        "business_confidential_data",
        "source_code_private_documents",
    }
    decision_factors = {
        "decision_affecting_person",
        "automatic_financial_decision",
        "automatic_account_access_decision",
        "model_decision_authority",
        "account_access_security",
    }
    high_impact_factors = decision_factors | {
        "external_communication",
        "customer_facing_automated_output",
        "automatic_external_action",
        "automatic_customer_communication",
        "irreversible_action",
        "data_modification_deletion",
        "sensitive_system_access",
        "broad_ai_agent_permissions",
        "soc_security_workflow",
        "tool_action_use",
    }
    operational_high_impact_factors = decision_factors | {
        "automatic_external_action",
        "automatic_customer_communication",
        "irreversible_action",
        "data_modification_deletion",
        "sensitive_system_access",
        "broad_ai_agent_permissions",
        "soc_security_workflow",
        "tool_action_use",
    }
    flags: set[str] = set()
    if factors & sensitive_factors:
        flags.add("sensitive_data")
    if factors & decision_factors:
        flags.add("decision")
    if factors & high_impact_factors:
        flags.add("high_impact")
    if factors & operational_high_impact_factors:
        flags.add("operational_high_impact")
    if factors & {"sensitive_system_access", "broad_ai_agent_permissions", "tool_action_use", "account_access_security"}:
        flags.add("system_access")
    if any(
        keyword in normalized_text
        for keyword in (
            "refund",
            "payment",
            "billing",
            "chargeback",
            "reject",
            "decision",
            "eligibility",
            "rank",
            "shortlist",
            "disable account",
            "grant access",
            "revoke access",
        )
    ):
        flags.add("decision")
        flags.add("high_impact")
        flags.add("operational_high_impact")
    if any(
        keyword in normalized_text
        for keyword in (
            "customer",
            "client",
            "employee",
            "candidate",
            "patient",
            "personal data",
            "email address",
            "address",
            "invoice",
            "refund",
            "confidential",
            "source code",
            "private document",
        )
    ):
        flags.add("sensitive_data")
    if any(
        keyword in normalized_text
        for keyword in (
            "api",
            "tool",
            "webhook",
            "agent with access",
            "admin",
            "production",
            "database",
            "siem",
            "crm",
        )
    ):
        flags.add("system_access")
        flags.add("high_impact")
        flags.add("operational_high_impact")
    if "ai" in normalized_text or "model" in normalized_text or "llm" in normalized_text or "agent" in normalized_text:
        flags.add("ai")
    return flags


def _build_gap_finding(rule: dict[str, Any], detected_language: str) -> dict[str, Any]:
    factors = [str(item) for item in rule["factors"]]
    inference_basis = str(rule["evidence"])
    is_gap = str(rule["id"]).startswith("gap_")
    evidence_type = "inferred_gap" if is_gap else "derived_control_signal"
    evidence_prefix = "Inference" if is_gap else "Derived control signal"
    matched_text_evidence = f"{evidence_prefix} (not source evidence): {inference_basis}"
    finding = {
        "finding_id": _stable_finding_id(str(rule["id"]), 0, inference_basis),
        "category": str(rule["category"]),
        "severity": str(rule["severity"]),
        "confidence": _severity_confidence(str(rule["severity"]), False, 1),
        "matched_text_evidence": matched_text_evidence,
        "evidence_type": evidence_type,
        "source_excerpt": None,
        "inference_basis": inference_basis,
        "is_hypothesis": is_gap,
        "matched_rule_id": str(rule["id"]),
        "workflow_step_reference": "workflow_overall",
        "workflow_step_text": "",
        "explanation": "Deterministic gap finding inferred from detected workflow context and missing control wording.",
        "recommended_controls": [str(item) for item in rule.get("controls", [])],
        "risk_factor_mapping": factors,
        "language_detected_when_possible": detected_language,
        "action_classification": ["control_gap"],
    }
    return _augment_finding(finding)


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
            if str(pattern.get("explanation", "")).startswith("Synthetic portfolio-safe rule"):
                continue
            positive_control_patterns = {
                "rp_human_validation": "human_review",
                "rp_audit_log": "audit_trail",
                "rp_v2_fallback_present": "fallback",
            }
            control_key = positive_control_patterns.get(str(pattern.get("id")))
            if control_key and not _control_present(normalize_for_match(step), control_key):
                continue
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
                "evidence_type": "source_excerpt",
                "source_excerpt": evidence,
                "inference_basis": None,
                "is_hypothesis": False,
                "matched_rule_id": str(pattern["id"]),
                "workflow_step_reference": f"step_{step_index}",
                "workflow_step_text": step,
                "explanation": str(pattern.get("explanation", "")),
                "recommended_controls": controls,
                "risk_factor_mapping": factors,
                "language_detected_when_possible": detected_language,
                "action_classification": actions,
            }
            findings.append(_augment_finding(finding))

    normalized_text = normalize_for_match(text or "")
    detected_factors = {
        str(factor)
        for finding in findings
        for factor in finding.get("risk_factor_mapping", [])
        if str(factor)
    }
    flags = _context_flags(normalized_text, detected_factors)

    for rule in POSITIVE_CONTROL_RULES:
        if _control_present(normalized_text, str(rule["control_key"])):
            findings.append(_build_gap_finding(rule, detected_language))

    for rule in CONTROL_GAP_RULES:
        required_flags = set(rule.get("requires", set()))
        if required_flags and not required_flags.issubset(flags):
            continue
        if _control_present(normalized_text, str(rule["control_key"])):
            continue
        findings.append(_build_gap_finding(rule, detected_language))

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
