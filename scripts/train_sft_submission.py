from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("OPENENV_LIGHT_MODE", "1")

from scripts.training_data import build_sft_text_rows


def main() -> None:
    try:
        import torch
        from datasets import Dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from trl import SFTConfig, SFTTrainer
    except ImportError as exc:
        raise SystemExit(
            "Install training extras first: pip install datasets transformers accelerate trl peft"
        ) from exc

    fast_local = os.getenv("FAST_LOCAL_TRAIN", "1") == "1"
    default_model = "sshleifer/tiny-gpt2" if fast_local else "Qwen/Qwen2.5-0.5B-Instruct"
    repeats = int(os.getenv("SFT_REPEATS_PER_SCENARIO", "1" if fast_local else "8"))
    max_steps = int(os.getenv("SFT_MAX_STEPS", "6" if fast_local else "40"))
    max_length = int(os.getenv("SFT_MAX_LENGTH", "320" if fast_local else "1024"))
    model_name = os.getenv("SFT_MODEL_NAME", default_model)
    output_dir = ROOT / "outputs" / "sft_run"
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = build_sft_text_rows(repeats_per_scenario=repeats)
    dataset = Dataset.from_list(rows)
    (output_dir / "dataset_preview.json").write_text(
        json.dumps(rows[:3], indent=2), encoding="utf-8"
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(model_name)

    config = SFTConfig(
        output_dir=str(output_dir),
        dataset_text_field="text",
        max_length=max_length,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1 if fast_local else 4,
        learning_rate=5e-5 if fast_local else 2e-5,
        logging_steps=1,
        save_steps=max_steps,
        save_strategy="steps",
        logging_strategy="steps",
        num_train_epochs=1,
        max_steps=max_steps,
        report_to="none",
        do_train=True,
        use_cpu=not torch.cuda.is_available(),
        remove_unused_columns=True,
        gradient_checkpointing=False,
        packing=False,
        dataloader_num_workers=0,
    )

    trainer = SFTTrainer(
        model=model,
        args=config,
        train_dataset=dataset,
        processing_class=tokenizer,
    )
    trainer.train()
    trainer.save_model(str(output_dir / "final_model"))
    tokenizer.save_pretrained(str(output_dir / "final_model"))


if __name__ == "__main__":
    main()
