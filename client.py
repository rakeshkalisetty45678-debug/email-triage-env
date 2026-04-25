from __future__ import annotations

from typing import Any, Dict

from openenv.core import EnvClient
from openenv.core.env_client import StepResult

from env import AssistantAction, AssistantObservation, AssistantState


class ExecutiveAssistantEnvClient(
    EnvClient[AssistantAction, AssistantObservation, AssistantState]
):
    def _step_payload(self, action: AssistantAction) -> Dict[str, Any]:
        return action.model_dump()

    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[AssistantObservation]:
        observation = AssistantObservation.model_validate(payload.get("observation", {}))
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", observation.done),
        )

    def _parse_state(self, payload: Dict[str, Any]) -> AssistantState:
        return AssistantState.model_validate(payload)

