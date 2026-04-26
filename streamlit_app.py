from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

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


def _risk_tone(risk: str) -> str:
    return {
        "critical": "#ef4444",
        "high": "#f59e0b",
        "medium": "#38bdf8",
        "low": "#34d399",
    }.get(risk.lower(), "#a1a1aa")


def _render_badge(label: str, value: str, tone: str = "#f59e0b") -> None:
    st.markdown(
        f"""
        <div class="badge-row">
          <span class="badge-label">{html.escape(label)}</span>
          <span class="badge-value" style="border-color:{tone}; color:{tone};">
            {html.escape(value)}
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _metric_card_html(
    label: str,
    value: str,
    detail: str = "",
    value_class: str = "",
) -> str:
    detail_html = (
        f'<div class="metric-detail">{html.escape(detail)}</div>' if detail else ""
    )
    metric_value_class = "metric-value"
    if value_class:
        metric_value_class = f"{metric_value_class} {value_class}"
    return f"""
        <div class="metric-card">
          <div class="metric-label">{html.escape(label)}</div>
          <div class="{metric_value_class}">{html.escape(value)}</div>
          {detail_html}
        </div>
    """


def _render_metric_grid(cards: list[str]) -> None:
    st.markdown(
        f"""
        <div class="metrics-grid">
          {''.join(cards)}
        </div>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def _section(title: str, subtitle: str = ""):
    with st.container(border=True):
        st.markdown(
            f'<div class="section-title">{html.escape(title)}</div>',
            unsafe_allow_html=True,
        )
        if subtitle:
            st.markdown(
                f'<div class="section-subtitle">{html.escape(subtitle)}</div>',
                unsafe_allow_html=True,
            )
        yield


def _render_fixed_table(title: str, rows: list[dict]) -> None:
    st.markdown(f"**{title}**")
    if not rows:
        st.write("No data available.")
        return

    columns = list(rows[0].keys())
    header_html = "".join(f"<th>{html.escape(str(column))}</th>" for column in columns)
    row_html = []
    for row in rows:
        cells = "".join(
            f"<td>{html.escape(str(row.get(column, '')))}</td>" for column in columns
        )
        row_html.append(f"<tr>{cells}</tr>")

    st.markdown(
        f"""
        <div class="stable-table-wrap">
          <table class="stable-table">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{''.join(row_html)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_text_list(title: str, items: list[str]) -> None:
    st.markdown(f"**{title}**")
    if not items:
        st.write("No data available.")
        return

    item_html = "".join(f"<li>{html.escape(item)}</li>" for item in items)
    st.markdown(
        f"""
        <div class="stable-list-wrap">
          <ul class="stable-list">{item_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    _ensure_session()
    st.markdown(
        """
        <style>
          html {
            scrollbar-gutter: stable both-edges;
          }
          body {
            overflow-x: hidden;
            overflow-y: scroll;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            font-family: "Segoe UI", Arial, sans-serif;
          }
          *, *::before, *::after {
            animation: none !important;
            transition: none !important;
          }
          [data-testid="stAppViewContainer"],
          [data-testid="stApp"] {
            overflow-x: hidden;
          }
          .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1400px;
          }
          [data-testid="stHeader"] {
            background: transparent;
          }
          [data-testid="stToolbar"] {
            right: 0.75rem;
          }
          [data-testid="stElementToolbar"] {
            display: none;
          }
          [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(33, 33, 43, 0.98), rgba(24, 24, 32, 0.98));
            border-right: 1px solid rgba(250, 250, 250, 0.06);
          }
          [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.7rem;
          }
          .hero-shell {
            border: 1px solid rgba(250, 250, 250, 0.08);
            background: rgba(255, 255, 255, 0.02);
            border-radius: 16px;
            padding: 1.35rem 1.35rem 1.2rem 1.35rem;
            margin-bottom: 1rem;
          }
          .eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #f59e0b;
            font-size: 0.74rem;
            margin-bottom: 0.45rem;
          }
          .hero-title {
            font-size: 2.2rem;
            line-height: 1.12;
            font-weight: 600;
            color: #f8fafc;
            margin: 0 0 0.65rem 0;
          }
          .hero-copy {
            max-width: 64ch;
            color: #cbd5e1;
            font-size: 0.98rem;
            line-height: 1.55;
          }
          .metric-card {
            min-height: 132px;
            border: 1px solid rgba(250, 250, 250, 0.08);
            background: rgba(255, 255, 255, 0.02);
            border-radius: 18px;
            padding: 1rem 1rem 0.9rem 1rem;
            overflow: hidden;
          }
          .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
          }
          .metric-label {
            color: #a1a1aa;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.65rem;
          }
          .metric-value {
            color: #f8fafc;
            font-size: 1.75rem;
            line-height: 1.12;
            font-weight: 600;
            overflow-wrap: break-word;
            word-break: break-word;
          }
          .metric-value--title {
            font-size: 0.98rem;
            line-height: 1.28;
            font-weight: 600;
          }
          .metric-value--score {
            white-space: nowrap;
          }
          .metric-detail {
            color: #cbd5e1;
            margin-top: 0.85rem;
            font-size: 0.92rem;
            line-height: 1.45;
          }
          [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 18px;
          }
          [data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 1.15rem 1.15rem 1rem 1.15rem;
          }
          [data-testid="column"] {
            min-width: 0;
          }
          [data-testid="stHorizontalBlock"] > [data-testid="column"] > div {
            min-width: 0;
          }
          .section-title {
            color: #f8fafc;
            font-size: 1.35rem;
            font-weight: 650;
            margin-bottom: 0.35rem;
          }
          .section-subtitle {
            color: #a1a1aa;
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 1rem;
          }
          .thread-meta {
            color: #e4e4e7;
            line-height: 1.6;
            margin-bottom: 0.5rem;
          }
          .thread-body {
            color: #f1f5f9;
            font-size: 1.05rem;
            line-height: 1.75;
            margin: 0.85rem 0 0.4rem 0;
          }
          .list-card {
            min-height: 190px;
            border: 1px solid rgba(250, 250, 250, 0.06);
            background: rgba(255, 255, 255, 0.018);
            border-radius: 16px;
            padding: 0.95rem 1rem 0.85rem 1rem;
          }
          .list-card h4 {
            margin: 0 0 0.75rem 0;
            font-size: 1rem;
            color: #f8fafc;
          }
          .list-card ul {
            margin: 0;
            padding-left: 1.2rem;
          }
          .list-card li {
            margin-bottom: 0.5rem;
            color: #e4e4e7;
            line-height: 1.55;
          }
          .badge-row {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin-top: 0.9rem;
            margin-bottom: 0.2rem;
          }
          .badge-label {
            color: #a1a1aa;
            font-size: 0.92rem;
          }
          .badge-value {
            display: inline-flex;
            align-items: center;
            min-height: 32px;
            padding: 0.15rem 0.65rem;
            border: 1px solid;
            border-radius: 999px;
            background: rgba(255,255,255,0.02);
            font-size: 0.88rem;
            font-weight: 600;
          }
          .stable-table-wrap {
            width: 100%;
            overflow-x: auto;
            border: 1px solid rgba(250, 250, 250, 0.12);
            border-radius: 12px;
            margin-bottom: 1rem;
          }
          .stable-table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            min-width: 620px;
          }
          .stable-table thead {
            white-space: nowrap;
          }
          .stable-table th,
          .stable-table td {
            padding: 0.75rem 0.8rem;
            border-bottom: 1px solid rgba(250, 250, 250, 0.08);
            text-align: left;
            vertical-align: top;
            word-break: break-word;
            overflow-wrap: break-word;
            hyphens: none;
          }
          .stable-table th {
            font-weight: 600;
            background: rgba(250, 250, 250, 0.03);
          }
          .stable-list-wrap {
            border: 1px solid rgba(250, 250, 250, 0.08);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.015);
            padding: 0.65rem 0.85rem;
            margin-bottom: 1rem;
            overflow: hidden;
          }
          .stable-list {
            margin: 0;
            padding-left: 1.15rem;
          }
          .stable-list li {
            color: #e4e4e7;
            line-height: 1.55;
            margin-bottom: 0.45rem;
          }
          .stable-list li:last-child {
            margin-bottom: 0;
          }
          .artifact-grid-note {
            color: #a1a1aa;
            margin-top: -0.45rem;
            margin-bottom: 1rem;
          }
          .stButton > button {
            min-height: 48px;
            border-radius: 14px;
            border: 1px solid rgba(250, 250, 250, 0.08);
          }
          .stNumberInput, .stSelectbox, .stTextArea {
            margin-bottom: 0.1rem;
          }
          @media (max-width: 1100px) {
            .hero-title {
              font-size: 1.95rem;
            }
            .metrics-grid {
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }
          }
          @media (max-width: 700px) {
            .hero-title {
              font-size: 1.7rem;
            }
            .metrics-grid {
              grid-template-columns: 1fr;
            }
            .metric-value {
              font-size: 1.5rem;
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("## Episode Setup")
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

    st.markdown(
        """
        <div class="hero-shell">
          <div class="eyebrow">Interactive Operations Console</div>
          <div class="hero-title">Executive Assistant Negotiation Env</div>
          <div class="hero-copy">
            A high-pressure assistant workflow simulator where every reply, delegation,
            and calendar decision trades off urgency, relationships, and long-horizon outcomes.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_metric_grid(
        [
            _metric_card_html(
                "Scenario",
                scenario["title"],
                observation.scenario_id,
                "metric-value--title",
            ),
            _metric_card_html(
            "Progress",
            f"{observation.step_index}/{observation.total_steps}",
            "Current step across the episode trajectory.",
            "metric-value--score",
            ),
            _metric_card_html(
            "Reward",
            f"{state.cumulative_reward:.4f}",
            "Cumulative score from the rubric so far.",
            "metric-value--score",
            ),
            _metric_card_html(
                "Final Score",
                f"{state.final_score:.4f}" if state.final_score is not None else "Pending",
                "Locked when the episode reaches the last thread.",
                "metric-value--score",
            ),
        ]
    )

    left, right = st.columns([1.45, 0.95], gap="large")

    with left:
        with _section("Current Thread", scenario["objective"]):
            st.markdown(
                f"""
                <div class="thread-meta"><strong>From:</strong> {html.escape(observation.current_thread.sender)}
                ({html.escape(observation.current_thread.sender_role)})</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="thread-meta"><strong>Subject:</strong> {html.escape(observation.current_thread.subject)}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="thread-body">{html.escape(observation.current_thread.body)}</div>',
                unsafe_allow_html=True,
            )
            _render_badge(
                "Social Risk",
                observation.current_thread.social_risk,
                _risk_tone(observation.current_thread.social_risk),
            )

            thread_col1, thread_col2 = st.columns(2)
            with thread_col1:
                constraint_items = "".join(
                    f"<li>{html.escape(item)}</li>"
                    for item in observation.current_thread.visible_constraints
                )
                st.markdown(
                    f"""
                    <div class="list-card">
                      <h4>Visible Constraints</h4>
                      <ul>{constraint_items}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with thread_col2:
                ask_items = "".join(
                    f"<li>{html.escape(item)}</li>"
                    for item in observation.current_thread.asks
                )
                st.markdown(
                    f"""
                    <div class="list-card">
                      <h4>Asks</h4>
                      <ul>{ask_items}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        with _section(
            "Action Composer",
            "Compose a response manually or let the heuristic take the next move.",
        ):
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
        with _section("Live State", "Operational resources, teammate capacity, and conflict tracking."):
            _render_fixed_table(
                "Available Slots",
                [
                    {
                        "slot_id": slot.slot_id,
                        "label": slot.label,
                        "available": slot.available,
                        "reserved_for": slot.reserved_for or "",
                    }
                    for slot in observation.available_slots
                ],
            )
            _render_fixed_table(
                "Delegates",
                [
                    {
                        "name": delegate.name,
                        "role": delegate.role,
                        "capacity_remaining": delegate.capacity_remaining,
                        "specialties": ", ".join(delegate.specialties),
                    }
                    for delegate in observation.delegates
                ],
            )
            _render_text_list(
                "Stakeholder Hints",
                [
                    f"{hint.name} ({hint.role}): {hint.preference_hint}"
                    for hint in observation.stakeholder_hints
                ],
            )
            _render_text_list(
                "Conflicts",
                observation.outstanding_conflicts or ["No conflicts logged."],
            )

    with _section("Episode History", "Decision trail across the current run."):
        if st.session_state.history:
            st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)
        else:
            st.write("No actions applied yet.")

    with _section("Artifacts", "Benchmark and training evidence committed with the repo."):
        st.markdown('<div class="artifact-grid-note">These visuals are static repo artifacts, useful for demos and submission evidence.</div>', unsafe_allow_html=True)
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
