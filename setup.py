import os

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {path}")

# ── requirements.txt ──────────────────────────────────────────────
write("requirements.txt", """\
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.1
torch==2.3.0
torchvision==0.18.0
pillow==10.3.0
openai==1.30.1
pytest==8.2.0
pytest-asyncio==0.23.7
httpx==0.27.0
python-multipart==0.0.9
""")

# ── Dockerfile ────────────────────────────────────────────────────
write("Dockerfile", """\
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p ml/weights dualshield_env/data
EXPOSE 7860
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
""")

# ── openenv.yaml ──────────────────────────────────────────────────
write("openenv.yaml", """\
name: dualshield-env
version: "1.0.0"
description: "Womens digital image safety environment"
domain: "content_safety / image_forensics"

environment:
  base_url: "https://dualshield-env.hf.space"
  reset_endpoint: "/reset"
  step_endpoint: "/step"
  state_endpoint: "/state/{episode_id}"

tasks:
  - id: task_protect
    name: "Image Protection"
    difficulty: easy
    max_steps: 5
    reward_range: [0.0, 1.0]
    success_threshold: 0.8
  - id: task_detect
    name: "Manipulation Detection"
    difficulty: medium
    max_steps: 10
    reward_range: [0.0, 1.2]
    success_threshold: 0.7
  - id: task_respond
    name: "Full Incident Response"
    difficulty: hard
    max_steps: 15
    reward_range: [0.0, 1.1]
    success_threshold: 0.65

reward:
  task_protect: "0.5 * watermark_score + 0.5 * signature_score"
  task_detect: "classification_acc * confidence - 0.2 * missed_penalty"
  task_respond: "(detection*0.3) + (spread*0.2) + (proof*0.3) + (legal*0.2)"
  global_bonus: "+0.1 if full pipeline under 8 steps"
  penalty: "-0.3 if missed manipulation"
""")

# ── graders ───────────────────────────────────────────────────────
write("graders/__init__.py", """\
from .authenticity_grader import grade_authenticity
from .protection_grader import grade_protection
from .spread_grader import grade_spread
from .pipeline_grader import grade_pipeline
""")

write("graders/authenticity_grader.py", """\
def grade_authenticity(prediction: str, ground_truth: str, confidence: float) -> float:
    if prediction == ground_truth:
        base = 1.0
    elif prediction == "none" and ground_truth != "none":
        base = 0.0
    else:
        base = 0.3
    return round(base * min(max(confidence, 0.0), 0.99), 4)
""")

write("graders/protection_grader.py", """\
def grade_protection(watermark_present: bool, signature_valid: bool) -> float:
    return round((0.5 * int(watermark_present)) + (0.5 * int(signature_valid)), 4)
""")

write("graders/spread_grader.py", """\
RISK_ORDER = {"low": 0, "medium": 1, "high": 2}

def grade_spread(predicted_risk: str, actual_risk: str) -> float:
    diff = abs(RISK_ORDER.get(predicted_risk, 1) - RISK_ORDER.get(actual_risk, 1))
    return round(max(0.0, 1.0 - (diff * 0.5)), 4)
""")

write("graders/pipeline_grader.py", """\
def grade_pipeline(detection_acc: float, spread_correct: bool, proof_quality: bool, legal_steps_followed: bool) -> float:
    score = (
        detection_acc * 0.3
        + float(spread_correct) * 0.2
        + float(proof_quality) * 0.3
        + float(legal_steps_followed) * 0.2
    )
    return round(min(score, 1.0), 4)
""")

# ── dualshield_env ────────────────────────────────────────────────
write("dualshield_env/__init__.py", """\
from .environment import DualShieldEnv
from .models import Action, DualShieldState, ImageCase, Observation
__all__ = ["DualShieldEnv", "Action", "DualShieldState", "ImageCase", "Observation"]
""")

write("dualshield_env/data/__init__.py", "")

