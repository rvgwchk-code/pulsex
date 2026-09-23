from fastapi import APIRouter, Header, HTTPException, Query

from app import store
from app.schemas.companies import (
    CompanyPage,
    CompanySummary,
    VerificationRequest,
    VerificationResponse,
)

router = APIRouter()


@router.get("", response_model=list[CompanySummary])
def search_companies(query: str = Query(default="", max_length=120)):
    normalized = query.casefold().strip()
    return [
        company
        for company in store.companies
        if not normalized
        or normalized in company["name"].casefold()
        or normalized in company["domain"].casefold()
    ]


@router.get("/{company_id}", response_model=CompanyPage)
def get_company(company_id: str):
    company = next((item for item in store.companies if item["id"] == company_id), None)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    approved = [
        review
        for review in store.reviews.values()
        if review["company_id"] == company_id and review["status"] == "approved"
    ]
    return {
        **company,
        "review_count": len(approved),
        "average_rating": round(sum(item["rating"] for item in approved) / len(approved), 1)
        if approved
        else None,
        "verified_review_count": sum(item["verified"] for item in approved),
    }


@router.post("/{company_id}/verification", response_model=VerificationResponse)
def start_verification(
    company_id: str,
    payload: VerificationRequest,
    x_user_id: str = Header(default="demo-user"),
):
    if not any(company["id"] == company_id for company in store.companies):
        raise HTTPException(status_code=404, detail="Company not found")
    verification = {
        "id": store.new_id(),
        "user_id": x_user_id,
        "company_id": company_id,
        "method": payload.method,
        "status": "verified" if payload.method == "test-mode" else "pending",
        "verified_at": None,
    }
    store.verifications[verification["id"]] = verification
    return verification