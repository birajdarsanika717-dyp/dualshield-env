RISK_ORDER = {"low": 0, "medium": 1, "high": 2}

def grade_spread(predicted_risk: str, actual_risk: str) -> float:
    diff = abs(RISK_ORDER.get(predicted_risk, 1) - RISK_ORDER.get(actual_risk, 1))
    return round(max(0.0, 1.0 - (diff * 0.5)), 4)
