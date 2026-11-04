from fsociety.modules.password import audit_password


def test_weak_password_patterns_are_reported():
    result = audit_password("Password123!!!")
    assert result["length"] == 14
    assert result["patterns"]
    assert result["score"] < 4


def test_long_diverse_password_rates_well():
    result = audit_password("R7!vQ2#kLm9@pZ4x")
    assert result["length"] >= 14
    assert result["score"] == 4
    assert "password" not in result
