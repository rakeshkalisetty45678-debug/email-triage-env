# Executive Assistant Negotiation Env

## A better training target than inbox classification

Most email agents are evaluated on tasks that are too local. They label a message, extract a field, or draft a polite reply, then stop there. Real assistant work is harder because the right move depends on what happens next.

This project builds an OpenEnv environment around that missing layer of difficulty. The agent is not just answering one thread. It is managing a moving executive workflow where every action can create downstream effects:

- taking a meeting can burn a protected personal commitment
- delegating to the wrong person can overload scarce teammate capacity
- choosing sync over async can waste the executive's attention
- sending the wrong tone can damage trust even if the logistics are technically resolved

That is the core idea behind `Executive Assistant Negotiation Env`: train models on coordination, judgment, and consequence management, not just message handling.

## What the environment simulates

Each episode places the model inside a partially observable executive assistant scenario. The current version ships with scenarios such as:

- `board_crunch`: protect family dinner while handling investor pressure, security escalation, and board-prep work
- `launch_week`: coordinate product, legal, sales, and co-founder constraints during a launch window

On every step, the agent sees structured operational context:

- the active email thread
- visible constraints
- stakeholder roles and social risk
- available calendar slots
- delegate specialties and remaining capacity
- stakeholder preference hints
- outstanding conflicts created earlier in the episode

The model must then produce a structured action with real tradeoffs:

- `reply`
- `delegate`
- `schedule`
- `decline`
- `clarify`
- `archive`

It also has to assign priority, optionally choose a delegate or slot, write a rationale, and draft the outward-facing message.

This matters because many seemingly acceptable local actions are globally bad. A model can sound helpful while still making the executive's week worse.

## Why this is a multi-agent problem

The environment is called a negotiation environment for a reason. The agent is constantly balancing multiple actors with different needs:

- executives protecting time, reputation, and personal commitments
- internal operators who can absorb work but only within capacity
- external stakeholders who care about responsiveness and reliability
- family or relationship actors whose constraints should not be treated as disposable

That combination creates a more realistic social planning problem than generic email triage. Success is not about being maximally agreeable. It is about choosing the right coordination move under pressure.

## Reward design

The reward function is built from composable OpenEnv rubrics so the model gets feedback on both local and long-horizon behavior:

- `DecisionRubric`: did it pick the right action type?
- `PriorityRubric`: did it calibrate urgency correctly?
- `CoordinationRubric`: did it choose the right slot or delegate?
- `CommunicationRubric`: did the rationale and message reflect the actual constraints?
- `LongHorizonOutcomeRubric`: did the full episode avoid preventable conflicts and resolve the important work?

This is one of the more important parts of the project. A purely terminal reward would make iteration slow and opaque. A purely local reward would miss the whole point. The mixed rubric approach gives dense feedback while still preserving the cost of bad trajectory-level decisions.

## Project structure

The repo is organized so the environment, evaluation loop, and demo surface all reinforce each other:

- `env/`: environment state, tasks, data models, and grading logic
- `server/`: OpenEnv-compatible serving layer
- `streamlit_app.py`: interactive UI for playing scenarios step by step
- `inference.py`: heuristic policy used for baselines and autoplay
- `scripts/`: benchmarking, synthetic training-data generation, SFT pipeline, plotting, and submission evaluation
- `outputs/`: committed evidence such as reward plots, submission metrics, and training artifacts

This is not just an environment definition sitting alone in a folder. It is a complete small workflow: simulate, act, evaluate, train, inspect, and demo.

## Streamlit as a model-debugging surface

One nice property of the project is that the Streamlit app is not just presentation polish. It is a debugging and interpretation tool.

The UI exposes:

- the current thread and its visible constraints
- the live operational state on the right side
- manual action composition
- heuristic autoplay
- episode history
- benchmark and training artifacts

That makes it easier to inspect failure modes. When the model chooses a bad scheduling slot or delegates to the wrong teammate, you can actually see the world state that made the mistake meaningful.

## Baselines and training

The repository includes a simple random baseline, a heuristic baseline, and a lightweight supervised fine-tuning path for submission evidence. That is a practical choice: before reaching for heavyweight RL, the project first checks that the environment produces a learnable and behaviorally sensible signal.

The committed metrics already show the heuristic outperforming random, which is a useful sanity check. It suggests the task is structured enough for policy improvement, while still being rich enough that the model has real decisions to make.

## Why this project is distinctive

What makes this repo feel different from many agent demos is that it treats assistant work as operational intelligence rather than clerical automation.

The hard part is not detecting that an email mentions a meeting.
The hard part is understanding:

- whether the executive should attend at all
- whether async handling is better than live discussion
- whether a protected commitment should win over a high-status request
- whether the teammate you want is already overloaded
- whether the message you send preserves trust while still holding the boundary

That combination of resource allocation, social reasoning, and delayed consequence is where current LLM assistants still feel fragile. This environment turns that weakness into something concrete enough to train against.

## Where it can grow next

There is a lot of room to extend the environment in credible ways:

- hidden stakeholder preferences revealed over time
- longer episodes with branching consequences
- more varied delegate trust profiles
- richer calendar geometry than fixed slots
- learning directly from rollouts with stronger policy optimization

Even in its current form, though, the project already demonstrates a meaningful benchmark category: executive assistance as sequential coordination under uncertainty.

## Closing thought

`Executive Assistant Negotiation Env` is a small but pointed argument about what useful assistant training should look like. If we want models that can help with real work, they need practice on tasks where being polite is not enough, being fast is not enough, and being locally correct is not enough.

They need to learn how to protect priorities across time.
