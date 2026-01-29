from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(
    title="Cloud Advisory Copilot (Cloud-Agnostic)",
    version="0.1.0",
    description="A cloud agnostic API that converts workload requirements into prioritized recommendations.",
)

app.include_router(api_router)