from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.auth import AuthUserResponse


CryptoAsset = Literal["bitcoin", "ethereum", "solana", "cardano", "ripple"]
InvestorType = Literal["hodler", "day_trader", "nft_collector"]
ContentPreference = Literal[
    "market_news",
    "coin_prices",
    "ai_insights",
    "fun",
]


class OnboardingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    crypto_assets: list[CryptoAsset] = Field(min_length=1)
    investor_type: InvestorType
    content_preferences: list[ContentPreference] = Field(min_length=1)

    @field_validator("crypto_assets", "content_preferences")
    @classmethod
    def reject_duplicates(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("Selections must not contain duplicates.")
        return values


class PreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    crypto_assets: list[CryptoAsset]
    investor_type: InvestorType
    content_preferences: list[ContentPreference]


class OnboardingResponse(BaseModel):
    message: str
    user: AuthUserResponse
    preferences: PreferenceResponse
