from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

NSE_BASE = "https://www.nseindia.com"
OPTION_CHAIN_API = f"{NSE_BASE}/api/option-chain-indices"
DEFAULT_TIMEOUT = 20


@dataclass
class NSEClientConfig:
    symbol: str = "NIFTY"
    timeout: int = DEFAULT_TIMEOUT
    max_retries: int = 3
    sleep_between_retries: float = 1.5


class NSEOptionChainClient:
    def __init__(self, config: NSEClientConfig | None = None) -> None:
        self.config = config or NSEClientConfig()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "user-agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
                ),
                "accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.9",
                "referer": f"{NSE_BASE}/option-chain",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "connection": "keep-alive",
            }
        )
        self._bootstrapped = False

    def bootstrap(self) -> None:
        response = self.session.get(f"{NSE_BASE}/option-chain", timeout=self.config.timeout)
        response.raise_for_status()
        self._bootstrapped = True

    def fetch_option_chain(self, symbol: str | None = None) -> dict[str, Any]:
        if not self._bootstrapped:
            self.bootstrap()

        symbol = symbol or self.config.symbol
        last_error: Exception | None = None

        for attempt in range(1, self.config.max_retries + 1):
            try:
                response = self.session.get(
                    OPTION_CHAIN_API,
                    params={"symbol": symbol},
                    timeout=self.config.timeout,
                )

                if response.status_code in {401, 403}:
                    self.bootstrap()
                    response = self.session.get(
                        OPTION_CHAIN_API,
                        params={"symbol": symbol},
                        timeout=self.config.timeout,
                    )

                response.raise_for_status()
                return response.json()
            except Exception as exc:
                last_error = exc
                if attempt < self.config.max_retries:
                    time.sleep(self.config.sleep_between_retries)
                    self._bootstrapped = False
                    self.bootstrap()
                else:
                    break

        assert last_error is not None
        raise last_error
