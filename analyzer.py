from __future__ import annotations

import re
from typing import Iterable

from controls_engine import recommend_controls
from evidence_engine import run_evidence_engine
from human_validation import build_human_validation_plan
from risk_rules import calculate_risk
from risk_matrix import calculate_risk_matrix


DATA_KEYWORDS: dict[str, tuple[str, ...]] = {
    "personal_data": (
        "personal data",
        "personally identifiable",
        "name",
        "phone",
        "address",
        "email address",
        "contact detail",
        "employee",
        "candidate",
        "cv",
        "resume",
        "données personnelles",
        "adresse",
        "e-mail",
        "email",
        "שם",
        "כתובת",
    ),
    "customer_data": (
        "customer",
        "client",
        "support ticket",
        "account",
        "customer email",
        "delivery request",
        "customer notification",
        "données clients",
        "données client",
        "client",
        "notification client",
        "לקוח",
    ),
    "hr_candidate_data": (
        "candidate",
        "cv",
        "resume",
        "interview",
        "recruit",
        "hr",
        "employee",
        "screening",
        "application",
        "données rh",
        "candidat",
        "cv",
        "entretien",
        "présélection",
        "recruteur",
        "מועמד",
    ),
    "financial_data": (
        "invoice",
        "payment",
        "bank",
        "salary",
        "expense",
        "credit card",
        "billing",
        "financial",
        "facture",
        "paiement",
        "remboursement",
    ),
    "medical_health_data": (
        "medical",
        "health",
        "patient",
        "clinical",
        "diagnosis",
        "treatment",
        "santé",
        "patient",
    ),
    "legal_compliance_data": (
        "legal",
        "contract",
        "compliance",
        "regulation",
        "policy exception",
        "audit requirement",
        "juridique",
        "contrat",
        "conformité",
    ),
    "credentials_secrets": (
        "password",
        "token",
        "api key",
        "secret",
        "credential",
        "private key",
        "mot de passe",
        "jeton",
    ),
    "security_event_data": (
        "soc",
        "security alert",
        "alert triage",
        "incident",
        "siem",
        "ioc",
        "severity",
        "malware",
        "phishing",
        "unauthorized",
        "alerte sécurité",
        "alerte de sécurité",
        "escalade",
        "blocage",
    ),
    "location_logistics_data": (
        "delivery",
        "route",
        "dispatch",
        "driver",
        "shipment",
        "transport",
        "warehouse",
        "location",
        "eta",
        "schedule",
        "livraison",
        "transport",
        "localisation",
        "adresse",
        "tournée",
        "dispatcher",
    ),
    "business_confidential_data": (
        "confidential",
        "internal",
        "pricing",
        "strategy",
        "roadmap",
        "trade secret",
        "supplier",
    ),
}


WORKFLOW_KEYWORDS: dict[str, tuple[str, ...]] = {
    "customer_support": ("support", "customer email", "ticket", "reply", "escalation", "service client", "e-mails"),
    "hr": ("candidate", "cv", "resume", "interview", "hr", "recruit", "candidat", "entretien", "présélection"),
    "soc": ("soc", "security alert", "incident", "siem", "alert triage", "alerte sécurité", "escalade"),
    "logistics": ("delivery", "route", "dispatch", "shipment", "transport", "driver", "livraison", "tournée", "dispatcher"),
    "finance": ("invoice", "payment", "billing", "expense", "financial", "facture", "paiement"),
    "legal": ("legal", "contract", "compliance", "regulation", "juridique", "contrat", "conformité"),
}


HUMAN_REVIEW_KEYWORDS = (
    "human",
    "approval",
    "review",
    "analyst review",
    "manager review",
    "manual",
    "validated by",
    "sign-off",
    "sign off",
    "validation humaine",
    "approbation",
    "revue humaine",
    "valide",
    "valider",
    "אישור אנושי",
)

AUDIT_KEYWORDS = ("audit", "log", "record of decision", "trace", "history", "journal d’audit", "journal d'audit")

