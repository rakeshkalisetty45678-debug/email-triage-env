from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from env import AssistantAction, ExecutiveAssistantEnv
from scripts.training_data import build_rollout_rows


def _extract_completion_text(completion: Any) -> str:
    if isinstance(completion, str):
        return completion
    if isinstance(completion, list):
        if completion and isinstance(completion[0], dict):
            return completion[-1].get("content", "")
        if completion:
            return str(completion[-1])
    if isinstance(completion, dict):
        return str(completion.get("content", ""))
    return str(completion)


def _extract_json_block(text: str) -> str:
    fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    raw = re.search(r"(\{.*\})", text, flags=re.DOTALL)
    if raw:
        return raw.group(1)
    return text


def _parse_action(text: str) -> AssistantAction | None:
    try:
        payload = json.loads(_extract_json_block(text))
        return AssistantAction.model_validate(payload)
    except Exception:
        return None


def json_format_reward(completions, **kwargs):
    rewards = []
    for completion in completions:
        rewards.append(1.0 if _parse_action(_extract_completion_text(completion)) else 0.0)
    return rewards


def env_reward(completions, scenario_id, seed, prefix_actions, **kwargs):
    rewards = []
    for completion, scenario_id_i, seed_i, prefix_i in zip(
        completions, scenario_id, seed, prefix_actions
    ):
        action = _parse_action(_extract_completion_text(completion))
        if action is None:
            rewards.append(0.0)
            continue

        env = ExecutiveAssistantEnv()
        observation = env.reset(seed=int(seed_i), scenario_id=scenario_id_i)
        for logged_action in prefix_i:
            observation = env.step(AssistantAction.model_validate(logged_action))
        if action.thread_id != observation.current_thread.thread_id:
            rewards.append(0.0)
            continue
        next_observation = env.step(action)
        rewards.append(float(next_observation.reward or 0.0))
    return rewards


def main() -> None:
    try:
        from datasets import Dataset
        from trl import GRPOConfig, GRPOTrainer
        import torch
    except ImportError as exc:
        raise SystemExit(
            "Install training extras first: pip install datasets transformers accelerate trl peft"
        ) from exc

    repeats = int(os.getenv("TRL_REPEATS_PER_SCENARIO", "8"))
    rows = build_rollout_rows(repeats_per_scenario=repeats)
    dataset = Dataset.from_list(rows)
    use_cpu = not torch.cuda.is_available()
    model_name = os.getenv("TRL_MODEL_NAME", "Qwen/Qwen2.5-0.5B-Instruct")

    config = GRPOConfig(
        output_dir=str(ROOT / "outputs" / "trl_run"),
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        max_completion_length=220,
        num_generations=4,
        logging_steps=1,
        save_steps=25,
        num_train_epochs=1,
        do_train=True,
        use_cpu=use_cpu,
        report_to="none",
        learning_rate=1e-6,
        save_strategy="steps",
        logging_strategy="steps",
        remove_unused_columns=False,
    )

    trainer = GRPOTrainer(
        model=model_name,
        args=config,
        train_dataset=dataset,
        reward_funcs=[json_format_reward, env_reward],
    )
    trainer.train()


if __name__ == "__main__":
    main()
