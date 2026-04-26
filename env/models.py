from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from env.openenv_compat import Action, Observation, State


DecisionType = Literal["reply", "delegate", "schedule", "decline", "clarify", "archive"]
PriorityLevel = Literal["critical", "high", "medium", "low"]


class StakeholderHint(BaseModel):
    name: str
    role: str
    preference_hint: str


class CalendarSlot(BaseModel):
    slot_id: str
    label: str
    duration_minutes: int
    available: bool = True
    reserved_for: Optional[str] = None


class DelegateStatus(BaseModel):
    name: str
    role: str
    specialties: List[str]
    capacity_remaining: int
    trust_level: str


class ThreadContext(BaseModel):
    thread_id: str
    sender: str
    sender_role: str
    subject: str
    body: str
    visible_constraints: List[str]
    social_risk: str
    asks: List[str]


class AssistantAction(Action):
    thread_id: str = Field(..., description="Thread being acted on in the current turn")
    decision: DecisionType = Field(..., description="Primary next step for the thread")
    priority: PriorityLevel = Field(..., description="Priority assigned to the thread")
    target_person: Optional[str] = Field(
        default=None,
        description="Person to delegate to or recipient to prioritize in the reply",
    )
    chosen_slot: Optional[str] = Field(
        default=None,
        description="Calendar slot id used when scheduling a meeting",
    )
    rationale: str = Field(
        ...,
        min_length=12,
        max_length=400,
        description="Brief explanation of the decision and tradeoffs",
    )
    message: str = Field(
        ...,
        min_length=12,
        max_length=500,
        description="Reply or delegation message drafted by the agent",
    )


class AssistantObservation(Observation):
    scenario_id: str
    title: str
    objective: str
    step_index: int
    total_steps: int
    current_thread: ThreadContext
    available_slots: List[CalendarSlot]
    delegates: List[DelegateStatus]
    stakeholder_hints: List[StakeholderHint]
    outstanding_conflicts: List[str]
    completed_threads: List[str]
    last_outcome: str = "Episode started."


class AssistantState(State):
    scenario_id: str
    title: str
    objective: str
    current_thread_id: Optional[str] = None
    booked_slots: Dict[str, str] = Field(default_factory=dict)
    delegate_loads: Dict[str, int] = Field(default_factory=dict)
    completed_threads: List[str] = Field(default_factory=list)
    unresolved_threads: List[str] = Field(default_factory=list)
    conflict_log: List[str] = Field(default_factory=list)
    cumulative_reward: float = 0.0
    final_score: Optional[float] = None


class ThreadOutcome(BaseModel):
    thread_id: str
    success: bool
    notes: List[str]
    conflicts_added: List[str] = Field(default_factory=list)