EXTERNAL_COMMUNICATION_KEYWORDS = (
    "email",
    "emails",
    "message",
    "send",
    "sends",
    "sending",
    "reply",
    "notify",
    "notification",
    "customer-facing",
    "external",
    "publish",
    "e-mail",
    "réponse externe",
    "notification client",
)

AUTOMATION_KEYWORDS = (
    "automate",
    "automatic",
    "automated",
    "agent",
    "ai",
    "model",
    "draft",
    "drafts",
    "suggest",
    "propose",
    "rédige",
    "résume",
)

DECISION_KEYWORDS = (
    "approve",
    "reject",
    "rank",
    "ranking",
    "score candidate",
    "eligibility",
    "qualification",
    "decision",
    "shortlist",
    "décision affectant une personne",
    "présélection",
    "candidat",
)

IRREVERSIBLE_KEYWORDS = (
    "delete",
    "deletion",
    "terminate",
    "reject",
    "close account",
    "containment",
    "disable",
    "block",
    "blocage",
    "suppression",
)

MODIFICATION_KEYWORDS = (
    "update record",
    "modify",
    "delete",
    "deletion",
    "write",
    "change record",
    "change records",
    "close ticket",
    "close incident",
    "modifier",
    "suppression",
    "tournée",
)

THIRD_PARTY_KEYWORDS = (
    "third-party",
    "third party",
    "vendor",
    "api",
    "integration",
    "crm",
    "siem",
    "hr system",
    "ticketing",
    "external service",
    "cloud",
)

SENSITIVE_ACCESS_KEYWORDS = (
    "admin",
    "privileged",
    "production",
    "siem",
    "hr system",
    "crm",
    "database",
    "sensitive system",
)

BROAD_PERMISSION_KEYWORDS = (
    "autonomous agent",
    "agent with access",
    "full access",
    "broad permissions",
    "execute actions",
    "autonomous workflow",
    "auto execute",
)


def clean_input(text: str | None) -> str:
    if text is None:
        return ""
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def _keyword_pattern(keyword: str) -> str:
    escaped = re.escape(keyword)
    if re.fullmatch(r"[a-z0-9]+", keyword):
        return rf"\b{escaped}\b"
    return escaped


def _has_any(text: str, keywords: Iterable[str]) -> bool:
    return any(re.search(_keyword_pattern(keyword), text) for keyword in keywords)


def _count_hits(text: str, keywords: Iterable[str]) -> int:
    return sum(1 for keyword in keywords if re.search(_keyword_pattern(keyword), text))


def _detect_from_keywords(text: str, keyword_map: dict[str, tuple[str, ...]]) -> list[str]:
    return [key for key, keywords in keyword_map.items() if _has_any(text, keywords)]


def extract_steps(text: str) -> list[str]:
    cleaned = clean_input(text)
    if not cleaned:
        return []

    chunks = re.split(r"\n+|(?<=[.!?])\s+", cleaned)
    steps: list[str] = []
    for chunk in chunks:
        chunk = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", chunk).strip(" -\t")
        if len(chunk) < 8:
            continue
        steps.append(chunk)

    if len(steps) < 2:
        steps = [
            part.strip(" -\t")
            for part in re.split(r"\s+(?:then|and then|after that)\s+|;", cleaned, flags=re.I)
            if len(part.strip()) >= 8
        ]

    return steps[:12] or ["Review the submitted workflow text."]


def classify_workflow(text: str) -> str:
    lower_text = text.casefold()
    scores = {
        workflow_type: _count_hits(lower_text, keywords)
        for workflow_type, keywords in WORKFLOW_KEYWORDS.items()
    }
    best_type, best_score = max(scores.items(), key=lambda item: item[1])
    return best_type if best_score > 0 else "general_business"


def detect_sensitive_data(text: str) -> list[str]:
    return _detect_from_keywords(text.casefold(), DATA_KEYWORDS)


