from datetime import UTC, datetime
from uuid import uuid4


def new_id() -> str:
    return str(uuid4())


companies = [
    {
        "id": "company-pulsex",
        "name": "PulseX Labs",
        "domain": "pulsex.example",
        "status": "approved",
        "created_at": datetime.now(UTC),
    },
    {
        "id": "company-northstar",
        "name": "Northstar Systems",
        "domain": "northstar.example",
        "status": "approved",
        "created_at": datetime.now(UTC),
    },
]

users: dict[str, dict] = {}
verifications: dict[str, dict] = {}
reviews: dict[str, dict] = {
    "review-demo": {
        "id": "review-demo",
        "company_id": "company-pulsex",
        "rating": 4,
        "role": "Product designer",
        "location": "Remote",
        "tenure_range": "1-2 years",
        "pros": "Clear product direction and thoughtful peers.",
        "cons": "Priorities can change quickly.",
        "advice": "Ask how product decisions are made day to day.",
        "status": "approved",
        "verified": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "author_id": "private-demo-author",
        "verification_id": "private-demo-verification",
    }
}
reports: dict[str, dict] = {}
responses: dict[str, dict] = {}
moderation_events: list[dict] = []