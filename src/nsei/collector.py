from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .client import NSEOptionChainClient
from .normalize import normalize_option_chain
from .storage import snapshot_paths, write_parquet, write_raw_json


def collect_option_chain_snapshot(base_dir: str | Path, symbol: str = "NIFTY") -> dict[str, Any]:
    base_path = Path(base_dir)
    captured_at = datetime.now()
    client = NSEOptionChainClient()
    payload = client.fetch_option_chain(symbol=symbol)
    frame = normalize_option_chain(payload, captured_at=captured_at)
    raw_path, parquet_path = snapshot_paths(base_path, symbol=symbol, captured_at=captured_at)
    write_raw_json(raw_path, payload)
    write_parquet(parquet_path, frame)

    return {
        "captured_at": captured_at.isoformat(),
        "symbol": symbol,
        "rows": int(len(frame)),
        "raw_path": str(raw_path),
        "parquet_path": str(parquet_path),
    }
