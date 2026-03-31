def grade_pipeline(detection_acc: float, spread_correct: bool, proof_quality: bool, legal_steps_followed: bool) -> float:
    score = (
        detection_acc * 0.3
        + float(spread_correct) * 0.2
        + float(proof_quality) * 0.3
        + float(legal_steps_followed) * 0.2
    )
    return round(min(score, 1.0), 4)
