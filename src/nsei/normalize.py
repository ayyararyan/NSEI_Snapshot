from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd


def normalize_option_chain(payload: dict[str, Any], captured_at: datetime) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    symbol = payload.get("records", {}).get("underlying")
    timestamp = payload.get("records", {}).get("timestamp")
    data = payload.get("records", {}).get("data", [])

    for entry in data:
        expiry = entry.get("expiryDate")
        strike = entry.get("strikePrice")
        for option_type in ("CE", "PE"):
            leg = entry.get(option_type)
            if not leg:
                continue
            records.append(
                {
                    "captured_at": captured_at.isoformat(),
                    "exchange_timestamp": timestamp,
                    "symbol": symbol,
                    "expiry": expiry,
                    "strike_price": strike,
                    "option_type": option_type,
                    "open_interest": leg.get("openInterest"),
                    "change_in_oi": leg.get("changeinOpenInterest"),
                    "pchange_in_oi": leg.get("pchangeinOpenInterest"),
                    "total_traded_volume": leg.get("totalTradedVolume"),
                    "implied_volatility": leg.get("impliedVolatility"),
                    "last_price": leg.get("lastPrice"),
                    "change": leg.get("change"),
                    "pchange": leg.get("pChange"),
                    "bid_qty": leg.get("bidQty"),
                    "bid_price": leg.get("bidprice"),
                    "ask_qty": leg.get("askQty"),
                    "ask_price": leg.get("askPrice"),
                    "underlying_value": leg.get("underlyingValue"),
                }
            )

    return pd.DataFrame.from_records(records)
