#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nsei.collector import collect_option_chain_snapshot


def within_market_hours(now: datetime, start_hhmm: str, end_hhmm: str) -> bool:
    current = now.strftime("%H:%M")
    return start_hhmm <= current <= end_hhmm


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect NSE option-chain snapshots at 1-minute frequency")
    parser.add_argument("--symbol", default="NIFTY")
    parser.add_argument("--interval-seconds", type=int, default=60)
    parser.add_argument("--start", default="09:14")
    parser.add_argument("--end", default="15:31")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"option_chain_{datetime.now().strftime('%Y-%m-%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler(sys.stdout)],
    )

    while True:
        now = datetime.now()

        if args.once:
            result = collect_option_chain_snapshot(ROOT, symbol=args.symbol)
            logging.info("Captured snapshot: %s", result)
            return

        if within_market_hours(now, args.start, args.end):
            try:
                result = collect_option_chain_snapshot(ROOT, symbol=args.symbol)
                logging.info("Captured snapshot: %s", result)
            except Exception as exc:
                logging.exception("Snapshot fetch failed: %s", exc)
        else:
            logging.info("Outside market window, sleeping")

        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
