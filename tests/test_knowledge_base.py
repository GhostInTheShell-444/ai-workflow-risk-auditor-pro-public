from knowledge_loader import (
    CONTROL_EFFECT_KEYS,
    CONTROL_KEYS,
    DATA_CATEGORY_KEYS,
    EXPLANATION_CARD_KEYS,
    FRAMEWORK_MAPPING_KEYS,
    REVIEW_QUESTION_KEYS,
    RISK_FACTOR_GROUP_KEYS,
    RISK_PATTERN_KEYS,
    knowledge_counts,
    load_control_library,
    load_data_categories,
    load_demo_scenarios,
    load_explanation_cards,
    load_framework_mappings_v2,
    load_control_effects_v2,
    load_risk_patterns,
    load_risk_factors_v2,
    load_review_questions_v2,
    load_workflow_templates,
    validate_knowledge_base,
)


def test_knowledge_base_counts_meet_minimums():
    counts = knowledge_counts()
    assert counts["risk_patterns"] >= 25
    assert counts["control_library"] >= 40
    assert counts["demo_scenarios"] >= 20
    assert counts["workflow_templates"] >= 20
    assert counts["explanation_cards"] >= 25


def test_risk_patterns_have_required_schema():
    assert all(RISK_PATTERN_KEYS.issubset(item) for item in load_risk_patterns(enabled_only=False))


def test_controls_have_required_schema():
    assert all(CONTROL_KEYS.issubset(item) for item in load_control_library(enabled_only=False))


def test_data_categories_have_required_schema():
    assert all(DATA_CATEGORY_KEYS.issubset(item) for item in load_data_categories())


def test_explanation_cards_have_required_schema():
    assert all(EXPLANATION_CARD_KEYS.issubset(item) for item in load_explanation_cards())


def test_demo_scenarios_are_synthetic_and_enabled():
    scenarios = load_demo_scenarios()
    assert scenarios
    assert all(scenario["enabled"] for scenario in scenarios)
    assert all(scenario["synthetic"] is True for scenario in scenarios)


def test_workflow_templates_are_available():
    templates = load_workflow_templates()
    assert len(templates) >= 20
    assert all("workflow_text" in template for template in templates)


def test_control_ids_are_unique():
    control_ids = [control["id"] for control in load_control_library(enabled_only=False)]
    assert len(control_ids) == len(set(control_ids))


def test_pattern_control_references_exist():
    control_ids = {control["id"] for control in load_control_library(enabled_only=False)}
    for pattern in load_risk_patterns(enabled_only=False):
        assert set(pattern["recommended_control_ids"]).issubset(control_ids)


def test_required_french_keywords_are_loadable():
    keywords = " ".join(
        keyword
        for pattern in load_risk_patterns()
        for keyword in pattern["keywords"]
    ).casefold()
    for required in ["données clients", "présélection", "validation humaine", "alerte sécurité", "livraison"]:
        assert required in keywords


def test_explanation_cards_cover_core_concepts():
    topics = {card["id"] for card in load_explanation_cards()}
    for required in ["risk_score", "evidence", "control", "residual_risk", "local_first", "deterministic"]:
        assert required in topics


def test_v2_reference_knowledge_files_are_local_and_structured():
    factor_groups = load_risk_factors_v2()
    effects = load_control_effects_v2()
    mappings = load_framework_mappings_v2()
    questions = load_review_questions_v2()
    assert all(RISK_FACTOR_GROUP_KEYS.issubset(item) for item in factor_groups)
    assert all(CONTROL_EFFECT_KEYS.issubset(item) for item in effects)
    assert all(FRAMEWORK_MAPPING_KEYS.issubset(item) for item in mappings)
    assert all(REVIEW_QUESTION_KEYS.issubset(item) for item in questions)
    assert all(item["runtime_status"] == "reference_only" for item in factor_groups + effects + mappings + questions)


def test_knowledge_base_cross_references_are_valid():
    validate_knowledge_base()


def test_synthetic_filler_patterns_are_not_active():
    active_patterns = load_risk_patterns()
    assert not any("synthetic risk pattern" in pattern["name"].casefold() for pattern in active_patterns)
    assert not any(
        pattern["explanation"].startswith("Synthetic portfolio-safe rule")
        for pattern in active_patterns
    )


def test_controls_are_recommendations_not_implementation_claims():
    for control in load_control_library(enabled_only=False):
        assert control["implementation_status"] == "recommended_not_verified"
        assert "not measured efficacy" in control["effectiveness_note"]
        assert "proof of implementation" in control["effectiveness_note"]


def test_framework_mappings_are_non_certifying_and_non_exhaustive():
    boundaries = " ".join(item["claim_boundary"] for item in load_framework_mappings_v2()).casefold()
    assert "not a certification" in boundaries
    assert "does not establish effectiveness" in boundaries
    assert "cannot prove mitigation was implemented" in boundaries


def test_review_questions_remain_questions():
    assert all(item["question"].endswith("?") for item in load_review_questions_v2())


def test_explanation_cards_do_not_contain_numbered_placeholders():
    cards = load_explanation_cards()
    assert not any("concept " in card["title"].casefold() for card in cards)
    assert not any("short explanation for" in card["short_explanation"].casefold() for card in cards)
