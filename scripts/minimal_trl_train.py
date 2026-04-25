from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from env import AssistantAction, ExecutiveAssistantEnv
from inference import heuristic_policy


PROMPT_TEMPLATE = """You are an executive assistant operating inside an OpenEnv environment.
Return only JSON with these fields:
- thread_id
- decision
- priority
- target_person
- chosen_slot
- rationale
- message

Current scenario: {title}
Objective: {objective}
Step: {step_index}/{total_steps}
Current thread:
- id: {thread_id}
- sender: {sender} ({sender_role})
- subject: {subject}
- body: {body}
- visible_constraints: {visible_constraints}
- social_risk: {social_risk}
- asks: {asks}

Available slots: {slots}
Delegates: {delegates}
Stakeholder hints: {hints}
Outstanding conflicts: {conflicts}
Completed threads: {completed}
Last outcome: {last_outcome}
"""


def format_prompt(observation) -> str:
    slots = ", ".join(
        f"{slot.slot_id}:{slot.label}:{'free' if slot.available else 'booked'}"
        for slot in observation.available_slots
    )
    delegates = ", ".join(
        f"{delegate.name}({delegate.role}, cap={delegate.capacity_remaining})"
        for delegate in observation.delegates
    )
    hints = "; ".join(
        f"{hint.name}/{hint.role}: {hint.preference_hint}"
        for hint in observation.stakeholder_hints
    )
    return PROMPT_TEMPLATE.format(
        title=observation.title,
        objective=observation.objective,
        step_index=observation.step_index + 1,
        total_steps=observation.total_steps,
        thread_id=observation.current_thread.thread_id,
        sender=observation.current_thread.sender,
        sender_role=observation.current_thread.sender_role,
        subject=observation.current_thread.subject,
        body=observation.current_thread.body,
        visible_constraints=", ".join(observation.current_thread.visible_constraints),
        social_risk=observation.current_thread.social_risk,
        asks=", ".join(observation.current_thread.asks),
        slots=slots,
        delegates=delegates,
        hints=hints,
        conflicts=", ".join(observation.outstanding_conflicts) or "none",
        completed=", ".join(observation.completed_threads) or "none",
        last_outcome=observation.last_outcome,
    )


def build_dataset_rows(repeats_per_scenario: int = 8) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    scenarios = ["board_crunch", "launch_week"]

    for scenario_id in scenarios:
        for seed in range(repeats_per_scenario):
            env = ExecutiveAssistantEnv()
            observation = env.reset(seed=seed, scenario_id=scenario_id)
            prefix_actions: List[Dict[str, Any]] = []

            while not observation.done:
                rows.append(
                    {
                        "prompt": format_prompt(observation),
                        "scenario_id": scenario_id,
                        "seed": seed,
                        "prefix_actions": list(prefix_actions),
                    }
                )
                action = heuristic_policy(observation)
                prefix_actions.append(action.model_dump())
                observation = env.step(action)

    return rows


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
    except ImportError as exc:
        raise SystemExit(
            "Install training extras first: pip install datasets transformers accelerate trl peft"
        ) from exc

    rows = build_dataset_rows()
    dataset = Dataset.from_list(rows)

    config = GRPOConfig(
        output_dir=str(ROOT / "outputs" / "trl_run"),
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        max_prompt_length=1024,
        max_completion_length=220,
        num_generations=4,
        logging_steps=1,
        save_steps=25,
        num_train_epochs=1,
        report_to=[],
    )

    trainer = GRPOTrainer(
        model="Qwen/Qwen2.5-0.5B-Instruct",
        args=config,
        train_dataset=dataset,
        reward_funcs=[json_format_reward, env_reward],
    )
    trainer.train()


if __name__ == "__main__":
    main()

