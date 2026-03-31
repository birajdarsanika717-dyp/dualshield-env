import hashlib

def _h(s): return hashlib.sha256(s.encode()).hexdigest()
def _img(): return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI6QAAAABJRU5ErkJggg=="

SEED_CASES = [
    {"case_id": "case_001", "original_hash": _h("case_001"), "submitted_image": _img(), "manipulation_type": "face_swap",       "severity": 0.92, "platform_context": "telegram",  "spread_risk": "high",   "description": "Deepfake face swap"},
    {"case_id": "case_002", "original_hash": _h("case_002"), "submitted_image": _img(), "manipulation_type": "background_edit", "severity": 0.45, "platform_context": "instagram", "spread_risk": "medium", "description": "Offensive background"},
    {"case_id": "case_003", "original_hash": _h("case_003"), "submitted_image": _img(), "manipulation_type": "none",            "severity": 0.0,  "platform_context": "whatsapp",  "spread_risk": "low",    "description": "Authentic photo"},
    {"case_id": "case_004", "original_hash": _h("case_004"), "submitted_image": _img(), "manipulation_type": "metadata_strip",  "severity": 0.30, "platform_context": "unknown",   "spread_risk": "low",    "description": "EXIF stripped"},
    {"case_id": "case_005", "original_hash": _h("case_005"), "submitted_image": _img(), "manipulation_type": "composite",       "severity": 0.85, "platform_context": "telegram",  "spread_risk": "high",   "description": "Defamatory composite"},
    {"case_id": "case_006", "original_hash": _h("case_006"), "submitted_image": _img(), "manipulation_type": "color_grade",     "severity": 0.20, "platform_context": "instagram", "spread_risk": "low",    "description": "Color manipulation"},
    {"case_id": "case_007", "original_hash": _h("case_007"), "submitted_image": _img(), "manipulation_type": "face_swap",       "severity": 0.78, "platform_context": "whatsapp",  "spread_risk": "high",   "description": "Mobile deepfake"},
    {"case_id": "case_008", "original_hash": _h("case_008"), "submitted_image": _img(), "manipulation_type": "background_edit", "severity": 0.60, "platform_context": "telegram",  "spread_risk": "medium", "description": "Harassing overlay"},
    {"case_id": "case_009", "original_hash": _h("case_009"), "submitted_image": _img(), "manipulation_type": "none",            "severity": 0.0,  "platform_context": "instagram", "spread_risk": "low",    "description": "Verification check"},
    {"case_id": "case_010", "original_hash": _h("case_010"), "submitted_image": _img(), "manipulation_type": "composite",       "severity": 0.95, "platform_context": "unknown",   "spread_risk": "high",   "description": "Harassment campaign"},
    {"case_id": "case_011", "original_hash": _h("case_011"), "submitted_image": _img(), "manipulation_type": "metadata_strip",  "severity": 0.25, "platform_context": "whatsapp",  "spread_risk": "low",    "description": "Origin untraceable"},
    {"case_id": "case_012", "original_hash": _h("case_012"), "submitted_image": _img(), "manipulation_type": "face_swap",       "severity": 0.88, "platform_context": "unknown",   "spread_risk": "high",   "description": "Professional deepfake"},
    {"case_id": "case_013", "original_hash": _h("case_013"), "submitted_image": _img(), "manipulation_type": "color_grade",     "severity": 0.35, "platform_context": "instagram", "spread_risk": "medium", "description": "Skin tone change"},
    {"case_id": "case_014", "original_hash": _h("case_014"), "submitted_image": _img(), "manipulation_type": "background_edit", "severity": 0.72, "platform_context": "telegram",  "spread_risk": "high",   "description": "Misconduct implied"},
    {"case_id": "case_015", "original_hash": _h("case_015"), "submitted_image": _img(), "manipulation_type": "none",            "severity": 0.0,  "platform_context": "telegram",  "spread_risk": "low",    "description": "No manipulation"},
    {"case_id": "case_016", "original_hash": _h("case_016"), "submitted_image": _img(), "manipulation_type": "composite",       "severity": 0.70, "platform_context": "whatsapp",  "spread_risk": "medium", "description": "False alibi"},
    {"case_id": "case_017", "original_hash": _h("case_017"), "submitted_image": _img(), "manipulation_type": "face_swap",       "severity": 0.55, "platform_context": "instagram", "spread_risk": "medium", "description": "Low quality swap"},
    {"case_id": "case_018", "original_hash": _h("case_018"), "submitted_image": _img(), "manipulation_type": "metadata_strip",  "severity": 0.40, "platform_context": "telegram",  "spread_risk": "medium", "description": "Leaked image"},
    {"case_id": "case_019", "original_hash": _h("case_019"), "submitted_image": _img(), "manipulation_type": "color_grade",     "severity": 0.15, "platform_context": "unknown",   "spread_risk": "low",    "description": "Minor filter"},
    {"case_id": "case_020", "original_hash": _h("case_020"), "submitted_image": _img(), "manipulation_type": "composite",       "severity": 0.98, "platform_context": "telegram",  "spread_risk": "high",   "description": "Viral spread urgent"},
]
