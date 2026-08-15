import logging
from typing import Literal

from pydantic import ValidationError

from app.data.news import STATIC_MARKET_NEWS
from app.schemas.dashboard import NewsItemResponse


logger = logging.getLogger(__name__)

NewsStatus = Literal["fallback", "unavailable"]


def select_personalized_news(
    selected_assets: list[str],
    limit: int = 4,
) -> tuple[list[NewsItemResponse], NewsStatus]:
    try:
        selected_asset_set = set(selected_assets)
        relevant_items = [
            item
            for item in STATIC_MARKET_NEWS
            if selected_asset_set.intersection(item["related_assets"])
        ]
        general_items = [
            item
            for item in STATIC_MARKET_NEWS
            if item["related_assets"] == ["general"]
        ]

        selected_items = []
        selected_ids = set()
        for item in (*relevant_items, *general_items):
            if item["id"] in selected_ids:
                continue
            selected_items.append(NewsItemResponse.model_validate(item))
            selected_ids.add(item["id"])
            if len(selected_items) == limit:
                break

        return selected_items, "fallback"
    except (KeyError, TypeError, ValidationError) as exc:
        logger.warning(
            "Static market news is unavailable (%s).",
            exc.__class__.__name__,
        )
        return [], "unavailable"
