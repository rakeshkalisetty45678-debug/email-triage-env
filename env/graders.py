from env.models import Reward

def safe_score(raw: float) -> float:
    # STRICT (0,1)
    return max(0.001, min(0.999, float(raw)))

def grade_action(action, expected):
    score = 0.0

    # partial rewards
    if action.category == expected["category"]:
        score += 0.4

    if action.priority == expected["priority"]:
        score += 0.3

    if action.action == expected["action"]:
        score += 0.3

    # 🚨 MOST IMPORTANT LINE
    score = safe_score(score)

    return Reward(score=score)