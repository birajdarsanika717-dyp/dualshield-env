from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import random

app = FastAPI(title="DualShield Environment")

class DualShieldAction(BaseModel):
    task_id: int
    answer: str
    confidence: float

class DualShieldObservation(BaseModel):
    task_id: int
    scenario: str
    options: List[str]
    done: bool
    reward: float

class DualShieldState(BaseModel):
    episode_id: str
    step_count: int
    current_task: int

class DualShieldEnvironment:
    def __init__(self):
        self.current_task = 1
        self.step_count = 0
        self.episode_id = str(random.randint(1000, 9999))

    def reset(self):
        self.current_task = 1
        self.step_count = 0
        self.episode_id = str(random.randint(1000, 9999))
        return DualShieldObservation(
            task_id=1,
            scenario="Ek image upload ki gayi hai. Face blurry hai, background alag lag raha hai.",
            options=["REAL", "FAKE"],
            done=False,
            reward=0.0
        )

    def step(self, action: DualShieldAction):
        self.step_count += 1
        reward = 0.0
        if self.current_task == 1:
            if action.answer.upper() == "FAKE":
                reward = 1.0
            self.current_task = 2
            return DualShieldObservation(
                task_id=2,
                scenario="Photo Instagram pe public account pe share ki gayi hai. 5000 followers hain.",
                options=["HIGH", "MEDIUM", "LOW"],
                done=False,
                reward=reward
            )
        elif self.current_task == 2:
            if action.answer.upper() == "HIGH":
                reward = 1.0
            elif action.answer.upper() == "MEDIUM":
                reward = 0.5
            self.current_task = 3
            return DualShieldObservation(
                task_id=3,
                scenario="Meri edited photo WhatsApp groups mein share ho rahi hai.",
                options=["EVIDENCE_COLLECT", "CYBER_COMPLAINT", "IGNORE"],
                done=False,
                reward=reward
            )
        elif self.current_task == 3:
            if action.answer.upper() == "CYBER_COMPLAINT":
                reward = 1.0
            elif action.answer.upper() == "EVIDENCE_COLLECT":
                reward = 0.6
            return DualShieldObservation(
                task_id=3,
                scenario="Episode complete!",
                options=[],
                done=True,
                reward=reward
            )

    def state(self):
        return DualShieldState(
            episode_id=self.episode_id,
            step_count=self.step_count,
            current_task=self.current_task
        )

env = DualShieldEnvironment()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.dict()

@app.post("/step")
def step(action: DualShieldAction):
    obs = env.step(action)
    return obs.dict()

@app.get("/state")
def state():
    return env.state().dict()
