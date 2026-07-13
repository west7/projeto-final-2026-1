"""Build the prepared feature artifact required by the API at startup."""
from __future__ import annotations

import os
from pathlib import Path

from app.data_prep import build_order_features, load_prepared_features


DEFAULT_RAW_DATA_DIR = Path(__file__).resolve().parents[2] / "dataset"
DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "prepared_orders.jsonl"


def main() -> None:
    raw_dir = Path(os.getenv("RAW_DATA_DIR", DEFAULT_RAW_DATA_DIR))
    output_path = Path(os.getenv("PREPARED_FEATURES_PATH", DEFAULT_OUTPUT_PATH))

    if _is_valid_artifact(output_path):
        print(f"Prepared data already exists at {output_path}")
        return

    if not raw_dir.is_dir():
        raise SystemExit(f"Raw data directory not found: {raw_dir}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    try:
        summary = build_order_features(raw_dir, temporary_path)
        if summary.total_orders == 0:
            raise RuntimeError("prepared dataset is empty")
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)
    print(
        "Prepared "
        f"{summary.total_orders} delivered orders "
        f"({summary.delayed_count} delayed) at {output_path}"
    )


def _is_valid_artifact(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    try:
        return bool(load_prepared_features(path))
    except (OSError, TypeError, ValueError):
        return False


if __name__ == "__main__":
    main()
