from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


FeedbackContentType = Literal["news", "ai_insight", "meme"]
FeedbackVote = Literal["up", "down"]


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content_type: FeedbackContentType
    content_id: str = Field(min_length=1, max_length=180)
    vote: FeedbackVote

    @field_validator("content_id")
    @classmethod
    def normalize_content_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("content_id must not be blank.")
        return normalized


class FeedbackResponse(BaseModel):
    content_type: FeedbackContentType
    content_id: str
    vote: FeedbackVote | None


class DashboardFeedbackResponse(BaseModel):
    news: dict[str, FeedbackVote] = Field(default_factory=dict)
    ai_insight: dict[str, FeedbackVote] = Field(default_factory=dict)
    meme: dict[str, FeedbackVote] = Field(default_factory=dict)
