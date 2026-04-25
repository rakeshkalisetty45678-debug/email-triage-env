from __future__ import annotations

from typing import Any, Dict, List

from openenv.core.rubrics import Rubric, TrajectoryRubric, WeightedSum


def clamp_score(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class DecisionRubric(Rubric):
    def forward(self, action: Any, observation: Any) -> float:
        expected = observation.metadata["expected"]
        if action.decision == expected["decision"]:
            return 1.0
        if action.decision in expected.get("acceptable_decisions", []):
            return 0.7
        return 0.0


class PriorityRubric(Rubric):
    ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}

    def forward(self, action: Any, observation: Any) -> float:
        expected = observation.metadata["expected"]
        target = expected["priority"]
        gap = abs(self.ORDER[action.priority] - self.ORDER[target])
        return {0: 1.0, 1: 0.6, 2: 0.2}.get(gap, 0.0)


class CoordinationRubric(Rubric):
    def forward(self, action: Any, observation: Any) -> float:
        expected = observation.metadata["expected"]
        score = 0.5

        target = expected.get("target_person")
        if target:
            if action.target_person == target:
                score += 0.5
            elif action.target_person:
                score -= 0.35

        chosen_slot = expected.get("chosen_slot")
        if chosen_slot:
            if action.chosen_slot == chosen_slot:
                score += 0.5
            elif action.chosen_slot:
                score -= 0.35

        forbidden_slot = expected.get("forbidden_slot")
        if forbidden_slot and action.chosen_slot == forbidden_slot:
            score -= 0.6

        if target is None and chosen_slot is None and not action.target_person and not action.chosen_slot:
            score += 0.25

        return clamp_score(score)


class CommunicationRubric(Rubric):
    def forward(self, action: Any, observation: Any) -> float:
        expected = observation.metadata["expected"]
        haystack = f"{action.rationale} {action.message}".lower()
        keywords: List[str] = expected.get("keywords", [])
        if not keywords:
            return 1.0
        matches = sum(1 for keyword in keywords if keyword.lower() in haystack)
        return clamp_score(matches / len(keywords))


class LongHorizonOutcomeRubric(TrajectoryRubric):
    def score_trajectory(self, trajectory):
        if not trajectory:
            return 0.0

        _, final_observation = trajectory[-1]
        meta = final_observation.metadata
        threads = meta["total_threads"]
        resolved = meta["resolved_threads"]
        unresolved_critical = meta["unresolved_critical"]
        conflict_count = meta["conflict_count"]
        protected_commitments = meta["protected_commitments"]

        completion = resolved / max(threads, 1)
        conflict_score = max(0.0, 1.0 - 0.25 * conflict_count)
        critical_score = 0.0 if unresolved_critical else 1.0
        commitment_score = 1.0 if protected_commitments else 0.3

        total = (
            0.35 * completion
            + 0.25 * conflict_score
            + 0.25 * critical_score
            + 0.15 * commitment_score
        )
        return clamp_score(total)

    def compute_step_rewards(self):
        final_score = self.score_trajectory(self.trajectory)
        if not self.trajectory:
            return []
        per_step = final_score / len(self.trajectory)
        return [per_step] * len(self.trajectory)


def build_rubric() -> WeightedSum:
    return WeightedSum(
        [
            DecisionRubric(),
            PriorityRubric(),
            CoordinationRubric(),
            CommunicationRubric(),
            LongHorizonOutcomeRubric(intermediate_reward=0.2),
        ],
        weights=[0.25, 0.15, 0.2, 0.15, 0.25],
    )

