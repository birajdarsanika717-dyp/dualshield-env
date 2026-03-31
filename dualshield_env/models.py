from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
import uuid

class ImageCase(BaseModel):
    case_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    original_hash: str
    submitted_image: str
    manipulation_type: Literal["none","face_swap","background_edit","metadata_strip","color_grade","composite"]
    severity: float = Field(ge=0.0, le=1.0)
    spread_risk: Literal["low","medium","high"]
    platform_context: str
    description: str = ""

class UserProfile(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    watermarks_applied: int = 0
    cases_submitted: int = 0
    legal_actions_taken: int = 0
    protection_score: float = Field(default=0.0, ge=0.0, le=1.0)

class DualShieldState(BaseModel):
    episode_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    step_count: int = 0
    current_case: ImageCase
    user: UserProfile
    available_actions: List[str] = Field(default_factory=list)
    is_terminal: bool = False
    task_id: str = "task_protect"
    cumulative_reward: float = 0.0
    authenticity_score: Optional[float] = None
    detected_manipulation: Optional[str] = None
    spread_risk_assessed: Optional[str] = None
    proof_generated: bool = False
    legal_guidance_triggered: bool = False
    report_filed: bool = False
    watermark_applied: bool = False
    signature_applied: bool = False

class Action(BaseModel):
    action_type: Literal["apply_watermark","apply_pixel_signature","analyze_authenticity","compare_images","generate_proof_report","assess_spread_risk","trigger_legal_guidance","file_cybercrime_report"]
    payload: Dict[str, Any] = Field(default_factory=dict)

class Observation(BaseModel):
    case_id: str
    step_count: int
    task_id: str
    image_metadata: Dict[str, Any]
    authenticity_score: Optional[float]
    manipulation_type: Optional[str]
    severity: float
    spread_risk: str
    legal_status: str
    available_actions: List[str]
    watermark_applied: bool
    signature_applied: bool
    proof_generated: bool
    legal_guidance_triggered: bool
    report_filed: bool
    cumulative_reward: float

class ResetResult(BaseModel):
    episode_id: str
    observation: Observation
    task_id: str
    message: str = "Episode reset."

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)

class StateResult(BaseModel):
    state: DualShieldState
    observation: Observation

class ResetRequest(BaseModel):
    task_id: Literal["task_protect","task_detect","task_respond"] = "task_protect"
    case_id: Optional[str] = None

class StepRequest(BaseModel):
    episode_id: str
    action: Action
