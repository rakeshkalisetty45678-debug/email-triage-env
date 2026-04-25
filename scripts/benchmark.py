from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from statistics import mean

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from env import AssistantAction, ExecutiveAssistantEnv
from inference import heuristic_policy

EVAL_DIR = ROOT / "outputs" / "evals"
PLOT_PATH = ROOT / "reward_curve.png"
JSON_PATH = EVAL_DIR / "baseline_metrics.json"


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
        rationale="A random baseline with no strategic model of the stakeholders.",
        message="This is a random placeholder message.",
    )


def run_episode(policy_name: str, scenario_id: str, seed: int) -> float:
    rng = random.Random(seed)
    env = ExecutiveAssistantEnv()
    observation = env.reset(seed=seed, scenario_id=scenario_id)
    rewards = []

    while not observation.done:
        if policy_name == "heuristic":
            action = heuristic_policy(observation)
        else:
            action = random_policy(observation, rng)
        observation = env.step(action)
        rewards.append(float(observation.reward or 0.0))

    return mean(rewards) if rewards else 0.0


def build_metrics(num_runs: int = 24) -> dict:
    scenarios = ["board_crunch", "launch_week"]
    series = {"random": [], "heuristic": []}

    for policy_name in series:
        for run_idx in range(num_runs):
            scenario_id = scenarios[run_idx % len(scenarios)]
            score = run_episode(policy_name, scenario_id, seed=run_idx + 11)
            series[policy_name].append(round(score, 4))

    return {
        "num_runs": num_runs,
        "random_mean": round(mean(series["random"]), 4),
        "heuristic_mean": round(mean(series["heuristic"]), 4),
        "random_series": series["random"],
        "heuristic_series": series["heuristic"],
    }


def draw_plot(metrics: dict) -> None:
    width, height = 1000, 560
    margin_left, margin_right, margin_top, margin_bottom = 90, 40, 50, 80
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    image = Image.new("RGB", (width, height), "#fbfaf7")
    draw = ImageDraw.Draw(image)

    axis_color = "#1f2937"
    random_color = "#c2410c"
    heuristic_color = "#0f766e"
    grid_color = "#d6d3d1"

    draw.text((margin_left, 15), "Executive Assistant Env: Random vs Heuristic Reward", fill=axis_color)

    for tick in range(6):
        y = margin_top + int(plot_h * tick / 5)
        draw.line((margin_left, y, width - margin_right, y), fill=grid_color, width=1)
        label = f"{1 - tick * 0.2:.1f}"
        draw.text((20, y - 8), label, fill=axis_color)

    draw.line((margin_left, margin_top, margin_left, height - margin_bottom), fill=axis_color, width=2)
    draw.line((margin_left, height - margin_bottom, width - margin_right, height - margin_bottom), fill=axis_color, width=2)

    def to_points(values):
        if len(values) == 1:
            return [(margin_left, height - margin_bottom)]
        points = []
        for idx, value in enumerate(values):
            x = margin_left + int(plot_w * idx / (len(values) - 1))
            y = margin_top + int((1 - value) * plot_h)
            points.append((x, y))
        return points

    random_points = to_points(metrics["random_series"])
    heuristic_points = to_points(metrics["heuristic_series"])
    draw.line(random_points, fill=random_color, width=4)
    draw.line(heuristic_points, fill=heuristic_color, width=4)

    draw.text((width - 270, 65), "Random baseline", fill=random_color)
    draw.text((width - 270, 90), "Rule-based policy", fill=heuristic_color)
    draw.text((margin_left + 320, height - 40), "Evaluation episode", fill=axis_color)
    draw.text((12, margin_top - 10), "Reward", fill=axis_color)

    image.save(PLOT_PATH)


def main() -> None:
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    metrics = build_metrics()
    JSON_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    draw_plot(metrics)
    print(json.dumps(metrics, indent=2))
    print(f"Wrote {PLOT_PATH}")


if __name__ == "__main__":
    main()
