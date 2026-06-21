from risk_rules import calculate_risk, calculate_score, get_risk_level


def test_risk_level_thresholds():
    assert get_risk_level(0) == "low"
    assert get_risk_level(4) == "low"
    assert get_risk_level(5) == "medium"
    assert get_risk_level(9) == "medium"
    assert get_risk_level(10) == "high"
    assert get_risk_level(15) == "high"
    assert get_risk_level(16) == "critical"


def test_known_factors_add_expected_values():
    factors = ["personal_data", "customer_data", "external_communication"]
    assert calculate_score(factors) == 6


def test_duplicate_and_unknown_factors_are_stable():
    factors = ["customer_data", "unknown", "customer_data", "personal_data"]
    result = calculate_risk(factors)
    assert result["score"] == 4
    assert result["factors"] == ["personal_data", "customer_data"]


def test_same_factors_always_produce_same_score():
    factors = ["soc_security_workflow", "sensitive_system_access", "missing_audit_trail"]
    first = calculate_risk(factors)
    second = calculate_risk(list(reversed(factors)))
    assert first["score"] == second["score"]
    assert first["level"] == second["level"]
    assert first["breakdown"] == second["breakdown"]
