from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, SessionLocal, engine
from app.models.entities import Company
from app.routers import admin, auth, companies, reviews


def initialize_database():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.query(Company).first():
            db.add_all(
                [
                    Company(id="company-pulsex", name="PulseX Labs", domain="pulsex.example"),
                    Company(id="company-northstar", name="Northstar Systems", domain="northstar.example"),
                ]
            )
            db.commit()


initialize_database()

app = FastAPI(
    title="PulseX API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "pulsex-api",
    }


app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(reviews.router, tags=["reviews"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])