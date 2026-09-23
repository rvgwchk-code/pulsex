from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_user, new_id
from app.db import get_db
from app.models.entities import Company, EmploymentVerification, Review, User
from app.schemas.companies import (
    CompanyPage,
    CompanySummary,
    VerificationRequest,
    VerificationResponse,
)

router = APIRouter()


@router.get("", response_model=list[CompanySummary])
def search_companies(query: str = Query(default="", max_length=120), db: Session = Depends(get_db)):
    normalized = query.casefold().strip()
    statement = db.query(Company).filter(Company.status == "approved")
    if normalized:
        statement = statement.filter(or_(Company.name.ilike(f"%{normalized}%"), Company.domain.ilike(f"%{normalized}%")))
    return statement.order_by(Company.name).all()


@router.get("/{company_id}", response_model=CompanyPage)
def get_company(company_id: str, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    approved = db.query(Review).filter(Review.company_id == company_id, Review.status == "approved").all()
    return {
        "id": company.id,
        "name": company.name,
        "domain": company.domain,
        "status": company.status,
        "created_at": company.created_at,
        "review_count": len(approved),
        "average_rating": round(sum(item["rating"] for item in approved) / len(approved), 1)
        if approved
        else None,
        "verified_review_count": sum(item.verified for item in approved),
    }


@router.post("/{company_id}/verification", response_model=VerificationResponse)
def start_verification(
    company_id: str,
    payload: VerificationRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not db.get(Company, company_id):
        raise HTTPException(status_code=404, detail="Company not found")
    verification = {
        "id": new_id(),
        "user_id": user.id,
        "company_id": company_id,
        "method": payload.method,
        "status": "verified" if payload.method == "test-mode" else "pending",
        "verified_at": datetime.utcnow() if payload.method == "test-mode" else None,
    }
    record = EmploymentVerification(**verification)
    db.add(record)
    db.commit()
    return record