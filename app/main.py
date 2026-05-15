from fastapi import FastAPI
from app.api.routes import router as api_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="Cloud Advisory Copilot (Cloud-Agnostic)",
    version="0.1.0",
    description="A cloud agnostic API that converts workload requirements into prioritized recommendations.",
)

# Include your existing routes
app.include_router(api_router)

# Add Prometheus instrumentation
Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True
).instrument(app).expose(app)