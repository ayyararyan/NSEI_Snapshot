from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


def snapshot_paths(base_dir: Path, symbol: str, captured_at: datetime) -> tuple[Path, Path]:
    day = captured_at.strftime("%Y-%m-%d")
    stamp = captured_at.strftime("%H%M%S")
    raw_dir = base_dir / "data" / "raw" / "option_chain" / day / symbol
    processed_dir = base_dir / "data" / "processed" / "option_chain" / f"date={day}" / f"symbol={symbol}"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir / f"{stamp}.json", processed_dir / f"{stamp}.parquet"


def write_raw_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_parquet(path: Path, frame: pd.DataFrame) -> None:
    frame.to_parquet(path, index=False)