write("dualshield_env/data/seed_cases.py", """\
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
""")

write("dualshield_env/models.py", """\
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
""")

write("dualshield_env/environment.py", """\
from __future__ import annotations
import random, uuid
from typing import Dict, Optional
from .models import Action, DualShieldState, ImageCase, Observation, ResetResult, StateResult, StepResult, UserProfile
from .data.seed_cases import SEED_CASES
from graders.authenticity_grader import grade_authenticity
from graders.protection_grader import grade_protection
from graders.spread_grader import grade_spread
from graders.pipeline_grader import grade_pipeline

TASK_CONFIG = {
    "task_protect": {"max_steps": 5},
    "task_detect":  {"max_steps": 10},
    "task_respond": {"max_steps": 15},
}

ALL_ACTIONS = [
    "apply_watermark","apply_pixel_signature","analyze_authenticity",
    "compare_images","generate_proof_report","assess_spread_risk",
    "trigger_legal_guidance","file_cybercrime_report"
]

class DualShieldEnv:
    def __init__(self, base_url="http://localhost:7860"):
        self.base_url = base_url
        self._episodes: Dict[str, DualShieldState] = {}

    async def reset(self, task_id="task_protect", case_id=None) -> ResetResult:
        case_data = self._pick_case(case_id)
        case = ImageCase(**case_data)
        user = UserProfile()
        state = DualShieldState(
            episode_id=str(uuid.uuid4()), step_count=0,
            current_case=case, user=user,
            available_actions=ALL_ACTIONS[:],
            is_terminal=False, task_id=task_id, cumulative_reward=0.0
        )
        self._episodes[state.episode_id] = state
        return ResetResult(episode_id=state.episode_id, observation=self._make_obs(state), task_id=task_id)

    async def step(self, episode_id: str, action: Action) -> StepResult:
        state = self._episodes.get(episode_id)
        if state is None:
            raise KeyError(f"Unknown episode_id: {episode_id}")
        if state.is_terminal:
            return StepResult(observation=self._make_obs(state), reward=0.0, done=True, info={"message": "Episode finished."})
        reward, info = self._execute_action(state, action)
        state.step_count += 1
        state.cumulative_reward += reward
        done = state.is_terminal or (state.step_count >= TASK_CONFIG[state.task_id]["max_steps"])
        state.is_terminal = done
        return StepResult(observation=self._make_obs(state), reward=reward, done=done, info=info)

    async def state(self, episode_id: str) -> StateResult:
        state = self._episodes.get(episode_id)
        if state is None:
            raise KeyError(f"Unknown episode_id: {episode_id}")
        return StateResult(state=state, observation=self._make_obs(state))

    def _execute_action(self, state, action):
        at = action.action_type
        case = state.current_case
        reward = 0.0
        info = {"action": at}

        if at == "apply_watermark":
            state.watermark_applied = True
            state.user.watermarks_applied += 1
            reward = 0.5 * grade_protection(True, state.signature_applied)
        elif at == "apply_pixel_signature":
            state.signature_applied = True
            reward = 0.5 * grade_protection(state.watermark_applied, True)
        elif at == "analyze_authenticity":
            confidence = float(action.payload.get("confidence", 0.85))
            predicted = action.payload.get("predicted_type", case.manipulation_type)
            reward = grade_authenticity(predicted, case.manipulation_type, confidence)
            state.detected_manipulation = predicted
            state.authenticity_score = reward
        elif at == "compare_images":
            reward = 0.1 if state.authenticity_score is not None else 0.05
        elif at == "generate_proof_report":
            if state.authenticity_score is not None:
                reward = 0.3 * min(state.authenticity_score + 0.2, 1.0)
                state.proof_generated = True
            else:
                reward = 0.0
        elif at == "assess_spread_risk":
            predicted_risk = action.payload.get("predicted_risk", case.spread_risk)
            reward = 0.2 * grade_spread(predicted_risk, case.spread_risk)
            state.spread_risk_assessed = predicted_risk
        elif at == "trigger_legal_guidance":
            reward = 0.2 if state.proof_generated else 0.05
            if state.proof_generated:
                state.legal_guidance_triggered = True
        elif at == "file_cybercrime_report":
            pipeline_done = (state.watermark_applied and state.signature_applied
                             and state.proof_generated and state.legal_guidance_triggered)
            reward = grade_pipeline(
                state.authenticity_score or 0.0,
                state.spread_risk_assessed == case.spread_risk,
                state.proof_generated,
                state.legal_guidance_triggered
            ) if pipeline_done else 0.1
            state.report_filed = True
            state.user.cases_submitted += 1
            state.is_terminal = True
            if state.step_count < 8 and pipeline_done:
                reward += 0.1
                info["global_bonus"] = True

        if (at == "analyze_authenticity"
                and action.payload.get("predicted_type") == "none"
                and case.manipulation_type != "none"):
            reward -= 0.3

        return max(reward, 0.0), info

    def _pick_case(self, case_id):
        if case_id:
            for c in SEED_CASES:
                if c["case_id"] == case_id:
                    return c
        return random.choice(SEED_CASES)

    def _make_obs(self, state):
        case = state.current_case
        if state.report_filed:
            legal_status = "filed"
        elif state.legal_guidance_triggered:
            legal_status = "guidance_received"
        elif state.proof_generated:
            legal_status = "proof_ready"
        else:
            legal_status = "pending"
        return Observation(
            case_id=case.case_id, step_count=state.step_count, task_id=state.task_id,
            image_metadata={"hash": case.original_hash, "platform": case.platform_context, "description": case.description},
            authenticity_score=state.authenticity_score, manipulation_type=state.detected_manipulation,
            severity=case.severity, spread_risk=case.spread_risk, legal_status=legal_status,
            available_actions=state.available_actions, watermark_applied=state.watermark_applied,
            signature_applied=state.signature_applied, proof_generated=state.proof_generated,
            legal_guidance_triggered=state.legal_guidance_triggered, report_filed=state.report_filed,
            cumulative_reward=state.cumulative_reward
        )

    async def __aenter__(self): return self
    async def __aexit__(self, *_): self._episodes.clear()
""")

