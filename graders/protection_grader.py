def grade_protection(watermark_present: bool, signature_valid: bool) -> float:
    return round((0.5 * int(watermark_present)) + (0.5 * int(signature_valid)), 4)
