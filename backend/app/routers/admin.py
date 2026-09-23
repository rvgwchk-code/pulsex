from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app import store
from app.routers.reviews import public_review

router = APIRouter()


class ModerationUpdate(BaseModel):
    action: str = Field(pattern="^(approved|rejected|request-edit|appealed)$")
    reason: str = Field(min_length=5, max_length=500)


@router.get("/moderation")
def moderation_queue():
    return [public_review(review) for review in store.reviews.values() if review["status"] == "pending"]


@router.patch("/reviews/{review_id}")
def moderate_review(review_id: str, payload: ModerationUpdate):
    review = store.reviews.get(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    status = "pending" if payload.action == "request-edit" else payload.action
    review["status"] = status
    store.moderation_events.append({"review_id": review_id, "action": payload.action, "reason": payload.reason})
    return {"id": review_id, "status": status}