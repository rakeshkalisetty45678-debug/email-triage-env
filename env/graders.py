# env/graders.py

EPS = 1e-6  # avoid 0 and 1


def clamp_score(score: float) -> float:
    return max(EPS, min(1 - EPS, score))


# ----------- MAIN GRADER FUNCTION -----------

def grade(prediction, ground_truth):
    """
    Generic grader used by environment
    Modify logic based on your task
    """

    # Example logic (works for most cases)
    if prediction == ground_truth:
        score = 1.0
    elif isinstance(prediction, str) and isinstance(ground_truth, str):
        pred = prediction.lower().strip()
        gt = ground_truth.lower().strip()

        if pred == gt:
            score = 1.0
        elif pred in gt or gt in pred:
            score = 0.7
        else:
            score = 0.2
    else:
        score = 0.0

    return clamp_score(score)


# ----------- OPTIONAL MULTI-TASK SUPPORT -----------

def grade_task_1(prediction, ground_truth):
    return grade(prediction, ground_truth)


def grade_task_2(prediction, ground_truth):
    return grade(prediction, ground_truth)


def grade_task_3(prediction, ground_truth):
    return grade(prediction, ground_truth)