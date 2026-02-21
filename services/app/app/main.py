"""FastAPI application factory and router registration."""

from fastapi import FastAPI

from app.api.routers import api_router
from app.core.config import Settings, get_settings
from app.core.logger import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure the FastAPI application instance.

    Args:
        settings: Optional settings override for tests or custom runtime wiring.

    Returns:
        A configured :class:`fastapi.FastAPI` application.
    """
    resolved_settings = settings or get_settings()
    configure_logging(log_level=resolved_settings.log_level)

    application = FastAPI(
        title=resolved_settings.app_name,
        debug=resolved_settings.debug,
        version=resolved_settings.app_version,
    )
    application.include_router(api_router, prefix=resolved_settings.api_prefix)
    return application


app = create_app()
