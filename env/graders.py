# graders.py

EPS = 1e-6  # small value to avoid 0 and 1


def clamp_score(score: float) -> float:
    """
    Ensures score is strictly between (0,1)
    """
    return max(EPS, min(1 - EPS, score))


# Example Task 1 Grader
def grade_task_1(prediction, ground_truth):
    """
    Replace logic based on your task
    """
    if prediction == ground_truth:
        score = 1.0
    else:
        score = 0.0

    return clamp_score(score)


# Example Task 2 Grader (partial scoring)
def grade_task_2(prediction, ground_truth):
    """
    Example: partial matching
    """
    if not prediction or not ground_truth:
        return clamp_score(0.0)

    match_count = 0
    total = len(ground_truth)

    for p, g in zip(prediction, ground_truth):
        if p == g:
            match_count += 1

    score = match_count / total if total > 0 else 0.0
    return clamp_score(score)


# Example Task 3 Grader (string similarity)
def grade_task_3(prediction: str, ground_truth: str):
    """
    Simple similarity scoring
    """
    if not prediction or not ground_truth:
        return clamp_score(0.0)

    prediction = prediction.lower().strip()
    ground_truth = ground_truth.lower().strip()

    if prediction == ground_truth:
        score = 1.0
    elif prediction in ground_truth or ground_truth in prediction:
        score = 0.7
    else:
        score = 0.2

    return clamp_score(score)


# Main entry (if required)
def grade_all(tasks):
    """
    tasks = {
        "task1": (pred, gt),
        "task2": (pred, gt),
        ...
    }
    """
    results = {}

    if "task1" in tasks:
        pred, gt = tasks["task1"]
        results["task1"] = grade_task_1(pred, gt)

    if "task2" in tasks:
        pred, gt = tasks["task2"]
        results["task2"] = grade_task_2(pred, gt)

    if "task3" in tasks:
        pred, gt = tasks["task3"]
        results["task3"] = grade_task_3(pred, gt)

    return results