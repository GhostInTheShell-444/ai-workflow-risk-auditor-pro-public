from __future__ import annotations


EXAMPLES: dict[str, dict[str, object]] = {
    "customer_support": {
        "labels": {
            "en": "Customer Support Email Workflow",
            "fr": "Flux d'e-mails du support client",
            "he": "תהליך דוא״ל לתמיכת לקוחות",
        },
        "text": """A customer support inbox receives anonymized customer emails and support tickets.
The team classifies each request by topic, urgency, and required department.
An AI workflow may draft a suggested answer using approved knowledge base content.
A support agent reviews the draft, checks customer account context, and approves any customer-facing response before sending.
Complex complaints, refunds, or policy exceptions are escalated to a manager.
The process keeps an audit log of classification, review, approval, and final message decisions.""",
    },
    "hr_candidate_screening": {
        "labels": {
            "en": "HR Candidate Screening Workflow",
            "fr": "Flux de présélection RH",
            "he": "תהליך סינון מועמדים במשאבי אנוש",
        },
        "text": """HR receives anonymized CV and application material for an open role.
The workflow summarizes qualifications, required skills, and interview availability.
An AI workflow may prepare an internal shortlist suggestion and interview checklist.
Human HR review is required before candidate ranking, interview scheduling, rejection, or any decision affecting a person.
Candidate personal data is minimized and access is limited to the hiring team.
The process keeps an audit log of review decisions and final HR actions.""",
    },
    "soc_alert_triage": {
        "labels": {
            "en": "SOC Alert Triage Workflow",
            "fr": "Flux de triage des alertes SOC",
            "he": "תהליך מיון התראות SOC",
        },
        "text": """A SOC analyst receives anonymized security alert details from an internal queue without direct SIEM integration.
The workflow classifies severity, summarizes safe internal context, and suggests triage questions.
An AI workflow may draft an internal note and recommend escalation priority.
An analyst reviews every recommendation before escalation, closure, or incident response.
No automated containment, blocking, deletion, or production action is allowed in this MVP.
The process keeps an audit log of alert classification, analyst review, escalation decision, and final status.""",
    },
    "logistics_operations": {
        "labels": {
            "en": "Logistics / Transport Operations Workflow",
            "fr": "Flux opérations logistiques / transport",
            "he": "תהליך תפעול לוגיסטיקה והובלה",
        },
        "text": """A logistics team receives anonymized delivery requests with customer contact, location, schedule, and shipment constraints.
The workflow summarizes delivery requirements and suggests route or dispatch planning options.
An AI workflow may draft customer notification text for delay, ETA, or exception handling.
A dispatcher reviews route suggestions and approves any external customer message or dispatch-impacting change before action.
Operational exceptions such as damaged shipment, missed delivery window, or address mismatch are escalated for human review.
The process keeps an audit log of scheduling recommendations, dispatcher approval, customer communication, and final operational status.""",
    },
}


def get_example_label(example_key: str, language: str = "en") -> str:
    example = EXAMPLES[example_key]
    labels = example["labels"]
    assert isinstance(labels, dict)
    return str(labels.get(language) or labels["en"])


def get_example_text(example_key: str) -> str:
    return str(EXAMPLES[example_key]["text"])
