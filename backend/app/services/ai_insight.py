import logging
import re
from datetime import datetime, timezone
from typing import Literal

import httpx

from app.core.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from app.schemas.dashboard import (
    AIInsightAudienceResponse,
    AIInsightResponse,
    MarketCoinResponse,
)
from app.schemas.onboarding import CryptoAsset, InvestorType


logger = logging.getLogger(__name__)

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_TIMEOUT = httpx.Timeout(
    connect=3.0,
    read=12.0,
    write=5.0,
    pool=3.0,
)

AIStatus = Literal["available", "fallback"]

ASSET_LABELS = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "solana": "Solana",
    "cardano": "Cardano",
    "ripple": "XRP",
}

INVESTOR_LABELS = {
    "hodler": "long-term HODL-focused investor",
    "day_trader": "short-term day-trader profile",
    "nft_collector": "NFT collector interested in network ecosystems",
}

INVESTOR_GUIDANCE = {
    "hodler": (
        "Emphasize long-term context, broader participation and avoiding "
        "overreaction to a single daily move."
    ),
    "day_trader": (
        "Emphasize short-term volatility, relative movement and liquidity context "
        "without giving a trading signal."
    ),
    "nft_collector": (
        "Emphasize network activity and ecosystem context without inventing "
        "NFT events or collection data."
    ),
}

UNSAFE_OUTPUT_PATTERN = re.compile(
    r"\b(?:you should (?:buy|sell|invest)|buy now|sell now|"
    r"guaranteed return|will reach \$|allocate \d+%|invest \d+%)",
    re.IGNORECASE,
)

SYSTEM_PROMPT = """You are CoinSight's concise crypto market analyst.
Write informational market commentary only, never personal financial advice.
Use only the investor profile, followed assets and live market observations supplied by the user message.
Never invent prices, events or unavailable data. Never tell the reader to buy, sell, allocate funds or act now.
Do not promise returns or make guaranteed price predictions.
Write 80 to 160 words in one to three short paragraphs, with no heading, bullets or markdown.
Adapt the perspective to the supplied investor type while keeping a neutral, professional tone."""


