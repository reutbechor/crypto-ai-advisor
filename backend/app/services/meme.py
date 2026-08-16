import logging
import secrets
from typing import Literal
from urllib.parse import urlsplit

import httpx
from pydantic import ValidationError

from app.data.memes import STATIC_CRYPTO_MEMES
from app.schemas.dashboard import MemeResponse


logger = logging.getLogger(__name__)

MEME_API_URL = "https://meme-api.com/gimme/CryptoCurrencyMemes/20"
MEME_API_TIMEOUT = httpx.Timeout(5.0, connect=3.0)
MEME_API_USER_AGENT = "CoinSight-AI/1.0 (coding-assignment demo)"
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_HOSTS = {"i.redd.it", "preview.redd.it", "i.imgur.com"}
ALLOWED_SOURCE_HOSTS = {"redd.it", "www.reddit.com", "reddit.com"}
BLOCKED_TITLE_TERMS = {
    "biden",
    "graphic",
    "hate",
    "killing",
    "murder",
    "politics",
    "russia",
    "trump",
    "war",
    "buy now",
    "guaranteed return",
    "price target",
    "sell now",
}

MemeStatus = Literal["available", "fallback", "unavailable"]


def _has_allowed_image_url(value: object) -> bool:
    if not isinstance(value, str):
        return False

    parsed = urlsplit(value)
    suffix = next(
        (extension for extension in ALLOWED_IMAGE_EXTENSIONS if parsed.path.lower().endswith(extension)),
        None,
    )
    return (
        parsed.scheme == "https"
        and parsed.hostname in ALLOWED_IMAGE_HOSTS
        and suffix is not None
    )


def _has_safe_title(title: str) -> bool:
    normalized_title = title.casefold()
    return not any(term in normalized_title for term in BLOCKED_TITLE_TERMS)


def _normalize_candidate(item: object) -> MemeResponse | None:
    if not isinstance(item, dict):
        return None

    if (
        item.get("nsfw") is not False
        or item.get("spoiler") is True
        or item.get("is_video") is True
        or item.get("is_gallery") is True
        or str(item.get("subreddit", "")).casefold() != "cryptocurrencymemes"
    ):
        return None

    title = str(item.get("title", "")).strip()
    image_url = item.get("url")
    source_url = item.get("postLink")
    if not title or not _has_safe_title(title) or not _has_allowed_image_url(image_url):
        return None

    if not isinstance(source_url, str):
        return None
    parsed_source = urlsplit(source_url)
    if parsed_source.scheme != "https" or parsed_source.hostname not in ALLOWED_SOURCE_HOSTS:
        return None

    post_id = parsed_source.path.strip("/").split("/")[-1]
    if not post_id:
        return None

    try:
        return MemeResponse(
            id=f"reddit-{post_id}",
            title=title[:180],
            image_url=image_url,
            source="Reddit · r/CryptoCurrencyMemes",
            source_url=source_url,
            alt_text=f"Crypto meme: {title}"[:240],
        )
    except ValidationError:
        return None


def _select_fallback() -> tuple[MemeResponse | None, MemeStatus]:
    try:
        return MemeResponse.model_validate(secrets.choice(STATIC_CRYPTO_MEMES)), "fallback"
    except (IndexError, TypeError, ValidationError) as exc:
        logger.warning("Local crypto meme fallback is unavailable (%s).", exc.__class__.__name__)
        return None, "unavailable"


def fetch_meme() -> tuple[MemeResponse | None, MemeStatus]:
    try:
        with httpx.Client(timeout=MEME_API_TIMEOUT) as client:
            response = client.get(
                MEME_API_URL,
                headers={
                    "Accept": "application/json",
                    "User-Agent": MEME_API_USER_AGENT,
                },
            )
            response.raise_for_status()
            payload = response.json()

        if not isinstance(payload, dict) or not isinstance(payload.get("memes"), list):
            raise ValueError("Unexpected meme provider response shape.")

        candidates = [
            meme
            for item in payload["memes"]
            if (meme := _normalize_candidate(item)) is not None
        ]
        if not candidates:
            raise ValueError("Meme provider returned no suitable images.")

        return secrets.choice(candidates), "available"
    except (httpx.HTTPError, TypeError, ValueError) as exc:
        logger.warning("External crypto meme is unavailable (%s).", exc.__class__.__name__)
        return _select_fallback()