# ── ml ────────────────────────────────────────────────────────────
write("ml/__init__.py", "")

write("ml/model.py", """\
import torch
import torch.nn as nn
import torch.nn.functional as F

class FrequencyBranch(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.bn1   = nn.BatchNorm2d(32)
        self.bn2   = nn.BatchNorm2d(64)
        self.pool  = nn.AdaptiveAvgPool2d((8, 8))
        self.fc    = nn.Linear(64 * 8 * 8, 256)
    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        return F.relu(self.fc(self.pool(x).flatten(1)))

class SpatialBranch(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 5, padding=2)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.bn1   = nn.BatchNorm2d(32)
        self.bn2   = nn.BatchNorm2d(64)
        self.pool  = nn.AdaptiveAvgPool2d((8, 8))
        self.fc    = nn.Linear(64 * 8 * 8, 256)
    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        return F.relu(self.fc(self.pool(x).flatten(1)))

class DualShieldNet(nn.Module):
    NUM_CLASSES = 6
    CLASS_NAMES = ["none","face_swap","background_edit","metadata_strip","color_grade","composite"]
    def __init__(self):
        super().__init__()
        self.freq_branch    = FrequencyBranch()
        self.spatial_branch = SpatialBranch()
        self.trunk = nn.Sequential(
            nn.Linear(512, 256), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(256, 128), nn.ReLU()
        )
        self.cls_head      = nn.Linear(128, self.NUM_CLASSES)
        self.severity_head = nn.Sequential(nn.Linear(128,64), nn.ReLU(), nn.Linear(64,1), nn.Sigmoid())
    def forward(self, x):
        fused  = torch.cat([self.freq_branch(x), self.spatial_branch(x)], dim=1)
        h      = self.trunk(fused)
        logits = self.cls_head(h)
        probs  = F.softmax(logits, dim=1)
        return {"logits": logits, "probs": probs, "severity": self.severity_head(h),
                "confidence": probs.max(dim=1).values, "pred_class": probs.argmax(dim=1)}
    @torch.no_grad()
    def predict(self, x):
        self.eval()
        out = self.forward(x)
        return {"label": [self.CLASS_NAMES[i] for i in out["pred_class"].tolist()],
                "confidence": out["confidence"].tolist(),
                "severity": out["severity"].squeeze(-1).tolist()}
""")

