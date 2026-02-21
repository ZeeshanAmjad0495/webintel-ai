from fastapi import FastAPI

from app.api.routers import jobs, metrics, monitors, tasks

app = FastAPI(title="WebIntel API")
app.include_router(tasks.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(monitors.router, prefix="/api")
app.include_router(metrics.router)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
