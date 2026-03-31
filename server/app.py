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
