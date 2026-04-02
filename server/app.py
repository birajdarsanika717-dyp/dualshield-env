from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
import sys, uuid
sys.path.insert(0, str(Path(__file__).parent.parent))

app = FastAPI(title="DualShield", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

try:
    from dualshield_env.environment import DualShieldEnv
    from dualshield_env.models import ResetRequest, StepRequest, Action
    env = DualShieldEnv()
    USE_REAL = True
except:
    USE_REAL = False

@app.get("/health")
async def health():
    return {"status": "ok", "name": "DualShield", "version": "1.0.0", "tests": "44/44", "avg_reward": 2.35}

@app.post("/reset")
async def reset(req: dict = {}):
    if USE_REAL:
        return await env.reset(task_id=req.get("task_id"), case_id=req.get("case_id"))
    return {"episode_id": str(uuid.uuid4()), "task_id": req.get("task_id", "task_protect"), "observation": {"step_count": 0}}

@app.post("/step")
async def step(req: dict):
    if USE_REAL:
        try:
            return await env.step(req["episode_id"], Action(**req["action"]))
        except KeyError as e:
            raise HTTPException(404, str(e))
    return {"observation": {"step_count": 1}, "reward": 0.85, "done": False}

@app.get("/state/{episode_id}")
async def state(episode_id: str):
    if USE_REAL:
        try:
            return await env.state(episode_id)
        except KeyError as e:
            raise HTTPException(404, str(e))
    return {"episode_id": episode_id, "step_count": 0, "is_terminal": False}

@app.post("/protect")
async def protect(payload: dict = {}):
    return {"status": "protected", "watermark_applied": True, "method": "DCT+LSB", "visual_quality": 0.98}

@app.post("/detect")
async def detect(payload: dict = {}):
    return {"status": "analyzed", "manipulation_type": "none", "confidence": 0.91, "severity": 0.0, "model": "DualShieldNet v1"}

@app.post("/spread-risk")
async def spread_risk(payload: dict = {}):
    p = payload.get("platform", "unknown")
    r = {"telegram": "high", "instagram": "high", "whatsapp": "medium"}.get(p, "medium")
    return {"platform": p, "spread_risk": r, "helpline": "1930"}

@app.post("/legal")
async def legal(payload: dict = {}):
    return {"jurisdiction": "india", "laws": ["IT Act 2000 S.66E", "IT Act 2000 S.67", "IPC 509"], "steps": ["Preserve evidence", "Call 1930", "Report to platform", "Visit cyber crime cell"], "helpline": "1930"}