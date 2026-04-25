from openenv.core.env_server import create_app

from env import AssistantAction, AssistantObservation, ExecutiveAssistantEnv


_ENV = ExecutiveAssistantEnv()


def build_env() -> ExecutiveAssistantEnv:
    return _ENV


app = create_app(
    env=build_env,
    action_cls=AssistantAction,
    observation_cls=AssistantObservation,
    env_name="executive-assistant-negotiation-env",
)


def main() -> None:
    import uvicorn

    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()