def detect_risk_factors(text: str, categories: list[str]) -> list[str]:
    lower_text = text.casefold()
    factors: list[str] = []

    category_to_factor = {
        "personal_data": "personal_data",
        "customer_data": "customer_data",
        "hr_candidate_data": "hr_candidate_data",
        "financial_data": "financial_data",
        "medical_health_data": "medical_health_data",
        "legal_compliance_data": "legal_compliance_data",
        "security_event_data": "soc_security_workflow",
    }
    factors.extend(category_to_factor[category] for category in categories if category in category_to_factor)

    has_external = _has_any(lower_text, EXTERNAL_COMMUNICATION_KEYWORDS)
    has_automation = _has_any(lower_text, AUTOMATION_KEYWORDS)
    has_decision = _has_any(lower_text, DECISION_KEYWORDS)
    has_irreversible = _has_any(lower_text, IRREVERSIBLE_KEYWORDS)
    has_modification = _has_any(lower_text, MODIFICATION_KEYWORDS)
    has_third_party = _has_any(lower_text, THIRD_PARTY_KEYWORDS)
    has_sensitive_access = _has_any(lower_text, SENSITIVE_ACCESS_KEYWORDS) or "credentials_secrets" in categories
    has_broad_permissions = _has_any(lower_text, BROAD_PERMISSION_KEYWORDS)
    negated_review = re.search(r"\b(?:no|without)\s+(?:human\s+)?(?:review|approval)\b", lower_text)
    has_human_review = _has_any(lower_text, HUMAN_REVIEW_KEYWORDS) and not negated_review
    has_audit = _has_any(lower_text, AUDIT_KEYWORDS)

    if has_external:
        factors.append("external_communication")
    if has_external and ("customer_data" in categories or "customer" in lower_text) and has_automation:
        factors.append("customer_facing_automated_output")
    if has_decision or "hr_candidate_data" in categories:
        factors.append("decision_affecting_person")
    if has_irreversible:
        factors.append("irreversible_action")
    if has_modification:
        factors.append("data_modification_deletion")
    if has_third_party:
        factors.append("third_party_integration")
    if has_sensitive_access:
        factors.append("sensitive_system_access")
    if has_broad_permissions:
        factors.append("broad_ai_agent_permissions")

    high_impact = any(
        factor in factors
        for factor in (
            "external_communication",
            "customer_facing_automated_output",
            "decision_affecting_person",
            "irreversible_action",
            "data_modification_deletion",
            "sensitive_system_access",
            "broad_ai_agent_permissions",
            "soc_security_workflow",
        )
    )
    if high_impact and not has_human_review:
        factors.append("missing_human_validation")
    if high_impact and not has_audit:
        factors.append("missing_audit_trail")

    return list(dict.fromkeys(factors))


def detect_cybersecurity_risks(text: str, categories: list[str], factors: list[str]) -> list[str]:
    lower_text = text.casefold()
    risks: list[str] = []

    if categories:
        risks.append("sensitive_data_exposure")
    if "external_communication" in factors:
        risks.append("unreviewed_external_communication")
    if "missing_audit_trail" in factors:
        risks.append("weak_auditability")
    if "broad_ai_agent_permissions" in factors:
        risks.append("excessive_automation_permissions")
    if "third_party_integration" in factors:
        risks.append("third_party_integration_risk")
    if _has_any(lower_text, ("email", "intake", "submitted", "message", "ticket", "prompt")):
        risks.append("prompt_injection_risk")
    if "data_modification_deletion" in factors:
        risks.append("unauthorized_data_modification")
    if "soc_security_workflow" in factors:
        risks.append("incorrect_security_alert_prioritization")
        risks.append("over_automation_of_incident_response")
    if "missing_human_validation" in factors:
        risks.append("missing_high_impact_approval")

    return list(dict.fromkeys(risks))


