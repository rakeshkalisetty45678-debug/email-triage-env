# Under-2-Minute Demo Script

This project is `Executive Assistant Negotiation Env`, an OpenEnv environment for training LLMs on realistic executive-assistant work.

Instead of classifying one email at a time, the agent operates in a partially observable world with conflicting stakeholders, limited delegate capacity, and scarce meeting slots. It has to choose whether to reply, delegate, schedule, decline, clarify, or archive, and it must draft a short message that fits the situation.

The core challenge is long horizon reasoning. One bad scheduling choice can create a later conflict. One careless delegation can overload the wrong teammate. And protecting personal commitments matters just as much as handling urgent business issues.

We built the reward using composable OpenEnv rubrics for decision quality, priority calibration, coordination quality, communication quality, and final trajectory outcome. That gives dense feedback while still rewarding strong overall episode management.

For the baseline, we compare a random policy against a simple rule-based assistant and log the reward curves directly in the repo. The rule-based policy already beats random, which shows the environment provides a learnable signal.

The repo also includes a minimal Hugging Face TRL training script and Colab notebook, plus a Hugging Face Space deployment path through OpenEnv.

The goal is to train models that do better on real assistant tasks where negotiation, delegation, and planning all matter together.

