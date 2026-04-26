from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import streamlit as st

from env import AssistantAction, ExecutiveAssistantEnv
from env.tasks import SCENARIOS
from inference import heuristic_policy


st.set_page_config(
    page_title="Executive Assistant Negotiation Env",
    page_icon="📅",
    layout="wide",
)


def _ensure_session() -> None:
    if "env" not in st.session_state:
        st.session_state.env = ExecutiveAssistantEnv()
    if "observation" not in st.session_state:
        st.session_state.observation = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "seed" not in st.session_state:
        st.session_state.seed = 7
    if "scenario_id" not in st.session_state:
        st.session_state.scenario_id = "board_crunch"


def _reset_env() -> None:
    st.session_state.env = ExecutiveAssistantEnv()
    st.session_state.observation = st.session_state.env.reset(
        seed=int(st.session_state.seed),
        scenario_id=st.session_state.scenario_id,
    )
    st.session_state.history = []


def _apply_action(action: AssistantAction) -> None:
    observation = st.session_state.env.step(action)
    st.session_state.history.append(
        {
            "thread_id": action.thread_id,
            "decision": action.decision,
            "priority": action.priority,
            "target_person": action.target_person,
            "chosen_slot": action.chosen_slot,
            "reward": float(observation.reward or 0.0),
            "last_outcome": observation.last_outcome,
        }
    )
    st.session_state.observation = observation


def _play_heuristic_episode() -> None:
    if st.session_state.observation is None:
        _reset_env()
    while not st.session_state.observation.done:
        action = heuristic_policy(st.session_state.observation)
        _apply_action(action)


def _artifact_image(path: str, caption: str) -> None:
    artifact_path = Path(path)
    if artifact_path.exists():
        st.image(str(artifact_path), caption=caption, use_container_width=True)


def _artifact_json(path: str) -> Optional[dict]:
    artifact_path = Path(path)
    if artifact_path.exists():
        return json.loads(artifact_path.read_text(encoding="utf-8"))
    return None