def detect_privacy_risks(text: str, categories: list[str], factors: list[str]) -> list[str]:
    lower_text = text.casefold()
    risks: list[str] = []

    if "personal_data" in categories:
        risks.append("personal_data_in_workflow")
    if "hr_candidate_data" in categories:
        risks.append("candidate_employee_data")
    if "customer_data" in categories:
        risks.append("customer_data_in_workflow")
    if "financial_data" in categories:
        risks.append("financial_data_in_workflow")
    if "medical_health_data" in categories:
        risks.append("medical_data_in_workflow")
    if "external_communication" in factors:
        risks.append("external_sharing_or_messaging")
    if not _has_any(lower_text, ("minimize", "data minimization", "only required", "redact")):
        risks.append("data_minimization_gap")
    if not _has_any(lower_text, ("retention", "delete after", "archive policy")):
        risks.append("retention_policy_gap")
    if not _has_any(lower_text, ("consent", "notice", "transparency")) and categories:
        risks.append("transparency_gap")
    if "decision_affecting_person" in factors:
        risks.append("automated_decision_impact")
    if "third_party_integration" in factors:
        risks.append("third_party_processing_risk")

    return list(dict.fromkeys(risks))


def detect_human_checkpoints(categories: list[str], factors: list[str]) -> list[str]:
    checkpoints: list[str] = []

    if "external_communication" in factors or "customer_facing_automated_output" in factors:
        checkpoints.append("approve_external_messages")
    if "hr_candidate_data" in categories or "decision_affecting_person" in factors:
        checkpoints.append("review_people_affecting_decisions")
    if "financial_data" in categories:
        checkpoints.append("review_financial_decisions")
    if "legal_compliance_data" in categories:
        checkpoints.append("review_legal_compliance")
    if "medical_health_data" in categories:
        checkpoints.append("review_health_workflows")
    if "soc_security_workflow" in factors:
        checkpoints.append("analyst_review_security_response")
    if "irreversible_action" in factors or "data_modification_deletion" in factors:
        checkpoints.append("approve_record_changes")
    if "third_party_integration" in factors:
        checkpoints.append("review_third_party_actions")
    if categories:
        checkpoints.append("validate_sensitive_data_use")
    if "broad_ai_agent_permissions" in factors:
        checkpoints.append("approve_agent_permissions")

    return list(dict.fromkeys(checkpoints))


def build_automation_opportunities(workflow_type: str, categories: list[str], factors: list[str]) -> dict[str, list[str]]:
    good = ["summarize_workflow", "classify_requests", "draft_internal_notes", "extract_non_sensitive_fields"]
    approval = []
    poor = []
    guardrails = ["human_approval_gate", "audit_log", "data_minimization", "least_privilege"]

    if workflow_type == "customer_support":
        good.extend(["draft_customer_response", "suggest_escalation_category"])
    if workflow_type == "hr":
        good.extend(["summarize_candidate_material", "prepare_interview_checklist"])
    if workflow_type == "soc":
        good.extend(["summarize_alert_context", "suggest_triage_questions"])
    if workflow_type == "logistics":
        good.extend(["summarize_delivery_request", "draft_customer_update", "flag_operational_exceptions"])

    if "external_communication" in factors:
        approval.append("external_messages")
    if "decision_affecting_person" in factors:
        approval.append("people_affecting_decisions")
    if "data_modification_deletion" in factors:
        approval.append("record_changes")
    if "soc_security_workflow" in factors:
        approval.append("security_escalation")
    if "financial_data" in categories:
        approval.append("financial_actions")

    if "irreversible_action" in factors:
        poor.append("irreversible_actions")
    if "soc_security_workflow" in factors:
        poor.append("autonomous_incident_containment")
    if "medical_health_data" in categories:
        poor.append("medical_determinations")
    if "legal_compliance_data" in categories:
        poor.append("legal_determinations")
    if "hr_candidate_data" in categories:
        poor.append("unreviewed_hr_decisions")
    if "credentials_secrets" in categories:
        poor.append("secret_handling")

    return {
        "good_candidates": list(dict.fromkeys(good)),
        "requires_approval": list(dict.fromkeys(approval)) or ["review_before_external_impact"],
        "poor_candidates": list(dict.fromkeys(poor)) or ["unreviewed_high_impact_actions"],
        "guardrails": list(dict.fromkeys(guardrails)),
    }


