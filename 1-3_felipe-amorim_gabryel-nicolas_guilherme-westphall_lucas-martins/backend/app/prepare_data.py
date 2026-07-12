"""Build the prepared feature artifact required by the API at startup."""
from __future__ import annotations

import os
from pathlib import Path

from app.data_prep import build_order_features


DEFAULT_RAW_DATA_DIR = Path(__file__).resolve().parents[2] / "dataset"
DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "prepared_orders.jsonl"


def main() -> None:
    raw_dir = Path(os.getenv("RAW_DATA_DIR", DEFAULT_RAW_DATA_DIR))
    output_path = Path(os.getenv("PREPARED_FEATURES_PATH", DEFAULT_OUTPUT_PATH))

    if output_path.is_file() and output_path.stat().st_size > 0:
        print(f"Prepared data already exists at {output_path}")
        return

    if not raw_dir.is_dir():
        raise SystemExit(f"Raw data directory not found: {raw_dir}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = build_order_features(raw_dir, output_path)
    print(
        "Prepared "
        f"{summary.total_orders} delivered orders "
        f"({summary.delayed_count} delayed) at {summary.output}"
    )


if __name__ == "__main__":
    main()
