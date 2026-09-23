from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin, companies, reviews

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