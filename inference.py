import os
import json
from openai import OpenAI
from env.environment import EmailTriageEnv
from env.models import Action
from typing import List, Optional

# Environment variables — defaults mandatory!
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

SYSTEM_PROMPT = """
You are an email triage assistant.
Given an email, you must respond with ONLY a JSON object like this:
{
    "category": "spam|work|personal|newsletter|urgent",
    "priority": "high|medium|low",
    "action": "delete|reply|read|forward|archive"
}
No explanation. No extra text. Just the JSON.
"""

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

def get_action(obs) -> Action:
    user_prompt = f"""
Task: {obs.task_description}
Email ID: {obs.email.id}
Subject: {obs.email.subject}
Sender: {obs.email.sender}
Body: {obs.email.body}

Classify this email.
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=100
        )
        text = response.choices[0].message.content.strip()
        data = json.loads(text)
        return Action(**data)
    except Exception as e:
        print(f"[DEBUG] Error: {e}", flush=True)
        return Action(category="spam", priority="low", action="delete")

def run_task(task_name: str):
    env = EmailTriageEnv(task_name=task_name)
    obs = env.reset()
    rewards: List[float] = []
    step = 0
    done = False
    score = 0.0
    success = False

    log_start(task=task_name, env="email-triage-env", model=MODEL_NAME)

    try:
        while not done:
            step += 1
            action = get_action(obs)
            obs, reward, done, info = env.step(action)
            rewards.append(reward)
            log_step(step=step, action=f"{action.category}/{action.priority}/{action.action}", reward=reward, done=done, error=None)

        score = sum(rewards) / len(rewards) if rewards else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= 0.5
    finally:
        log_end(success=success, steps=step, score=score, rewards=rewards)

if __name__ == "__main__":
    for task in ["spam_detection", "email_categorization", "inbox_triage"]:
        run_task(task)
        print()