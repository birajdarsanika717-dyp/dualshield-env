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
    return asyncio.run(coro)

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
