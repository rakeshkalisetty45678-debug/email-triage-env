from __future__ import annotations

from env import AssistantAction, ExecutiveAssistantEnv


def heuristic_policy(observation) -> AssistantAction:
    thread = observation.current_thread
    text = f"{thread.subject} {thread.body}".lower()

    decision = "reply"
    priority = "medium"
    target_person = None
    chosen_slot = None
    rationale = "Acknowledge the thread and choose the lowest-risk next action."
    message = "Thanks, I am handling this with the right balance of urgency and constraints."

    if "family" in text or thread.sender_role == "Family":
        decision = "reply"
        priority = "high"
        rationale = "Protecting the family commitment prevents relationship damage later in the episode."
        message = "Confirmed. Friday dinner remains protected and I will keep that time blocked."
    elif "security" in text or "login" in text or "incident" in text:
        decision = "delegate"
        priority = "critical"
        target_person = "Mira Shah"
        rationale = "Security incidents should move immediately to the security lead with explicit approval."
        message = "Mira, you are approved to lock sessions and begin incident response immediately."
    elif "vendor" in text or "appendix" in text or "finance" in text:
        decision = "delegate"
        priority = "high"
        target_person = "Nikhil Rao"
        rationale = "This needs progress before the deadline but can be prepared by the chief of staff."
        message = "Nikhil, please take point on the board appendix and bring back the vendor ranges for decision."
    elif "pricing" in text or "procurement" in text or "pilot" in text:
        decision = "delegate"
        priority = "high"
        target_person = "Aman Verma"
        rationale = "Aman can keep the buyer warm without consuming executive meeting time."
        message = "Aman, please coordinate pricing follow-up and keep the pilot timeline on track."
    elif "blocker" in text or "arbitration" in text or "launch" in text:
        decision = "schedule"
        priority = "critical"
        chosen_slot = "tue_1130"
        rationale = "This is the highest-leverage live decision, so reserve the protected Tuesday slot."
        message = "Let's meet Tuesday 11:30 to resolve the launch blockers decisively."
    elif "friday 6:30" in text:
        decision = "decline"
        priority = "high"
        rationale = "The request collides with a protected family commitment, so propose an alternative instead."
        message = "We need to keep Friday evening protected, but I can send the board narrative now and propose Thursday."
    elif "async" in text:
        decision = "reply"
        priority = "medium"
        rationale = "The sender explicitly prefers async review, which preserves scarce meeting capacity."
        message = "Async review works well here. Please send comments tonight and we will fold them in."

    return AssistantAction(
        thread_id=thread.thread_id,
        decision=decision,
        priority=priority,
        target_person=target_person,
        chosen_slot=chosen_slot,
        rationale=rationale,
        message=message,
    )


def run_demo(scenario_id: str = "board_crunch") -> float:
    env = ExecutiveAssistantEnv()
    observation = env.reset(seed=7, scenario_id=scenario_id)
    rewards = []

    while not observation.done:
        action = heuristic_policy(observation)
        observation = env.step(action)
        rewards.append(float(observation.reward or 0.0))

    return sum(rewards) / len(rewards)


if __name__ == "__main__":
    for scenario_id in ("board_crunch", "launch_week"):
        score = run_demo(scenario_id)
        print(f"{scenario_id}: mean_step_reward={score:.3f}")

