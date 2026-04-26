from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent


def _load_state(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Trainer state not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _draw_line_plot(series, title, label, out_path: Path) -> None:
    width, height = 1000, 560
    image = Image.new("RGB", (width, height), "#fbfaf7")
    draw = ImageDraw.Draw(image)
    axis_color = "#1f2937"
    line_color = "#0f766e"
    grid_color = "#d6d3d1"
    margin_left, margin_right, margin_top, margin_bottom = 90, 40, 50, 80
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    draw.text((margin_left, 15), title, fill=axis_color)

    max_value = max(v for _, v in series) if series else 1.0
    min_value = min(v for _, v in series) if series else 0.0
    span = max(max_value - min_value, 1e-6)

    for tick in range(6):
        y = margin_top + int(plot_h * tick / 5)
        draw.line((margin_left, y, width - margin_right, y), fill=grid_color, width=1)
        value = max_value - span * tick / 5
        draw.text((20, y - 8), f"{value:.3f}", fill=axis_color)

    draw.line((margin_left, margin_top, margin_left, height - margin_bottom), fill=axis_color, width=2)
    draw.line((margin_left, height - margin_bottom, width - margin_right, height - margin_bottom), fill=axis_color, width=2)

    if series:
        points = []
        last_step = series[-1][0]
        for step, value in series:
            x = margin_left + int(plot_w * step / max(last_step, 1))
            y = margin_top + int((max_value - value) / span * plot_h)
            points.append((x, y))
        draw.line(points, fill=line_color, width=4)

    draw.text((margin_left + 350, height - 40), "Training step", fill=axis_color)
    draw.text((15, margin_top - 10), label, fill=axis_color)
    image.save(out_path)


def main() -> None:
    run_dir = ROOT / "outputs" / "sft_run"
    state = _load_state(run_dir / "trainer_state.json")
    log_history = state.get("log_history", [])

    loss_series = [
        (int(item["step"]), float(item["loss"]))
        for item in log_history
        if "loss" in item and "step" in item
    ]

    if not loss_series:
        raise SystemExit("No loss values found in trainer_state.json yet.")

    out_path = run_dir / "training_loss_curve.png"
    _draw_line_plot(
        loss_series,
        "SFT Training Loss Over Time",
        "Loss",
        out_path,
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

