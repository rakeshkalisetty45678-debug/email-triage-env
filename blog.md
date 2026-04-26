# Executive Assistant Negotiation Env

## The story behind the project

This project started from a simple observation: most LLM email tasks are too easy in the wrong way.

A model can classify an email, extract fields, or draft a polished reply and still fail at the real job. In actual executive support work, the hard part is not writing a sentence. The hard part is deciding what should happen next, who should own it, whether the executive should get involved, and which tradeoff matters most right now.

That is the gap this repository tries to address.

`Executive Assistant Negotiation Env` is an OpenEnv environment built around sequential assistant decision-making. Instead of treating inbox work as isolated message handling, it treats it as a live coordination problem with stakeholders, scarce calendar slots, delegate capacity, social risk, and delayed consequences.

The project is essentially asking a better question:

Can we train an assistant model not just to answer emails, but to manage pressure, negotiate constraints, and protect priorities across time?

## Why this problem matters

Inbox automation often looks successful because the benchmark is narrow. If the only goal is to produce a fluent answer, a model can look competent very quickly.

But real assistant work is full of hidden failure modes:

- a meeting can be scheduled into a protected personal commitment
- a security escalation can be delayed because the model sounds diplomatic instead of decisive
- a trusted operator can be overloaded because the agent ignored capacity
- a high-status stakeholder can be handled in a way that creates relationship damage later
- a locally reasonable reply can quietly make the whole week worse

Those are exactly the kinds of mistakes people remember, because they compound.

This project focuses on that compounding behavior. It frames assistant work as long-horizon coordination rather than one-turn text generation.

## Core idea

The environment places the model into a partially observable executive workflow. On each step, the model sees the current email thread plus operational context and has to emit a structured action.

The agent can choose from:

- `reply`
- `delegate`
- `schedule`
- `decline`
- `clarify`
- `archive`

It must also set priority, optionally select a delegate or a meeting slot, write a rationale, and draft the actual message.

That combination matters because the environment is not only checking whether the model can talk. It is checking whether the model can decide.

## What makes the environment realistic

The simulation is intentionally built around tensions that show up in real assistant workflows:

- multiple stakeholders want different things
- not every urgent request deserves live executive time
- calendar slots are scarce and sometimes politically sensitive
- delegates have specialties but also limited capacity
- some requests should be handled asynchronously
- personal commitments are not disposable just because business pressure appears

The agent therefore has to reason about more than one dimension at once:

- operational correctness
- communication quality
- social judgment
- resource allocation
- long-term consequence management

That is where the project becomes more interesting than standard email triage.

## The scenarios

The repo currently includes scenarios such as `board_crunch` and `launch_week`.

In `board_crunch`, the assistant has to protect a family dinner commitment while handling investor pressure, security escalation, and board-prep dependencies. This scenario works well because it forces the model to weigh emotional, operational, and reputational consequences together.

In `launch_week`, the model navigates product, legal, sales, and co-founder constraints during a busy launch window. It has to understand that not every blocker should trigger a meeting, and not every stakeholder request deserves the same coordination path.

These scenarios are compact, but they are deliberately structured so that a bad early choice can create downstream friction.

## Why this is a multi-agent environment

This is not a single-user assistant toy. It is a multi-agent coordination setting.

The assistant is balancing the preferences and capabilities of:

- the executive
- internal operators
- functional leaders
- external stakeholders
- personal or family relationships

Each of those actors has different incentives, different urgency, and different expectations about how they should be handled.

A good assistant does not just maximize speed. A good assistant routes work to the right place, protects scarce attention, and preserves trust while moving things forward.

That is the behavior this environment is trying to make learnable.

## State, actions, and observation design

Every episode exposes enough information to act, but not enough to trivialize the decision. The model gets:

- the active thread
- visible constraints
- stakeholder hints
- available calendar slots
- delegate specialties and remaining capacity
- conflict history
- prior outcomes in the episode

This makes the environment partially observable in a useful way. The model is not solving a hidden-puzzle game. It is working with incomplete but realistic operational context, the way assistants usually do.

That design choice keeps the environment grounded in actual workflow ambiguity.

## Reward design

One of the strongest parts of the repo is the reward structure.

The environment uses composable rubrics to score behavior:

- action quality
- priority calibration
- coordination quality
- communication quality
- final long-horizon outcome

This balance is important. A pure terminal reward would make improvement hard to diagnose. A pure step reward would miss the cost of choices that only become bad later.

By combining both, the project gives the model denser learning signals while still preserving the reality that some mistakes only show up after several steps.

## Why the Streamlit app matters

The Streamlit app is not just a demo shell. It is part of the project’s usefulness.

It gives a human-readable view into:

- the current thread
- the live state of slots and delegates
- stakeholder hints
- conflicts
- action composition
- heuristic autoplay
- trajectory history
- evaluation artifacts

That turns the environment into something inspectable. You can step through an episode and see why a choice mattered. You can also compare what a heuristic policy does against what a model or a human operator would do.

For a project like this, visibility is a big deal. It helps transform the benchmark from abstract code into an understandable workflow system.

## Training and evaluation

The repository includes a practical path from environment to evidence:

- a benchmark script for comparing random and heuristic policies
- a synthetic data path for training examples
- a lightweight SFT pipeline
- plotting and evaluation scripts
- committed output artifacts for inspection

That means the repo is not just saying "this environment could be useful." It is already instrumented to show whether policies improve and how their behavior changes.

The baseline results matter here. The heuristic outperforming random is a small but important proof that the environment has signal. It tells us the task is neither arbitrary nor completely flat.

## What makes the project distinctive

There are many agent demos that look polished but reduce the actual intelligence problem to formatting or calling tools in sequence.

This project is more specific than that. It targets a category of work where mistakes are subtle:

- a model can be fluent and still be wrong
- a model can be efficient and still violate a protected constraint
- a model can sound reasonable and still make poor delegation decisions
- a model can optimize one thread while harming the full trajectory

That makes this environment a better probe for practical assistant intelligence.

It treats executive support as a planning and negotiation problem, not as a thin email veneer over a chatbot.

## What the repo includes

From a project completeness perspective, the repository ties together several layers:

- environment definitions in `env/`
- OpenEnv serving support in `server/`
- local and interactive UI in `streamlit_app.py`
- heuristic inference logic in `inference.py`
- training and evaluation scripts in `scripts/`
- benchmark and training artifacts in `outputs/`
- documentation and submission framing in `README.md` and this blog

That full loop matters. It means someone visiting the project can understand the concept, run the simulator, inspect the decisions, and review the evidence in one place.

## Future directions

There is a lot of room to push the idea further:

- longer episodes with more branching
- hidden stakeholder preferences that emerge over time
- richer delegate trust and failure models
- more realistic calendar structures
- direct reinforcement learning on top of the current reward design
- stronger baseline agents for comparison

But even without those extensions, the current project already establishes a useful benchmark pattern: assistant work as sequential coordination under uncertainty.

## Final reflection

At its heart, this repo is trying to move assistant evaluation closer to reality.

Real work is full of tradeoffs that are not visible in one isolated message. Useful assistants need to understand when to say no, when to escalate, when to delegate, when to preserve a human commitment, and when a fast answer is worse than a thoughtful one.

`Executive Assistant Negotiation Env` turns those judgment calls into something structured enough to simulate, score, inspect, and train on.

That is what makes the project more than an inbox demo. It is a small environment for teaching models how to protect priorities in motion.
