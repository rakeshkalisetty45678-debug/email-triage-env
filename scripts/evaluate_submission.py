from __future__ import annotations

import json
import os
import random
import re
import sys
from pathlib import Path
from statistics import mean
from typing import Callable, Dict, List

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("OPENENV_LIGHT_MODE", "1")

from env import AssistantAction, ExecutiveAssistantEnv
from inference import heuristic_policy
from scripts.training_data import format_prompt

OUT_DIR = ROOT / "outputs" / "submission_eval"
METRICS_PATH = OUT_DIR / "submission_metrics.json"
PLOT_PATH = OUT_DIR / "submission_reward_comparison.png"
BEHAVIOR_PATH = OUT_DIR / "behavior_examples.json"


def random_policy(observation, rng: random.Random) -> AssistantAction:
    slots = [slot.slot_id for slot in observation.available_slots if slot.available]
    delegates = [delegate.name for delegate in observation.delegates if delegate.capacity_remaining > 0]
    decision = rng.choice(["reply", "delegate", "schedule", "decline", "clarify", "archive"])
    return AssistantAction(
        thread_id=observation.current_thread.thread_id,
        decision=decision,
        priority=rng.choice(["critical", "high", "medium", "low"]),
        target_person=rng.choice(delegates) if delegates and decision == "delegate" else None,
        chosen_slot=rng.choice(slots) if slots and decision == "schedule" else None,
        rationale="This baseline acts without modeling the stakeholder tradeoffs.",
        message="Random placeholder response.",
    )


def _extract_json(text: str) -> str:
    fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    raw = re.search(r"(\{.*\})", text, flags=re.DOTALL)
    if raw:
        return raw.group(1)
    return text


def _load_generation_policy(model_path: str) -> Callable:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()

    def policy(observation):
        prompt = format_prompt(observation)
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=180,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True)
        try:
            payload = json.loads(_extract_json(text))
            payload.setdefault("thread_id", observation.current_thread.thread_id)
            return AssistantAction.model_validate(payload)
        except Exception:
            return AssistantAction(
                thread_id=observation.current_thread.thread_id,
                decision="clarify",
                priority="medium",
                rationale="Fallback because the model output was not valid JSON.",
                message="I need one more detail before I commit executive time.",
            )

    return policy


def run_policy(policy_name: str, policy_fn: Callable, runs: int = 12) -> Dict:
    scenarios = ["board_crunch", "launch_week"]
    series: List[float] = []
    examples: List[Dict] = []

    for run_idx in range(runs):
        seed = run_idx + 101
        scenario_id = scenarios[run_idx % len(scenarios)]
        env = ExecutiveAssistantEnv()
        observation = env.reset(seed=seed, scenario_id=scenario_id)
        rewards = []
        actions = []
        rng = random.Random(seed)

        while not observation.done:
            if policy_name == "random":
                action = random_policy(observation, rng)
            else:
                action = policy_fn(observation)
            actions.append(action.model_dump())
            observation = env.step(action)
            rewards.append(float(observation.reward or 0.0))

        series.append(round(mean(rewards), 4))
        if run_idx < 2:
            examples.append(
                {
                    "scenario_id": scenario_id,
                    "seed": seed,
                    "mean_reward": round(mean(rewards), 4),
                    "actions": actions,
                    "final_state": env.state.model_dump(),
                }
            )

    return {
        "mean_reward": round(mean(series), 4),
        "series": series,
        "examples": examples,
    }


def draw_bar_plot(metrics: Dict) -> None:
    width, height = 1100, 640
    image = Image.new("RGB", (width, height), "#fbfaf7")
    draw = ImageDraw.Draw(image)
    axis_color = "#1f2937"
    grid_color = "#d6d3d1"
    colors = {
        "random": "#b45309",
        "base_model": "#475569",
        "trained_model": "#0f766e",
        "heuristic": "#1d4ed8",
    }
    bars = [
        ("random", metrics["random"]["mean_reward"]),
        ("base_model", metrics["base_model"]["mean_reward"]),
        ("trained_model", metrics["trained_model"]["mean_reward"]),
        ("heuristic", metrics["heuristic"]["mean_reward"]),
    ]

    margin_left, margin_bottom, margin_top = 120, 110, 70
    chart_height = height - margin_top - margin_bottom
    baseline_y = height - margin_bottom

    draw.text((margin_left, 25), "Executive Assistant Env: Before/After Reward Comparison", fill=axis_color)

    for tick in range(6):
        y = margin_top + int(chart_height * tick / 5)
        draw.line((margin_left, y, width - 60, y), fill=grid_color, width=1)
        draw.text((35, y - 8), f"{1 - tick * 0.2:.1f}", fill=axis_color)

    bar_width = 140
    gap = 90
    x = margin_left + 40
    for label, value in bars:
        bar_height = int(chart_height * value)
        y0 = baseline_y - bar_height
        draw.rectangle((x, y0, x + bar_width, baseline_y), fill=colors[label])
        draw.text((x, baseline_y + 15), label.replace("_", " "), fill=axis_color)
        draw.text((x + 20, y0 - 25), f"{value:.3f}", fill=axis_color)
        x += bar_width + gap

    draw.text((width // 2 - 100, height - 45), "Policy variant", fill=axis_color)
    draw.text((15, margin_top - 10), "Mean reward", fill=axis_color)
    image.save(PLOT_PATH)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base_model_path = str(ROOT / "outputs" / "sft_run" / "final_model")
    if not Path(base_model_path).exists():
        raise SystemExit(
            "Trained model not found. Run: python scripts\\train_sft_submission.py"
        )

    fast_local = Path(base_model_path, "adapter_config.json").exists() or (
        os.getenv("FAST_LOCAL_TRAIN", "1") == "1"
    )
    base_name = os.getenv(
        "EVAL_BASE_MODEL_NAME",
        "sshleifer/tiny-gpt2" if fast_local else "Qwen/Qwen2.5-0.5B-Instruct",
    )
    base_policy = _load_generation_policy(base_name)
    trained_policy = _load_generation_policy(base_model_path)

    metrics = {
        "random": run_policy("random", heuristic_policy),
        "base_model": run_policy("base_model", base_policy),
        "trained_model": run_policy("trained_model", trained_policy),
        "heuristic": run_policy("heuristic", heuristic_policy),
    }

    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    BEHAVIOR_PATH.write_text(
        json.dumps(
            {
                "base_model_examples": metrics["base_model"]["examples"],
                "trained_model_examples": metrics["trained_model"]["examples"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    draw_bar_plot(metrics)
    print(json.dumps({k: v["mean_reward"] for k, v in metrics.items()}, indent=2))
    print(f"Wrote {PLOT_PATH}")


if __name__ == "__main__":
    main()
