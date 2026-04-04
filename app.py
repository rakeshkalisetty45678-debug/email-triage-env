from fastapi import FastAPI
from pydantic import BaseModel
from env.environment import EmailTriageEnv
from env.models import Action, Observation

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
def reset(request: ResetRequest):
    env = EmailTriageEnv(task_name=request.task_name)
    obs = env.reset()
    session_id = request.task_name
    envs[session_id] = env
    return {
        "session_id": session_id,
        "observation": obs.dict()
    }

@app.post("/step")
def step(request: StepRequest):
    env = envs.get(request.session_id)
    if not env:
        return {"error": "Session not found"}

    action = Action(
        category=request.category,
        priority=request.priority,
        action=request.action
    )

    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done
    }

@app.get("/state")
def state(session_id: str):
    env = envs.get(session_id)
    if not env:
        return {"error": "Session not found"}
    return env.state()

@app.get("/health")
def health():
    return {"status": "ok"}