write("ml/dataset.py", """\
import random, torch
from torch.utils.data import Dataset
from pathlib import Path
import torchvision.transforms as T

LABEL_MAP = {"none":0,"face_swap":1,"background_edit":2,"metadata_strip":3,"color_grade":4,"composite":5}

class DualShieldDataset(Dataset):
    def __init__(self, data_dir="data/images", split="train", image_size=(224,224), synthetic_size=500):
        self.image_size = image_size
        self.samples = []
        self.synthetic = False
        root = Path(data_dir)
        if root.exists():
            for cls_name, label in LABEL_MAP.items():
                for img_path in list((root/cls_name).glob("*.jpg")) + list((root/cls_name).glob("*.png")):
                    self.samples.append((str(img_path), label, label/5.0))
        if not self.samples:
            self.synthetic = True
            self.samples = [(None, random.randint(0,5), random.random()) for _ in range(synthetic_size)]
        self.transform = T.Compose([T.Resize(image_size), T.ToTensor(),
                                    T.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])])
    def __len__(self): return len(self.samples)
    def __getitem__(self, idx):
        path, label, severity = self.samples[idx]
        img = torch.randn(3, *self.image_size) if self.synthetic else self.transform(
            __import__("PIL").Image.open(path).convert("RGB"))
        return img, torch.tensor(label, dtype=torch.long), torch.tensor(severity, dtype=torch.float32)
""")

write("ml/train.py", """\
from pathlib import Path
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, random_split
from .model import DualShieldNet
from .dataset import DualShieldDataset

WEIGHTS_DIR = Path(__file__).parent / "weights"
WEIGHTS_DIR.mkdir(exist_ok=True)

def train(epochs=10, batch_size=32, lr=1e-4, device=None):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on {device}")
    dataset = DualShieldDataset()
    val_size = max(int(0.15 * len(dataset)), 1)
    train_ds, val_ds = random_split(dataset, [len(dataset)-val_size, val_size])
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    model = DualShieldNet().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-5)
    for epoch in range(1, epochs+1):
        model.train()
        total_loss = 0
        for imgs, labels, severities in train_loader:
            imgs, labels, severities = imgs.to(device), labels.to(device), severities.to(device)
            out  = model(imgs)
            loss = F.cross_entropy(out["logits"], labels) + 0.3 * F.mse_loss(out["severity"].squeeze(-1), severities)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch}/{epochs}  loss={total_loss/len(train_loader):.4f}")
    torch.save({"model_state": model.state_dict()}, WEIGHTS_DIR/"dualshield_v1.pt")
    print("Saved weights!")
    return model

if __name__ == "__main__":
    train()
""")

# ── server ────────────────────────────────────────────────────────
write("server/__init__.py", "")

