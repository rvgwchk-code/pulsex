from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    verification_id: str
    rating: int = Field(ge=1, le=5)
    role: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=2, max_length=120)
    tenure_range: str = Field(min_length=2, max_length=40)
    pros: str = Field(min_length=10, max_length=2000)
    cons: str = Field(min_length=10, max_length=2000)
    advice: str = Field(min_length=10, max_length=2000)


class PublicReview(BaseModel):
    id: str
    company_id: str
    rating: int
    role: str
    location: str
    tenure_range: str
    pros: str
    cons: str
    advice: str
    status: str
    verified: bool
    created_at: datetime


class ReportCreate(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class ResponseCreate(BaseModel):
    response: str = Field(min_length=10, max_length=2000)