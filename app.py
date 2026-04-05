import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from pydantic import BaseModel
from env.environment import EmailTriageEnv
from env.models import Action

app = FastAPI()
envs = {}

class ResetRequest(BaseModel):
    task_name: str = "spam_detection"

class StepRequest(BaseModel):
    session_id: str
    category: str
    priority: str
    action: str

@app.post("/reset")
def reset(request: ResetRequest = None):
    task_name = request.task_name if request else "spam_detection"
    env = EmailTriageEnv(task_name=task_name)
    obs = env.reset()
    envs[task_name] = env
    return {"session_id": task_name, "observation": obs.dict()}

@app.post("/step")
def step(request: StepRequest):
    env = envs.get(request.session_id)
    if not env:
        return {"error": "Session not found"}
    action = Action(category=request.category, priority=request.priority, action=request.action)
    obs, reward, done, info = env.step(action)
    return {"observation": obs.dict(), "reward": reward, "done": done}

@app.get("/state")
def state(session_id: str):
    env = envs.get(session_id)
    if not env:
        return {"error": "Session not found"}
    return env.state()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/metadata")
def metadata():
    return {
        "name": "email-triage-env",
        "description": "An RL environment for triaging emails"
    }

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()