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
            print(f"\n[{task}]")
            r = await run_episode(env, task)
            results.append(r)
            print(f"  total_reward={r['total_reward']}  steps={r['steps']}")
        avg = sum(r["total_reward"] for r in results) / len(results)
        print(f"\nAverage reward: {avg:.4f}")
        with open("inference_results.json", "w") as f:
            json.dump({"results": results, "avg_reward": avg}, f, indent=2)
        print("Saved inference_results.json")

if __name__ == "__main__":
    asyncio.run(main())
