from analyzer import analyze_workflow
from evidence_engine import run_evidence_engine
from workflow_parser import detect_language, extract_workflow_steps


FRENCH_SUPPORT = "Le service client reçoit des e-mails contenant des données clients et l’IA rédige une réponse proposée avant validation humaine."
FRENCH_HR = "Le service RH reçoit des CV anonymisés, résume les compétences et propose une présélection, mais un recruteur valide toute décision affectant un candidat."
FRENCH_SOC = "Un analyste SOC reçoit une alerte de sécurité, l’IA résume le contexte et propose une priorité d’escalade, mais aucune action de blocage n’est exécutée automatiquement."
FRENCH_LOGISTICS = "Une équipe logistique reçoit une demande de livraison avec adresse, créneau horaire et notification client. L’IA propose un résumé, mais le dispatcher valide toute modification de tournée."


def test_evidence_findings_include_required_fields():
    result = run_evidence_engine(FRENCH_SUPPORT)
    finding = result["findings"][0]
    for key in [
        "finding_id",
        "category",
        "severity",
        "confidence",
        "matched_text_evidence",
        "matched_rule_id",
        "workflow_step_reference",
        "explanation",
        "recommended_controls",
        "risk_factor_mapping",
        "language_detected_when_possible",
    ]:
        assert key in finding


def test_french_customer_support_detection_has_controls_and_matrix():
    result = analyze_workflow(FRENCH_SUPPORT)
    assert result["workflow_type"] == "customer_support"
    assert result["findings"]
    assert result["recommended_controls"]
    assert result["human_validation_plan"]
    assert result["risk_matrix"]["entries"]


def test_french_hr_detection_has_candidate_risk():
    result = analyze_workflow(FRENCH_HR)
    assert "hr_candidate_data" in result["sensitive_data"]
    assert any("hr_candidate_data" in entry["factor"] for entry in result["risk_matrix"]["entries"])
    assert any(plan["responsible_role"] == "HR recruiter" for plan in result["human_validation_plan"])


def test_french_soc_detection_has_soc_risk_and_no_action_execution_claim():
    result = analyze_workflow(FRENCH_SOC)
    assert result["workflow_type"] == "soc"
    assert any(entry["factor"] == "soc_security_workflow" for entry in result["risk_matrix"]["entries"])
    assert any(plan["responsible_role"] == "SOC analyst" for plan in result["human_validation_plan"])


def test_french_logistics_detection_has_dispatcher_checkpoint():
    result = analyze_workflow(FRENCH_LOGISTICS)
    assert result["workflow_type"] == "logistics"
    assert "location_logistics_data" in result["sensitive_data"]
    assert any(plan["responsible_role"] == "Dispatcher" for plan in result["human_validation_plan"])


def test_regex_email_like_evidence_is_detected():
    result = run_evidence_engine("Support receives a synthetic message from demo.user@example.test for review.")
    assert any("@" in finding["matched_text_evidence"] for finding in result["findings"])


def test_credential_like_regex_is_detected():
    result = run_evidence_engine("A user pasted token=DEMOONLY12345 into a synthetic workflow.")
    assert any("credentials_secrets" in finding["risk_factor_mapping"] for finding in result["findings"])


def test_finding_ids_are_deterministic():
    first = run_evidence_engine(FRENCH_SUPPORT)["findings"]
    second = run_evidence_engine(FRENCH_SUPPORT)["findings"]
    assert [finding["finding_id"] for finding in first] == [finding["finding_id"] for finding in second]


def test_empty_text_has_no_steps_or_findings():
    result = run_evidence_engine(" ")
    assert result["steps"] == []
    assert result["findings"] == []


def test_language_detection_handles_french_hebrew_and_english():
    assert detect_language(FRENCH_SUPPORT) == "fr"
    assert detect_language("תהליך תמיכה כולל אישור אנושי") == "he"
    assert detect_language("Support receives a customer email.") == "en"


def test_language_detection_avoids_english_false_positives():
    assert detect_language("A candidate uploads a CV and HR schedules an interview.") == "en"
    assert detect_language("A dispatcher reviews route options before notifying the customer.") == "en"


def test_workflow_step_extraction_handles_numbered_steps():
    steps = extract_workflow_steps("1. Receive customer email.\n2. Human review before sending.")
    assert steps == ["Receive customer email.", "Human review before sending."]
