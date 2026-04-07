from env.models import Reward

def safe_score(raw: float) -> float:
    return max(0.001, min(0.999, float(raw)))

def grade_action(action, expected):
    score = 0.0

    # partial rewards (slightly reduced to avoid total = 1.0)
    if action.category == expected["category"]:
        score += 0.35

    if action.priority == expected["priority"]:
        score += 0.30

    if action.action == expected["action"]:
        score += 0.30

    # small base reward (avoid 0 edge cases)
    score += 0.05

    # clamp strictly (0,1)
    score = safe_score(score)

    return Reward(score=score)