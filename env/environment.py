from __future__ import annotations

import copy
import random
import uuid
from typing import Any, Dict, List, Optional

from env.graders import build_rubric, clamp_score
from env.models import (
    AssistantAction,
    AssistantObservation,
    AssistantState,
    CalendarSlot,
    DelegateStatus,
    StakeholderHint,
    ThreadContext,
    ThreadOutcome,
)
from env.openenv_compat import Environment, EnvironmentMetadata
from env.tasks import SCENARIOS


class ExecutiveAssistantEnv(
    Environment[AssistantAction, AssistantObservation, AssistantState]
):
    SUPPORTS_CONCURRENT_SESSIONS = False

    def __init__(self, scenario_id: Optional[str] = None):
        super().__init__(rubric=build_rubric())
        self._rng = random.Random()
        self._requested_scenario_id = scenario_id
        self._scenario_id = scenario_id or "board_crunch"
        self._scenario: Dict[str, Any] = {}
        self._threads: List[Dict[str, Any]] = []
        self._thread_index = 0
        self._calendar_slots: List[Dict[str, Any]] = []
        self._delegates: Dict[str, Dict[str, Any]] = {}
        self._resolved_threads: List[str] = []
        self._conflicts: List[str] = []
        self._last_outcome = "Episode started."
        self._episode_id: Optional[str] = None
        self._cumulative_reward = 0.0
        self._protected_commitments = True

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AssistantObservation:
        self._reset_rubric()
        if seed is not None:
            self._rng.seed(seed)

        chosen = scenario_id or self._requested_scenario_id
        if chosen is None:
            chosen = self._rng.choice(sorted(SCENARIOS))
        self._scenario_id = chosen
        self._scenario = copy.deepcopy(SCENARIOS[chosen])
        self._threads = self._scenario["threads"]
        self._thread_index = 0
        self._calendar_slots = copy.deepcopy(self._scenario["calendar_slots"])
        self._delegates = {
            delegate["name"]: copy.deepcopy(delegate) for delegate in self._scenario["delegates"]
        }
        self._resolved_threads = []
        self._conflicts = []
        self._last_outcome = "Episode started."
        self._episode_id = episode_id or str(uuid.uuid4())
        self._cumulative_reward = 0.0
        self._protected_commitments = True
        return self._build_observation(done=False, reward=None)

    def step(
        self,
        action: AssistantAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> AssistantObservation:
        if not self._threads:
            self.reset(scenario_id=self._scenario_id)
        if self._thread_index >= len(self._threads):
            return self._build_observation(done=True, reward=0.0)

        current_thread = self._threads[self._thread_index]
        outcome = self._apply_action(current_thread, action)
        self._last_outcome = "; ".join(outcome.notes)
        if outcome.success:
            self._resolved_threads.append(current_thread["thread_id"])

        self._thread_index += 1
        done = self._thread_index >= len(self._threads)
        observation = self._build_observation(done=done, reward=None)
        reward = self._apply_rubric(action, observation)
        observation.reward = clamp_score(reward)
        self._cumulative_reward += observation.reward
        if done:
            observation.metadata["final_score"] = round(self._cumulative_reward / len(self._threads), 4)
        return observation

    @property
    def state(self) -> AssistantState:
        unresolved = [
            thread["thread_id"]
            for thread in self._threads[self._thread_index :]
        ]
        final_score = None
        if not unresolved and self._threads:
            final_score = round(self._cumulative_reward / len(self._threads), 4)
        return AssistantState(
            episode_id=self._episode_id,
            step_count=self._thread_index,
            scenario_id=self._scenario_id,
            title=self._scenario["title"],
            objective=self._scenario["objective"],
            current_thread_id=None if self._thread_index >= len(self._threads) else self._threads[self._thread_index]["thread_id"],
            booked_slots={
                slot["slot_id"]: slot["reserved_for"]
                for slot in self._calendar_slots
                if slot.get("reserved_for")
            },
            delegate_loads={
                name: delegate["capacity"]
                for name, delegate in self._delegates.items()
            },
            completed_threads=list(self._resolved_threads),
            unresolved_threads=unresolved,
            conflict_log=list(self._conflicts),
            cumulative_reward=round(self._cumulative_reward, 4),
            final_score=final_score,
        )

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="executive-assistant-negotiation-env",
            description=(
                "A multi-agent, long-horizon executive assistant environment with "
                "calendar negotiation, delegation, and stakeholder tradeoffs."
            ),
            version="2.0.0",
        )

    def _build_observation(
        self,
        done: bool,
        reward: Optional[float],
    ) -> AssistantObservation:
        thread = self._threads[min(self._thread_index, len(self._threads) - 1)]
        current_thread = ThreadContext(
            thread_id=thread["thread_id"],
            sender=thread["sender"],
            sender_role=thread["sender_role"],
            subject=thread["subject"],
            body=thread["body"],
            visible_constraints=thread["visible_constraints"],
            social_risk=thread["social_risk"],
            asks=thread["asks"],
        )
        observation = AssistantObservation(
            done=done,
            reward=reward,
            scenario_id=self._scenario_id,
            title=self._scenario["title"],
            objective=self._scenario["objective"],
            step_index=self._thread_index,
            total_steps=len(self._threads),
            current_thread=current_thread,
            available_slots=[
                CalendarSlot(
                    slot_id=slot["slot_id"],
                    label=slot["label"],
                    duration_minutes=slot["duration_minutes"],
                    available=slot.get("reserved_for") is None,
                    reserved_for=slot.get("reserved_for"),
                )
                for slot in self._calendar_slots
            ],
            delegates=[
                DelegateStatus(
                    name=delegate["name"],
                    role=delegate["role"],
                    specialties=delegate["specialties"],
                    capacity_remaining=delegate["capacity"],
                    trust_level=delegate["trust_level"],
                )
                for delegate in self._delegates.values()
            ],
            stakeholder_hints=[
                StakeholderHint(**hint) for hint in self._scenario["stakeholder_hints"]
            ],
            outstanding_conflicts=list(self._conflicts),
            completed_threads=list(self._resolved_threads),
            last_outcome=self._last_outcome,
            metadata={
                "expected": thread["expected"],
                "total_threads": len(self._threads),
                "resolved_threads": len(self._resolved_threads),
                "conflict_count": len(self._conflicts),
                "unresolved_critical": self._has_unresolved_critical_threads(done),
                "protected_commitments": self._protected_commitments,
            },
        )
        return observation

    def _apply_action(self, thread: Dict[str, Any], action: AssistantAction) -> ThreadOutcome:
        notes: List[str] = []
        conflicts_added: List[str] = []
        success = True

        if action.thread_id != thread["thread_id"]:
            notes.append("Action referenced the wrong thread.")
            conflicts_added.append(f"Wrong thread referenced for {thread['thread_id']}.")
            success = False

        if action.decision == "schedule":
            slot = self._lookup_slot(action.chosen_slot)
            if slot is None:
                notes.append("Requested meeting slot does not exist.")
                conflicts_added.append("Invalid calendar slot selected.")
                success = False
            elif slot.get("reserved_for") is not None:
                notes.append("Meeting slot was already reserved.")
                conflicts_added.append(f"Slot {action.chosen_slot} double-booked.")
                success = False
            else:
                slot["reserved_for"] = thread["thread_id"]
                notes.append(f"Reserved {slot['label']} for {thread['subject']}.")

        if action.decision == "delegate":
            delegate = self._delegates.get(action.target_person or "")
            if delegate is None:
                notes.append("Delegation target was not available.")
                conflicts_added.append("Delegated to a non-existent teammate.")
                success = False
            elif delegate["capacity"] <= 0:
                notes.append(f"{delegate['name']} had no delegation capacity left.")
                conflicts_added.append(f"Delegation overload on {delegate['name']}.")
                success = False
            else:
                delegate["capacity"] -= 1
                notes.append(f"Delegated to {delegate['name']}.")

        if action.decision == "decline" and action.chosen_slot:
            notes.append("Decline action should not reserve a slot.")
            conflicts_added.append("Reserved a slot while declining the request.")
            success = False

        if action.decision == "reply":
            notes.append("Drafted a direct reply.")

        if action.decision == "clarify":
            notes.append("Asked for more information before committing resources.")

        if action.decision == "decline":
            notes.append("Declined the request and protected scarce executive time.")

        if action.decision == "archive":
            notes.append("Archived the thread without follow-up.")
            if thread["social_risk"] in {"high", "critical"}:
                conflicts_added.append("Archived a thread that required response.")
                success = False

        forbidden_slot = thread["expected"].get("forbidden_slot")
        if forbidden_slot and action.chosen_slot == forbidden_slot:
            self._protected_commitments = False
            conflicts_added.append("Burned a protected personal commitment.")

        if thread["sender_role"] == "Family" and action.decision != "reply":
            self._protected_commitments = False
            conflicts_added.append("Family commitment was not explicitly protected.")

        self._conflicts.extend(conflicts_added)
        if not notes:
            notes.append("Action applied with no clear progress.")
            success = False

        return ThreadOutcome(
            thread_id=thread["thread_id"],
            success=success,
            notes=notes,
            conflicts_added=conflicts_added,
        )

    def _lookup_slot(self, slot_id: Optional[str]) -> Optional[Dict[str, Any]]:
        if slot_id is None:
            return None
        for slot in self._calendar_slots:
            if slot["slot_id"] == slot_id:
                return slot
        return None

    def _has_unresolved_critical_threads(self, done: bool) -> bool:
        remaining = [] if done else self._threads[self._thread_index :]
        return any(thread["expected"]["priority"] == "critical" for thread in remaining)
