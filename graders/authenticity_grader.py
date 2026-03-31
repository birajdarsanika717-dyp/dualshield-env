def grade_authenticity(prediction: str, ground_truth: str, confidence: float) -> float:
    if prediction == ground_truth:
        base = 1.0
    elif prediction == "none" and ground_truth != "none":
        base = 0.0
    else:
        base = 0.3
    return round(base * min(max(confidence, 0.0), 0.99), 4)
