import logging
import re
from typing import Literal

import httpx
from pydantic import ValidationError

from app.core.config import COINGECKO_API_KEY
from app.schemas.dashboard import MarketCoinResponse


logger = logging.getLogger(__name__)

COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"
COINGECKO_TIMEOUT = httpx.Timeout(5.0, connect=3.0)
COINGECKO_COIN_IDS = {
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "solana": "solana",
    "cardano": "cardano",
    "ripple": "ripple",
}

MarketStatus = Literal["available", "unavailable"]
MAX_ERROR_RESPONSE_LENGTH = 240
BEARER_VALUE_PATTERN = re.compile(r"(?i)\bbearer\s+[^\s,;\"'}]+")
SENSITIVE_RESPONSE_PATTERN = re.compile(
    r"(?i)(api[-_ ]?key|authorization|bearer|token)([\s\"':=]+)([^\s,\"'}]+)"
)


def _sanitize_error_response(response: httpx.Response) -> str:
    message = " ".join(response.text.split())
    if COINGECKO_API_KEY:
        message = message.replace(COINGECKO_API_KEY, "[REDACTED]")
    message = BEARER_VALUE_PATTERN.sub("Bearer [REDACTED]", message)
    message = SENSITIVE_RESPONSE_PATTERN.sub(
        lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]",
        message,
    )
    return (message or response.reason_phrase or "unavailable")[
        :MAX_ERROR_RESPONSE_LENGTH
    ]


def fetch_market_data(
    selected_assets: list[str],
) -> tuple[list[MarketCoinResponse], MarketStatus]:
    try:
        coin_ids = [COINGECKO_COIN_IDS[asset] for asset in selected_assets]
        headers = {
            "Accept": "application/json",
            "User-Agent": "CoinSight-AI/1.0",
        }
        if COINGECKO_API_KEY:
            headers["x-cg-demo-api-key"] = COINGECKO_API_KEY

        with httpx.Client(timeout=COINGECKO_TIMEOUT) as client:
            response = client.get(
                COINGECKO_MARKETS_URL,
                params={
                    "vs_currency": "usd",
                    "ids": ",".join(coin_ids),
                    "price_change_percentage": "24h",
                    "sparkline": "false",
                },
                headers=headers,
            )
            response.raise_for_status()
            payload = response.json()

        if not isinstance(payload, list):
            raise ValueError("Unexpected CoinGecko response shape.")

        requested_ids = set(coin_ids)
        coins_by_id = {
            coin.id: coin
            for item in payload
            if isinstance(item, dict) and item.get("id") in requested_ids
            for coin in [MarketCoinResponse.model_validate(item)]
        }

        if set(coins_by_id) != requested_ids:
            raise ValueError("CoinGecko response did not contain all requested coins.")

        return [coins_by_id[coin_id] for coin_id in coin_ids], "available"
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "CoinGecko request failed: status=%s url=%s response=%s",
            exc.response.status_code,
            exc.request.url.copy_with(query=None),
            _sanitize_error_response(exc.response),
        )
        return [], "unavailable"
    except (httpx.HTTPError, KeyError, TypeError, ValueError, ValidationError) as exc:
        logger.warning(
            "CoinGecko market data is unavailable (%s).",
            exc.__class__.__name__,
        )
        return [], "unavailable"
