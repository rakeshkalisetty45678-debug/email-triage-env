from pydantic import BaseModel
from typing import List, Optional

class Email(BaseModel):
    id: str
    subject: str
    sender: str
    body: str

class Action(BaseModel):
    category: str        # spam / work / personal / newsletter / urgent
    priority: str        # high / medium / low
    action: str          # delete / reply / read / forward / archive

class Observation(BaseModel):
    email: Email
    step_number: int
    max_steps: int
    task_description: str

class Reward(BaseModel):
    score: float
    category_correct: bool
    priority_correct: bool
    action_correct: bool
    reason: str