def analyze_workflow(text: str | None) -> dict[str, object]:
    cleaned = clean_input(text)
    if not cleaned:
        return {
            "valid": False,
            "error": "empty_input",
            "workflow_summary": "",
            "steps": [],
            "workflow_type": "unknown",
            "sensitive_data": [],
            "cybersecurity_risks": [],
            "privacy_risks": [],
            "human_checkpoints": [],
            "automation_opportunities": {
                "good_candidates": [],
                "requires_approval": [],
                "poor_candidates": [],
                "guardrails": [],
            },
            "risk": calculate_risk([]),
            "minimal_architecture": [],
            "implementation_notes": [],
            "limitations": [],
            "findings": [],
            "risk_matrix": calculate_risk_matrix([], []),
            "recommended_controls": [],
            "human_validation_plan": [],
            "evidence_chain": [],
            "language_detected": "unknown",
        }

    lower_text = cleaned.casefold()
    steps = extract_steps(cleaned)
    workflow_type = classify_workflow(cleaned)
    categories = detect_sensitive_data(cleaned)
    factors = detect_risk_factors(cleaned, categories)
    cybersecurity_risks = detect_cybersecurity_risks(cleaned, categories, factors)
    privacy_risks = detect_privacy_risks(cleaned, categories, factors)
    human_checkpoints = detect_human_checkpoints(categories, factors)
    risk = calculate_risk(factors)
    evidence_result = run_evidence_engine(cleaned)
    findings = evidence_result["findings"]
    risk_matrix = calculate_risk_matrix(findings, factors)
    recommended_controls = recommend_controls(findings)
    risk_matrix["mapped_controls"] = [
        {"id": control["id"], "name": control["name"], "risk_factors": control.get("risk_factors", [])}
        for control in recommended_controls
    ]
    human_validation_plan = build_human_validation_plan(findings, recommended_controls)

    summary = (
        f"Potential {workflow_type.replace('_', ' ')} workflow with {len(steps)} detected step"
        f"{'' if len(steps) == 1 else 's'}. The audit highlights automation candidates, sensitive data signals, "
        "security and privacy considerations, and human validation points."
    )

    minimal_architecture = [
        "local_streamlit_ui",
        "deterministic_analyzer",
        "transparent_risk_rules",
        "markdown_export",
    ]
    if _has_any(lower_text, AUTOMATION_KEYWORDS):
        minimal_architecture.append("optional_local_llm_enrichment")

    implementation_notes = [
        "keep_recommendation_separate_from_execution",
        "avoid_persistent_storage",
        "use_anonymized_inputs",
        "document_review_decisions",
    ]
    if "third_party_integration" in factors:
        implementation_notes.append("review_integration_boundaries")

    limitations = [
        "keyword_based_detection",
        "not_compliance_certification",
        "requires_domain_review",
        "not_connected_to_production_systems",
    ]

    return {
        "valid": True,
        "error": None,
        "workflow_summary": summary,
        "steps": steps,
        "workflow_type": workflow_type,
        "sensitive_data": categories,
        "cybersecurity_risks": cybersecurity_risks,
        "privacy_risks": privacy_risks,
        "human_checkpoints": human_checkpoints,
        "automation_opportunities": build_automation_opportunities(workflow_type, categories, factors),
        "risk": risk,
        "minimal_architecture": minimal_architecture,
        "implementation_notes": implementation_notes,
        "limitations": limitations,
        "findings": findings,
        "risk_matrix": risk_matrix,
        "recommended_controls": recommended_controls,
        "human_validation_plan": human_validation_plan,
        "evidence_chain": [
            {
                "workflow_step": finding.get("workflow_step_reference"),
                "matched_evidence": finding.get("matched_text_evidence"),
                "finding": finding.get("finding_id"),
                "risk_factors": finding.get("risk_factor_mapping", []),
                "score_impact": [
                    entry
                    for entry in risk_matrix.get("entries", [])
                    if entry.get("factor") in finding.get("risk_factor_mapping", [])
                ],
                "recommended_controls": finding.get("recommended_controls", []),
                "report_section": "Detected Evidence",
            }
            for finding in findings
        ],
        "language_detected": evidence_result.get("language_detected", "unknown"),
    }