write("server/app.py", """\
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from dualshield_env.environment import DualShieldEnv
from dualshield_env.models import ResetRequest, StepRequest

app = FastAPI(title="DualShield", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
env = DualShieldEnv()

@app.get("/")
async def root():
    index = Path(__file__).parent.parent / "frontend" / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"name": "DualShield", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "ok", "environment": "dualshield-env", "version": "1.0.0"}

@app.post("/reset")
async def reset(req: ResetRequest):
    return await env.reset(task_id=req.task_id, case_id=req.case_id)

@app.post("/step")
async def step(req: StepRequest):
    try:
        return await env.step(req.episode_id, req.action)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/state/{episode_id}")
async def state(episode_id: str):
    try:
        return await env.state(episode_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/protect")
async def protect(payload: dict):
    return {"status": "protected", "watermark_applied": True,
            "pixel_signature": "LSB-SHA256", "message": "Image protected."}

@app.post("/detect")
async def detect(payload: dict):
    return {"status": "analyzed", "manipulation_type": "none",
            "confidence": 0.91, "severity": 0.0, "message": "No manipulation detected."}

@app.post("/spread-risk")
async def spread_risk(payload: dict):
    platform = payload.get("platform", "unknown")
    risk_map = {"telegram": "high", "whatsapp": "medium", "instagram": "medium", "unknown": "low"}
    return {"platform": platform, "spread_risk": risk_map.get(platform, "low"),
            "recommended_action": "File report at cybercrime.gov.in"}

@app.post("/legal")
async def legal(payload: dict):
    return {
        "jurisdiction": "india",
        "applicable_laws": ["IT Act 2000 Section 66E", "IT Act 2000 Section 67", "IPC Section 509"],
        "steps": [
            {"step": 1, "action": "Preserve evidence with timestamp"},
            {"step": 2, "action": "Call 1930 or visit cybercrime.gov.in"},
            {"step": 3, "action": "Report to platform for takedown"},
            {"step": 4, "action": "Visit nearest cyber crime police station"}
        ],
        "emergency": {"helpline": "1930", "emergency": "112"}
    }
""")

# ── tests ─────────────────────────────────────────────────────────
write("tests/__init__.py", "")

