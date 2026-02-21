from fastapi import FastAPI

from app.api.routers import jobs, metrics, monitors, tasks


def create_app() -> FastAPI:
    app = FastAPI(title="WebIntel API")

    api_routers = [tasks.router, jobs.router, monitors.router]
    for router in api_routers:
        app.include_router(router, prefix="/api")

    app.include_router(metrics.router)

    @app.get("/health")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
