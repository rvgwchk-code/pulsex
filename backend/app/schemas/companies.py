from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompanySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    domain: str
    status: str


class CompanyPage(CompanySummary):
    review_count: int
    average_rating: float | None
    verified_review_count: int
    created_at: datetime


class VerificationRequest(BaseModel):
    method: str = "test-mode"


class VerificationResponse(BaseModel):
    id: str
    company_id: str
    status: str
    method: str