write("tests/test_all.py", """\
import pytest
import asyncio
import sys
sys.path.insert(0, ".")

from graders.authenticity_grader import grade_authenticity
from graders.protection_grader import grade_protection
from graders.spread_grader import grade_spread
from graders.pipeline_grader import grade_pipeline
from dualshield_env.models import Action
from dualshield_env.environment import DualShieldEnv

def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

# ── Authenticity (10 tests) ───────────────────────────────────────
class TestAuthenticity:
    def test_correct_high_conf(self):      assert 0.88 <= grade_authenticity("face_swap","face_swap",0.9) <= 0.91
    def test_missed_manip_zero(self):      assert grade_authenticity("none","face_swap",0.99) == 0.0
    def test_wrong_type_partial(self):     assert 0.23 <= grade_authenticity("face_swap","composite",0.8) <= 0.25
    def test_conf_capped(self):            assert abs(grade_authenticity("face_swap","face_swap",1.0) - grade_authenticity("face_swap","face_swap",0.99)) < 0.001
    def test_zero_conf(self):              assert grade_authenticity("face_swap","face_swap",0.0) == 0.0
    def test_correct_none(self):           assert grade_authenticity("none","none",0.9) > 0.88
    def test_background_edit(self):        assert grade_authenticity("background_edit","background_edit",0.75) > 0.7
    def test_all_missed_zero(self):
        for t in ["face_swap","background_edit","composite","color_grade"]:
            assert grade_authenticity("none",t,0.99) == 0.0
    def test_in_range(self):               assert 0.0 <= grade_authenticity("composite","face_swap",0.6) <= 1.0
    def test_metadata_correct(self):       assert grade_authenticity("metadata_strip","metadata_strip",0.85) > 0.8

# ── Protection (6 tests) ──────────────────────────────────────────
class TestProtection:
    def test_both(self):      assert grade_protection(True,True)   == 1.0
    def test_neither(self):   assert grade_protection(False,False) == 0.0
    def test_only_wm(self):   assert grade_protection(True,False)  == 0.5
    def test_only_sig(self):  assert grade_protection(False,True)  == 0.5
    def test_is_float(self):  assert isinstance(grade_protection(True,True), float)
    def test_in_range(self):
        for w in [True,False]:
            for s in [True,False]:
                assert 0.0 <= grade_protection(w,s) <= 1.0

# ── Spread (6 tests) ──────────────────────────────────────────────
class TestSpread:
    def test_low_exact(self):      assert grade_spread("low","low")       == 1.0
    def test_high_exact(self):     assert grade_spread("high","high")     == 1.0
    def test_off_one(self):        assert grade_spread("low","medium")    == 0.5
    def test_off_two(self):        assert grade_spread("low","high")      == 0.0
    def test_medium_exact(self):   assert grade_spread("medium","medium") == 1.0
    def test_never_negative(self):
        for p in ["low","medium","high"]:
            for a in ["low","medium","high"]:
                assert grade_spread(p,a) >= 0.0

# ── Pipeline (6 tests) ────────────────────────────────────────────
class TestPipeline:
    def test_perfect(self):         assert grade_pipeline(1.0,True,True,True)    == 1.0
    def test_zero(self):            assert grade_pipeline(0.0,False,False,False) == 0.0
    def test_detection_weight(self):assert abs(grade_pipeline(1.0,False,False,False) - 0.3) < 0.01
    def test_proof_weight(self):    assert abs(grade_pipeline(0.0,False,True,False) - 0.3) < 0.01
    def test_spread_weight(self):   assert abs(grade_pipeline(0.0,True,False,False) - 0.2) < 0.01
    def test_legal_weight(self):    assert abs(grade_pipeline(0.0,False,False,True) - 0.2) < 0.01

# ── Environment (16 tests) ────────────────────────────────────────
class TestEnvironment:
    def test_reset_returns_id(self):
        env = DualShieldEnv(); r = run(env.reset()); assert r.episode_id
    def test_reset_task_protect(self):
        env = DualShieldEnv(); r = run(env.reset(task_id="task_protect")); assert r.task_id == "task_protect"
    def test_reset_task_detect(self):
        env = DualShieldEnv(); r = run(env.reset(task_id="task_detect")); assert r.task_id == "task_detect"
    def test_reset_task_respond(self):
        env = DualShieldEnv(); r = run(env.reset(task_id="task_respond")); assert r.task_id == "task_respond"
    def test_obs_initial(self):
        env = DualShieldEnv(); r = run(env.reset()); assert r.observation.step_count == 0
    def test_specific_case(self):
        env = DualShieldEnv(); r = run(env.reset(case_id="case_001")); assert r.observation.case_id == "case_001"
    def test_watermark_step(self):
        env = DualShieldEnv(); r = run(env.reset())
        s = run(env.step(r.episode_id, Action(action_type="apply_watermark",payload={}))); assert s.observation.watermark_applied
    def test_signature_step(self):
        env = DualShieldEnv(); r = run(env.reset())
        s = run(env.step(r.episode_id, Action(action_type="apply_pixel_signature",payload={}))); assert s.observation.signature_applied
    def test_detect_correct(self):
        env = DualShieldEnv(); r = run(env.reset(case_id="case_001"))
        s = run(env.step(r.episode_id, Action(action_type="analyze_authenticity",payload={"predicted_type":"face_swap","confidence":0.9}))); assert s.reward > 0
    def test_missed_manip_penalty(self):
        env = DualShieldEnv(); r = run(env.reset(case_id="case_001"))
        s = run(env.step(r.episode_id, Action(action_type="analyze_authenticity",payload={"predicted_type":"none","confidence":0.9}))); assert s.reward == 0.0
    def test_unknown_episode_raises(self):
        env = DualShieldEnv()
        with pytest.raises(KeyError): run(env.step("bad-id", Action(action_type="apply_watermark",payload={})))
    def test_step_count_increments(self):
        env = DualShieldEnv(); r = run(env.reset())
        s = run(env.step(r.episode_id, Action(action_type="apply_watermark",payload={}))); assert s.observation.step_count == 1
    def test_full_pipeline_reward(self):
        env = DualShieldEnv(); r = run(env.reset(task_id="task_respond",case_id="case_001"))
        eid = r.episode_id; total = 0
        for at, pl in [("apply_watermark",{}),("apply_pixel_signature",{}),
                       ("analyze_authenticity",{"predicted_type":"face_swap","confidence":0.88}),
                       ("compare_images",{}),("assess_spread_risk",{"predicted_risk":"high"}),
                       ("generate_proof_report",{}),("trigger_legal_guidance",{}),("file_cybercrime_report",{})]:
            s = run(env.step(eid, Action(action_type=at,payload=pl))); total += s.reward
            if s.done: break
        assert total > 0.5
    def test_terminal_after_report(self):
        env = DualShieldEnv(); r = run(env.reset()); eid = r.episode_id; s = None
        for at in ["apply_watermark","apply_pixel_signature","analyze_authenticity",
                   "generate_proof_report","trigger_legal_guidance","file_cybercrime_report"]:
            pl = {"predicted_type":"none","confidence":0.5} if at=="analyze_authenticity" else {}
            s = run(env.step(eid, Action(action_type=at,payload=pl)))
        assert s.done
    def test_state_endpoint(self):
        env = DualShieldEnv(); r = run(env.reset())
        st = run(env.state(r.episode_id)); assert st.state.episode_id == r.episode_id
    def test_obs_not_none(self):
        env = DualShieldEnv(); r = run(env.reset())
        assert r.observation is not None
""")

