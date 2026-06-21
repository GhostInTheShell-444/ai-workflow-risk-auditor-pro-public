from knowledge_loader import (
    CONTROL_KEYS,
    DATA_CATEGORY_KEYS,
    EXPLANATION_CARD_KEYS,
    RISK_PATTERN_KEYS,
    knowledge_counts,
    load_control_library,
    load_data_categories,
    load_demo_scenarios,
    load_explanation_cards,
    load_risk_patterns,
    load_workflow_templates,
)


def test_knowledge_base_counts_meet_minimums():
    counts = knowledge_counts()
    assert counts["risk_patterns"] >= 120
    assert counts["control_library"] >= 40
    assert counts["demo_scenarios"] >= 20
    assert counts["workflow_templates"] >= 20
    assert counts["explanation_cards"] >= 25


def test_risk_patterns_have_required_schema():
    assert RISK_PATTERN_KEYS.issubset(load_risk_patterns()[0].keys())


def test_controls_have_required_schema():
    assert CONTROL_KEYS.issubset(load_control_library()[0].keys())


def test_data_categories_have_required_schema():
    assert DATA_CATEGORY_KEYS.issubset(load_data_categories()[0].keys())


def test_explanation_cards_have_required_schema():
    assert EXPLANATION_CARD_KEYS.issubset(load_explanation_cards()[0].keys())


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
    control_ids = [control["id"] for control in load_control_library()]
    assert len(control_ids) == len(set(control_ids))


def test_pattern_control_references_exist():
    control_ids = {control["id"] for control in load_control_library()}
    for pattern in load_risk_patterns():
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