def main() -> None:
    _ensure_session()

    st.title("Executive Assistant Negotiation Env")
    st.caption(
        "Interactive Streamlit UI for the OpenEnv executive assistant environment."
    )

    with st.sidebar:
        st.subheader("Episode Setup")
        st.selectbox(
            "Scenario",
            options=list(SCENARIOS.keys()),
            key="scenario_id",
            format_func=lambda key: SCENARIOS[key]["title"],
        )
        st.number_input("Seed", min_value=0, max_value=9999, step=1, key="seed")
        if st.button("Start New Episode", use_container_width=True):
            _reset_env()
        if st.button("Run Heuristic Episode", use_container_width=True):
            _reset_env()
            _play_heuristic_episode()

        st.divider()
        st.subheader("Artifacts")
        metrics = _artifact_json("outputs/submission_eval/submission_metrics.json")
        if metrics:
            st.metric("Random", f"{metrics['random']['mean_reward']:.4f}")
            st.metric("Base Model", f"{metrics['base_model']['mean_reward']:.4f}")
            st.metric("Trained Model", f"{metrics['trained_model']['mean_reward']:.4f}")
            st.metric("Heuristic", f"{metrics['heuristic']['mean_reward']:.4f}")

    if st.session_state.observation is None:
        _reset_env()

    observation = st.session_state.observation
    scenario = SCENARIOS[observation.scenario_id]
    state = st.session_state.env.state

    overview_col, score_col = st.columns([3, 1])
    with overview_col:
        st.subheader(scenario["title"])
        st.write(scenario["objective"])
    with score_col:
        st.metric("Step", f"{observation.step_index}/{observation.total_steps}")
        st.metric("Cumulative Reward", f"{state.cumulative_reward:.4f}")
        if state.final_score is not None:
            st.metric("Final Score", f"{state.final_score:.4f}")

    left, right = st.columns([1.6, 1])

    with left:
        st.subheader("Current Thread")
        st.markdown(f"**From:** {observation.current_thread.sender} ({observation.current_thread.sender_role})")
        st.markdown(f"**Subject:** {observation.current_thread.subject}")
        st.write(observation.current_thread.body)

        thread_col1, thread_col2 = st.columns(2)
        with thread_col1:
            st.markdown("**Visible Constraints**")
            for item in observation.current_thread.visible_constraints:
                st.write(f"- {item}")
        with thread_col2:
            st.markdown("**Asks**")
            for item in observation.current_thread.asks:
                st.write(f"- {item}")
            st.markdown(f"**Social Risk:** `{observation.current_thread.social_risk}`")

        st.subheader("Action Composer")
        heuristic = heuristic_policy(observation)

        with st.form("action_form", clear_on_submit=False):
            decision = st.selectbox(
                "Decision",
                options=["reply", "delegate", "schedule", "decline", "clarify", "archive"],
                index=["reply", "delegate", "schedule", "decline", "clarify", "archive"].index(
                    heuristic.decision
                ),
            )
            priority = st.selectbox(
                "Priority",
                options=["critical", "high", "medium", "low"],
                index=["critical", "high", "medium", "low"].index(heuristic.priority),
            )

            delegates = [delegate.name for delegate in observation.delegates if delegate.capacity_remaining > 0]
            slots = [slot.slot_id for slot in observation.available_slots if slot.available]

            target_person = st.selectbox(
                "Delegate Target",
                options=[""] + delegates,
                index=([""] + delegates).index(heuristic.target_person) if heuristic.target_person in delegates else 0,
            )
            chosen_slot = st.selectbox(
                "Meeting Slot",
                options=[""] + slots,
                index=([""] + slots).index(heuristic.chosen_slot) if heuristic.chosen_slot in slots else 0,
                format_func=lambda value: next(
                    (slot.label for slot in observation.available_slots if slot.slot_id == value),
                    "None",
                ) if value else "None",
            )
            rationale = st.text_area("Rationale", value=heuristic.rationale, height=100)
            message = st.text_area("Message", value=heuristic.message, height=120)

            submit = st.form_submit_button("Apply Action", use_container_width=True)

        action_bar = st.columns(2)
        with action_bar[0]:
            if st.button("Use Heuristic For This Step", use_container_width=True):
                _apply_action(heuristic)
                st.rerun()
        with action_bar[1]:
            if st.button("Run Heuristic To Finish", use_container_width=True):
                _play_heuristic_episode()
                st.rerun()

        if submit:
            action = AssistantAction(
                thread_id=observation.current_thread.thread_id,
                decision=decision,
                priority=priority,
                target_person=target_person or None,
                chosen_slot=chosen_slot or None,
                rationale=rationale,
                message=message,
            )
            _apply_action(action)
            st.rerun()

        if observation.done:
            st.success("Episode complete.")
            st.json(state.model_dump())
        else:
            st.info(observation.last_outcome)

    with right:
        st.subheader("Live State")
        st.markdown("**Available Slots**")
        st.dataframe(
            [
                {
                    "slot_id": slot.slot_id,
                    "label": slot.label,
                    "available": slot.available,
                    "reserved_for": slot.reserved_for or "",
                }
                for slot in observation.available_slots
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("**Delegates**")
        st.dataframe(
            [
                {
                    "name": delegate.name,
                    "role": delegate.role,
                    "capacity_remaining": delegate.capacity_remaining,
                    "specialties": ", ".join(delegate.specialties),
                }
                for delegate in observation.delegates
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("**Stakeholder Hints**")
        for hint in observation.stakeholder_hints:
            st.write(f"- **{hint.name}** ({hint.role}): {hint.preference_hint}")

        st.markdown("**Conflicts**")
        if observation.outstanding_conflicts:
            for item in observation.outstanding_conflicts:
                st.write(f"- {item}")
        else:
            st.write("No conflicts logged.")

    st.subheader("Episode History")
    if st.session_state.history:
        st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)
    else:
        st.write("No actions applied yet.")

    st.subheader("Artifacts")
    art_left, art_right = st.columns(2)
    with art_left:
        _artifact_image("reward_curve.png", "Benchmark: random vs heuristic reward")
        _artifact_image(
            "outputs/sft_run/training_loss_curve.png",
            "SFT training loss curve",
        )
    with art_right:
        _artifact_image(
            "outputs/submission_eval/submission_reward_comparison.png",
            "Submission reward comparison",
        )
        metrics = _artifact_json("outputs/submission_eval/submission_metrics.json")
        if metrics:
            st.json(
                {
                    key: value["mean_reward"] if isinstance(value, dict) and "mean_reward" in value else value
                    for key, value in metrics.items()
                }
            )


if __name__ == "__main__":
    main()