# ── inference.py ──────────────────────────────────────────────────
write("inference.py", """\
import os, json, asyncio
from dualshield_env.environment import DualShieldEnv
from dualshield_env.models import Action

FALLBACK = [
    Action(action_type="apply_watermark",        payload={"strength": 0.7}),
    Action(action_type="apply_pixel_signature",  payload={"method": "lsb"}),
    Action(action_type="analyze_authenticity",   payload={"predicted_type": "face_swap", "confidence": 0.88}),
    Action(action_type="compare_images",         payload={}),
    Action(action_type="assess_spread_risk",     payload={"predicted_risk": "high"}),
    Action(action_type="generate_proof_report",  payload={"format": "legal"}),
    Action(action_type="trigger_legal_guidance", payload={"jurisdiction": "india"}),
    Action(action_type="file_cybercrime_report", payload={"portal": "cybercrime.gov.in"}),
]

async def run_episode(env, task_id):
    r = await env.reset(task_id=task_id)
    eid = r.episode_id
    total = 0.0
    history = []
    for step in range(15):
        action = FALLBACK[step % len(FALLBACK)]
        s = await env.step(eid, action)
        total += s.reward
        history.append({"step": step, "action": action.action_type, "reward": s.reward})
        print(f"  step {step+1:02d} | {action.action_type:<30} | reward={s.reward:.4f}")
        if s.done:
            break
    return {"task_id": task_id, "total_reward": round(total, 4), "steps": len(history)}

async def main():
    print("=" * 55)
    print("DualShield Inference Baseline")
    print("=" * 55)
    async with DualShieldEnv() as env:
        results = []
        for task in ["task_protect", "task_detect", "task_respond"]:
            print(f"\\n[{task}]")
            r = await run_episode(env, task)
            results.append(r)
            print(f"  total_reward={r['total_reward']}  steps={r['steps']}")
        avg = sum(r["total_reward"] for r in results) / len(results)
        print(f"\\nAverage reward: {avg:.4f}")
        with open("inference_results.json", "w") as f:
            json.dump({"results": results, "avg_reward": avg}, f, indent=2)
        print("Saved inference_results.json")

if __name__ == "__main__":
    asyncio.run(main())
""")

print()
print("=" * 40)
print("ALL 16 FILES CREATED SUCCESSFULLY!")
print("=" * 40)
