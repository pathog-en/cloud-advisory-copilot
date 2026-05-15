print ("Loading App Main File")

from fastapi import FastAPI
from app.api.routes import router as api_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="Cloud Advisory Copilot (Cloud-Agnostic)",
    version="0.1.0",
    description="A cloud agnostic API that converts workload requirements into prioritized recommendations.",
)

# 1. Include routes FIRST
app.include_router(api_router)

# 2. THEN instrument (important)
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True
)

instrumentator.instrument(app)
instrumentator.expose(app)