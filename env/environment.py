from typing import Optional
from env.models import Action, Observation, Email, Reward
from env.tasks import TASKS
from env.graders import grade_action


class EmailTriageEnv:
    def __init__(self, task_name: str = "spam_detection"):
        self.task_name = task_name
        self.task = TASKS[task_name]
        self.emails = self.task["emails"]
        self.max_steps = self.task["max_steps"]
        self.current_step = 0
        self.current_email_index = 0
        self.done = False
        self.rewards = []

    def reset(self) -> Observation:
        self.current_step = 0
        self.current_email_index = 0
        self.done = False
        self.rewards = []
        return self._get_observation()

    def step(self, action: Action):
        if self.done:
            return self._get_observation(), 0.0, True, {}

        # Grade current action
        expected = self.emails[self.current_email_index]["expected"]
        reward_obj = grade_action(action, expected)
        reward = reward_obj.score

        self.rewards.append(reward)
        self.current_step += 1
        self.current_email_index += 1

        # Check if done
        if self.current_email_index >= len(self.emails):
            self.done = True
        elif self.current_step >= self.max_steps:
            self.done = True

        obs = self._get_observation()
        info = {"reward_detail": reward_obj}

        return obs, reward, self.done, info

    def state(self):
        return {
            "task_name": self.task_name,
            "current_step": self.current_step,
            "max_steps": self.max_steps,
            "current_email_index": self.current_email_index,
            "done": self.done,
            "rewards_so_far": self.rewards
        }

    def _get_observation(self) -> Observation:
        if self.done or self.current_email_index >= len(self.emails):
            email_data = self.emails[-1]
        else:
            email_data = self.emails[self.current_email_index]

        email = Email(
            id=email_data["id"],
            subject=email_data["subject"],
            sender=email_data["sender"],
            body=email_data["body"]
        )

        return Observation(
            email=email,
            step_number=self.current_step,
            max_steps=self.max_steps,
            task_description=self.task["description"]
        )