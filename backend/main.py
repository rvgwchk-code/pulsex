from fastapi import FastAPI

app = FastAPI(
    title="PulseX API",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "pulsex-api",
    }