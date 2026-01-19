# scoring/risk.py

def compute_risk(verdict: dict) -> dict:
    """
    Convert evaluator verdict into a normalized risk score.
    """

    severity = verdict.get("severity", 0.0)
    confidence = verdict.get("confidence", 0.0)
    decision = verdict.get("verdict", "error")

    # Base risk score
    risk_score = round(severity * confidence, 3)

    # Normalize by verdict
    if decision == "pass":
        risk_score = 0.0
    elif decision == "partial":
        risk_score *= 0.5
    elif decision == "error":
        risk_score = 0.0

    # Risk bands (opinionated but sane)
    if risk_score >= 0.7:
        level = "critical"
    elif risk_score >= 0.4:
        level = "high"
    elif risk_score >= 0.2:
        level = "medium"
    else:
        level = "low"

    return {
        "risk_score": risk_score,
        "risk_level": level
    }
