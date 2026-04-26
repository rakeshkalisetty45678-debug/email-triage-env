from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("OPENENV_LIGHT_MODE", "1")

from env import ExecutiveAssistantEnv
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


def build_rollout_rows(repeats_per_scenario: int = 8) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    scenarios = ["board_crunch", "launch_week"]

    for scenario_id in scenarios:
        for seed in range(repeats_per_scenario):
            env = ExecutiveAssistantEnv()
            observation = env.reset(seed=seed, scenario_id=scenario_id)
            prefix_actions: List[Dict[str, Any]] = []

            while not observation.done:
                action = heuristic_policy(observation)
                rows.append(
                    {
                        "prompt": format_prompt(observation),
                        "completion": json.dumps(action.model_dump(), ensure_ascii=True),
                        "scenario_id": scenario_id,
                        "seed": seed,
                        "prefix_actions": list(prefix_actions),
                    }
                )
                prefix_actions.append(action.model_dump())
                observation = env.step(action)

    return rows


def build_sft_text_rows(repeats_per_scenario: int = 8) -> List[Dict[str, str]]:
    rows = build_rollout_rows(repeats_per_scenario=repeats_per_scenario)
    return [{"text": f"{row['prompt']}\n{row['completion']}"} for row in rows]
