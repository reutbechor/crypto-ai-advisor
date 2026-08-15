import logging
from typing import Literal

import httpx
from pydantic import ValidationError

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


def fetch_market_data(
    selected_assets: list[str],
) -> tuple[list[MarketCoinResponse], MarketStatus]:
    try:
        coin_ids = [COINGECKO_COIN_IDS[asset] for asset in selected_assets]

        with httpx.Client(timeout=COINGECKO_TIMEOUT) as client:
            response = client.get(
                COINGECKO_MARKETS_URL,
                params={
                    "vs_currency": "usd",
                    "ids": ",".join(coin_ids),
                    "price_change_percentage": "24h",
                    "sparkline": "false",
                },
                headers={
                    "Accept": "application/json",
                    "User-Agent": "CoinSight-AI/1.0",
                },
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
    except (httpx.HTTPError, KeyError, TypeError, ValueError, ValidationError) as exc:
        logger.warning(
            "CoinGecko market data is unavailable (%s).",
            exc.__class__.__name__,
        )
        return [], "unavailable"
