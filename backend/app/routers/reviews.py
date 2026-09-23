from datetime import UTC, datetime

from fastapi import APIRouter, Header, HTTPException

from app import store
from app.schemas.reviews import PublicReview, ReportCreate, ResponseCreate, ReviewCreate

router = APIRouter()


def public_review(review: dict) -> dict:
    return {key: value for key, value in review.items() if key not in {"author_id", "verification_id"}}


@router.get("/companies/{company_id}/reviews", response_model=list[PublicReview])
def list_reviews(company_id: str):
    return [
        public_review(review)
        for review in store.reviews.values()
        if review["company_id"] == company_id and review["status"] == "approved"
    ]


@router.post("/companies/{company_id}/reviews", response_model=PublicReview, status_code=201)
def submit_review(
    company_id: str,
    payload: ReviewCreate,
    x_user_id: str = Header(default="demo-user"),
):
    verification = store.verifications.get(payload.verification_id)
    if not verification or verification["user_id"] != x_user_id or verification["company_id"] != company_id:
        raise HTTPException(status_code=403, detail="A matching employment verification is required")
    if verification["status"] != "verified":
        raise HTTPException(status_code=403, detail="Employment verification is not complete")
    if any(
        review["author_id"] == x_user_id
        and review["verification_id"] == payload.verification_id
        for review in store.reviews.values()
    ):
        raise HTTPException(status_code=409, detail="One review per employment episode is allowed")

    review = {
        "id": store.new_id(),
        "company_id": company_id,
        **payload.model_dump(exclude={"verification_id"}),
        "status": "pending",
        "verified": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "author_id": x_user_id,
        "verification_id": payload.verification_id,
    }
    store.reviews[review["id"]] = review
    return public_review(review)


@router.post("/reviews/{review_id}/report", status_code=201)
def report_review(review_id: str, payload: ReportCreate, x_user_id: str = Header(default="demo-user")):
    if review_id not in store.reviews:
        raise HTTPException(status_code=404, detail="Review not found")
    report = {"id": store.new_id(), "review_id": review_id, "reporter_id": x_user_id, "reason": payload.reason, "status": "open"}
    store.reports[report["id"]] = report
    return {"id": report["id"], "status": report["status"]}


@router.post("/reviews/{review_id}/response", status_code=201)
def respond_to_review(review_id: str, payload: ResponseCreate, x_user_id: str = Header(default="demo-company-user")):
    if review_id not in store.reviews:
        raise HTTPException(status_code=404, detail="Review not found")
    response = {"id": store.new_id(), "review_id": review_id, "company_user_id": x_user_id, "response": payload.response, "status": "published"}
    store.responses[response["id"]] = response
    return {"id": response["id"], "status": response["status"], "response": response["response"]}