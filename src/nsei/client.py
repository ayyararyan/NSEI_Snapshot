from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
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
        referer = f"{NSE_BASE}/option-chain?symbol={self.config.symbol}"
        self.session.headers.update(
            {
                "user-agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
                ),
                "accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.9",
                "referer": referer,
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "connection": "keep-alive",
            }
        )
        self._bootstrapped = False

    def bootstrap(self) -> None:
        url = f"{NSE_BASE}/option-chain?symbol={self.config.symbol}"
        response = self.session.get(url, timeout=self.config.timeout)
        response.raise_for_status()
        self._bootstrapped = True

    def _playwright_fetch(self, symbol: str) -> dict[str, Any]:
        project_root = Path(__file__).resolve().parents[2]
        script = project_root / "scripts" / "fetch_option_chain_playwright.js"
        result = subprocess.run(
            ["node", str(script), symbol],
            capture_output=True,
            text=True,
            timeout=90,
            check=True,
        )
        payload = json.loads(result.stdout or "{}")
        if not isinstance(payload, dict):
            raise RuntimeError("Unexpected Playwright payload shape from NSE")
        return payload

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
                payload = response.json()
                if isinstance(payload, dict) and payload:
                    return payload
            except Exception as exc:
                last_error = exc

            try:
                payload = self._playwright_fetch(symbol)
                if isinstance(payload, dict) and payload:
                    return payload
            except Exception as exc:
                last_error = exc

            if attempt < self.config.max_retries:
                time.sleep(self.config.sleep_between_retries)
                self._bootstrapped = False
                self.bootstrap()
            else:
                break

        if last_error is None:
            raise RuntimeError("NSE returned empty payload after retries")
        raise last_error
