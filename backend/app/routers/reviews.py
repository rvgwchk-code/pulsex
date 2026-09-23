from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user, new_id, require_roles
from app.db import get_db
from app.models.entities import Company, CompanyResponse, EmploymentVerification, Report, Review, User
from app.schemas.reviews import PublicReview, ReportCreate, ResponseCreate, ReviewCreate

router = APIRouter()


def public_review(review: Review) -> dict:
    return {
        "id": review.id,
        "company_id": review.company_id,
        "rating": review.rating,
        "role": review.role,
        "location": review.location,
        "tenure_range": review.tenure_range,
        "pros": review.pros,
        "cons": review.cons,
        "advice": review.advice,
        "status": review.status,
        "verified": review.verified,
        "created_at": review.created_at,
    }


@router.get("/companies/{company_id}/reviews", response_model=list[PublicReview])
def list_reviews(company_id: str, db: Session = Depends(get_db)):
    return [public_review(review) for review in db.query(Review).filter(Review.company_id == company_id, Review.status == "approved").all()]


@router.post("/companies/{company_id}/reviews", response_model=PublicReview, status_code=201)
def submit_review(
    company_id: str,
    payload: ReviewCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verification = db.get(EmploymentVerification, payload.verification_id)
    if not verification or verification.user_id != user.id or verification.company_id != company_id:
        raise HTTPException(status_code=403, detail="A matching employment verification is required")
    if verification.status != "verified":
        raise HTTPException(status_code=403, detail="Employment verification is not complete")
    if db.query(Review).filter(Review.author_id == user.id, Review.verification_id == payload.verification_id).first():
        raise HTTPException(status_code=409, detail="One review per employment episode is allowed")

    review = Review(
        id=new_id(),
        company_id=company_id,
        **payload.model_dump(exclude={"verification_id"}),
        status="pending",
        verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        author_id=user.id,
        verification_id=payload.verification_id,
    )
    db.add(review)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="One review per employment episode is allowed")
    return public_review(review)


@router.post("/reviews/{review_id}/report", status_code=201)
def report_review(review_id: str, payload: ReportCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.get(Review, review_id):
        raise HTTPException(status_code=404, detail="Review not found")
    report = Report(id=new_id(), review_id=review_id, reporter_id=user.id, reason=payload.reason, status="open")
    db.add(report)
    db.commit()
    return {"id": report.id, "status": report.status}


@router.post("/reviews/{review_id}/response", status_code=201)
def respond_to_review(review_id: str, payload: ResponseCreate, user: User = Depends(require_roles("company", "admin")), db: Session = Depends(get_db)):
    if not db.get(Review, review_id):
        raise HTTPException(status_code=404, detail="Review not found")
    response = CompanyResponse(id=new_id(), review_id=review_id, company_user_id=user.id, response=payload.response, status="published")
    db.add(response)
    db.commit()
    return {"id": response.id, "status": response.status, "response": response.response}