import os
from openai import OpenAI
from env.environment import EmailTriageEnv
from env.models import Action

# Environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

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

def get_action(obs) -> Action:
    user_prompt = f"""
Task: {obs.task_description}
Email ID: {obs.email.id}
Subject: {obs.email.subject}
Sender: {obs.email.sender}
Body: {obs.email.body}

Classify this email.
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,
        max_tokens=100
    )

    import json
    text = response.choices[0].message.content.strip()
    data = json.loads(text)
    return Action(**data)


def run_task(task_name: str):
    env = EmailTriageEnv(task_name=task_name)
    obs = env.reset()

    print(f"[START] task={task_name} env=email-triage-env model={MODEL_NAME}")

    rewards = []
    step = 0
    done = False

    while not done:
        step += 1
        action = get_action(obs)
        obs, reward, done, info = env.step(action)
        rewards.append(reward)

        print(f"[STEP] step={step} action={action.category}/{action.priority}/{action.action} reward={reward:.2f} done={str(done).lower()} error=null")

    success = sum(rewards) / len(rewards) >= 0.5
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={step} rewards={rewards_str}")


if __name__ == "__main__":
    for task in ["spam_detection", "email_categorization", "inbox_triage"]:
        run_task(task)
        print()