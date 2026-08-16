from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback import toggle_feedback


router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.put("", response_model=FeedbackResponse)
def update_feedback(
    payload: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    feedback = toggle_feedback(
        db,
        current_user.id,
        payload.content_type,
        payload.content_id,
        payload.vote,
    )

    return FeedbackResponse(
        content_type=payload.content_type,
        content_id=payload.content_id,
        vote=feedback.vote if feedback is not None else None,
    )
