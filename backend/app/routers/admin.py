from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user, new_id, require_roles
from app.db import get_db
from app.models.entities import ModerationEvent, Review, User
from app.routers.reviews import public_review

router = APIRouter()


class ModerationUpdate(BaseModel):
    action: str = Field(pattern="^(approved|rejected|request-edit|appealed)$")
    reason: str = Field(min_length=5, max_length=500)


@router.get("/moderation")
def moderation_queue(db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    return [public_review(review) for review in db.query(Review).filter(Review.status == "pending").all()]


@router.patch("/reviews/{review_id}")
def moderate_review(review_id: str, payload: ModerationUpdate, user: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    status = "pending" if payload.action == "request-edit" else payload.action
    review.status = status
    db.add(ModerationEvent(id=new_id(), review_id=review_id, moderator_id=user.id, action=payload.action, reason=payload.reason))
    db.commit()
    return {"id": review_id, "status": status}