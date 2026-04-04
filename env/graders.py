from env.models import Action, Reward


def grade_action(action: Action, expected: dict) -> Reward:
    score = 0.0
    category_correct = False
    priority_correct = False
    action_correct = False

    # Category check — 40%
    if action.category == expected["category"]:
        score += 0.4
        category_correct = True

    # Priority check — 30%
    if action.priority == expected["priority"]:
        score += 0.3
        priority_correct = True

    # Action check — 30%
    if action.action == expected["action"]:
        score += 0.3
        action_correct = True

    # Penalty — wrong urgent classification
    if action.category == "urgent" and expected["category"] == "spam":
        score -= 0.3

    # Clamp score between 0.0 and 1.0
    score = max(0.0, min(1.0, score))

    reason = f"Category={'✅' if category_correct else '❌'} Priority={'✅' if priority_correct else '❌'} Action={'✅' if action_correct else '❌'}"

    return Reward(
        score=score,
        category_correct=category_correct,
        priority_correct=priority_correct,
        action_correct=action_correct,
        reason=reason
    )