from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Router

from backend.app.api.v1.router import api_router
from backend.app.api.error_handlers import register_error_handlers
from backend.app.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(
        title="Content Matrix API",
        version=resolved_settings.app_version,
        debug=resolved_settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)

    @app.get("/health")
    def health() -> dict[str, str | bool]:
        return {
            "status": "ok",
            "app": "content-matrix",
            "version": resolved_settings.app_version,
            "mode": "mock" if resolved_settings.llm_mock_mode else resolved_settings.llm_provider,
        }

    app.include_router(api_router, prefix=resolved_settings.api_v1_prefix)
    if not api_router.routes:
        app.mount(resolved_settings.api_v1_prefix, Router(), name="api_v1")
    return app


app = create_app()