def generate_ai_insight(
    investor_type: InvestorType,
    selected_assets: list[CryptoAsset],
    market_data: list[MarketCoinResponse],
) -> tuple[AIInsightResponse, AIStatus]:
    generated_at = datetime.now(timezone.utc)

    if not OPENROUTER_API_KEY:
        return (
            _build_fallback_insight(
                investor_type,
                selected_assets,
                market_data,
                generated_at,
            ),
            "fallback",
        )

    try:
        with httpx.Client(timeout=OPENROUTER_TIMEOUT) as client:
            response = client.post(
                OPENROUTER_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": _build_user_prompt(
                                investor_type,
                                selected_assets,
                                market_data,
                            ),
                        },
                    ],
                    "temperature": 0.4,
                    "max_tokens": 260,
                    "stream": False,
                },
            )
            response.raise_for_status()
            payload = response.json()

        content = payload["choices"][0]["message"]["content"]
        content = _normalize_provider_content(content)

        return (
            AIInsightResponse(
                id=f"daily-{generated_at.date().isoformat()}",
                title="Your Daily AI Insight",
                content=content,
                generated_for=AIInsightAudienceResponse(
                    investor_type=investor_type,
                    crypto_assets=selected_assets,
                ),
                generated_at=generated_at,
            ),
            "available",
        )
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "OpenRouter insight is unavailable (HTTP %s).",
            exc.response.status_code,
        )
    except (
        httpx.HTTPError,
        IndexError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        logger.warning(
            "OpenRouter insight is unavailable (%s).",
            exc.__class__.__name__,
        )

    return (
        _build_fallback_insight(
            investor_type,
            selected_assets,
            market_data,
            generated_at,
        ),
        "fallback",
    )


def _build_user_prompt(
    investor_type: InvestorType,
    selected_assets: list[CryptoAsset],
    market_data: list[MarketCoinResponse],
) -> str:
    asset_names = ", ".join(ASSET_LABELS[asset] for asset in selected_assets)
    market_context = _format_market_context(market_data)

    return (
        f"Investor profile: {INVESTOR_LABELS[investor_type]}.\n"
        f"Followed assets: {asset_names}.\n"
        f"Profile guidance: {INVESTOR_GUIDANCE[investor_type]}\n"
        f"Live market observations:\n{market_context}\n"
        "Create today's concise personalized market perspective using only this context."
    )


def _format_market_context(market_data: list[MarketCoinResponse]) -> str:
    if not market_data:
        return "Live market data is unavailable. Do not mention current prices or movements."

    return "\n".join(
        (
            f"- {coin.name} ({coin.symbol.upper()}): "
            f"price {_format_usd(coin.current_price)}, "
            f"24-hour change {coin.price_change_percentage_24h:+.2f}%"
        )
        for coin in market_data
    )


def _format_usd(value: float) -> str:
    decimals = 4 if abs(value) < 1 else 2
    return f"${value:,.{decimals}f}"


def _normalize_provider_content(content: object) -> str:
    if not isinstance(content, str):
        raise TypeError("OpenRouter content must be text.")

    paragraphs = [
        " ".join(paragraph.split())
        for paragraph in content.strip().split("\n\n")
        if paragraph.strip()
    ][:3]
    normalized_content = "\n\n".join(paragraphs)
    words = normalized_content.split()

    if len(words) < 35 or UNSAFE_OUTPUT_PATTERN.search(normalized_content):
        raise ValueError("OpenRouter content did not pass output validation.")

    if len(words) > 160:
        normalized_content = " ".join(words[:160]).rstrip(".,;:") + "."

    return normalized_content


def _build_fallback_insight(
    investor_type: InvestorType,
    selected_assets: list[CryptoAsset],
    market_data: list[MarketCoinResponse],
    generated_at: datetime,
) -> AIInsightResponse:
    asset_names = [ASSET_LABELS[asset] for asset in selected_assets]
    readable_assets = _join_readable(asset_names)

    if market_data:
        changes = [coin.price_change_percentage_24h for coin in market_data]
        if any(change > 0 for change in changes) and any(change < 0 for change in changes):
            movement = "mixed short-term movement"
        elif all(change >= 0 for change in changes):
            movement = "broadly positive short-term movement"
        else:
            movement = "broadly negative short-term movement"

        observations = ", ".join(
            f"{coin.name} at {coin.price_change_percentage_24h:+.2f}% over 24 hours"
            for coin in market_data
        )
        opening = (
            f"{readable_assets} are showing {movement} in the available market data, "
            f"with {observations}."
        )
    else:
        opening = (
            f"Live price data for {readable_assets} is temporarily unavailable, so this "
            "perspective avoids making claims about current market movement."
        )

    profile_context = {
        "hodler": (
            "For a long-term HODL-focused profile, a single 24-hour change is more useful "
            "as context than as a standalone signal. Broader participation, liquidity and "
            "whether the followed assets maintain consistent network interest can provide "
            "a steadier frame for reviewing daily volatility. Comparing these measures "
            "across multiple periods can help separate temporary noise from more durable "
            "changes in market behavior."
        ),
        "day_trader": (
            "For a day-trader profile, differences in short-term direction and volatility "
            "can help frame which followed assets are moving most actively. Consistency, "
            "liquidity and changing momentum remain useful context, but these observations "
            "are not buy or sell signals. Comparing movement across more than one interval "
            "can help distinguish a brief fluctuation from a more persistent change in "
            "market activity."
        ),
        "nft_collector": (
            "For an NFT collector profile, daily token movement is only one part of the "
            "picture. Network participation, application activity and ecosystem engagement "
            "can add useful context without assuming that price changes reflect specific "
            "NFT developments. Reviewing these signals across multiple periods can offer a "
            "more balanced view of how the broader ecosystem is evolving."
        ),
    }[investor_type]

    content = (
        f"{opening}\n\n{profile_context} This market commentary is informational and "
        "does not account for individual financial circumstances."
    )

    return AIInsightResponse(
        id=f"daily-{generated_at.date().isoformat()}",
        title="Your Daily Market Insight",
        content=content,
        generated_for=AIInsightAudienceResponse(
            investor_type=investor_type,
            crypto_assets=selected_assets,
        ),
        generated_at=generated_at,
    )


def _join_readable(values: list[str]) -> str:
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return f"{', '.join(values[:-1])}, and {values[-1]}"
