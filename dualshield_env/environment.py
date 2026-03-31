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
