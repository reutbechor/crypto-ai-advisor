from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "content_type",
            "content_id",
            name="uq_feedback_user_content",
        ),
        CheckConstraint(
            "content_type IN ('news', 'ai_insight', 'meme')",
            name="ck_feedback_content_type",
        ),
        CheckConstraint(
            "vote IN ('up', 'down')",
            name="ck_feedback_vote",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_type: Mapped[str] = mapped_column(String(30), nullable=False)
    content_id: Mapped[str] = mapped_column(String(180), nullable=False)
    vote: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
