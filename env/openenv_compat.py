from __future__ import annotations

import os
from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


ActT = TypeVar("ActT")
ObsT = TypeVar("ObsT")
StateT = TypeVar("StateT")


LIGHT_MODE = os.getenv("OPENENV_LIGHT_MODE", "0") == "1"


if not LIGHT_MODE:
    from openenv.core import Action, Observation, State, Environment
    from openenv.core.env_server.types import EnvironmentMetadata
else:
    class Action(BaseModel):
        model_config = ConfigDict(
            extra="forbid",
            validate_assignment=True,
            arbitrary_types_allowed=True,
        )

        metadata: Dict[str, Any] = Field(default_factory=dict)


    class Observation(BaseModel):
        model_config = ConfigDict(
            extra="forbid",
            validate_assignment=True,
            arbitrary_types_allowed=True,
        )

        done: bool = False
        reward: bool | int | float | None = None
        metadata: Dict[str, Any] = Field(default_factory=dict)


    class State(BaseModel):
        model_config = ConfigDict(
            extra="allow",
            validate_assignment=True,
            arbitrary_types_allowed=True,
        )

        episode_id: Optional[str] = None
        step_count: int = 0


    class EnvironmentMetadata(BaseModel):
        name: str
        description: str
        version: str


    class Environment(Generic[ActT, ObsT, StateT]):
        SUPPORTS_CONCURRENT_SESSIONS: bool = False

        def __init__(self, transform=None, rubric=None):
            self.transform = transform
            self.rubric = rubric

        def _apply_rubric(self, action: ActT, observation: ObsT) -> float:
            if self.rubric is not None:
                return self.rubric(action, observation)
            return 0.0

        def _reset_rubric(self) -> None:
            if self.rubric is not None:
                self.rubric.reset()

