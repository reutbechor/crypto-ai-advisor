from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.schemas.feedback import (
    DashboardFeedbackResponse,
    FeedbackContentType,
    FeedbackVote,
)


def toggle_feedback(
    db: Session,
    user_id: int,
    content_type: FeedbackContentType,
    content_id: str,
    vote: FeedbackVote,
) -> Feedback | None:
    feedback = db.scalar(
        select(Feedback).where(
            Feedback.user_id == user_id,
            Feedback.content_type == content_type,
            Feedback.content_id == content_id,
        )
    )

    if feedback is not None and feedback.vote == vote:
        db.delete(feedback)
        db.commit()
        return None

    if feedback is None:
        feedback = Feedback(
            user_id=user_id,
            content_type=content_type,
            content_id=content_id,
            vote=vote,
        )
        db.add(feedback)
    else:
        feedback.vote = vote

    db.commit()
    db.refresh(feedback)
    return feedback


def get_feedback_state(db: Session, user_id: int) -> DashboardFeedbackResponse:
    rows = db.scalars(
        select(Feedback).where(Feedback.user_id == user_id)
    ).all()
    feedback = DashboardFeedbackResponse()

    for row in rows:
        getattr(feedback, row.content_type)[row.content_id] = row.vote

    return feedback
