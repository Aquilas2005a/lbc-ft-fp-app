from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.accounts import router as accounts_router
from app.api.alerts import router as alerts_router
from app.api.anomaly import router as anomaly_router
from app.api.audit_logs import router as audit_logs_router
from app.api.clients import router as clients_router
from app.api.health import router as health_router
from app.api.screening import router as screening_router
from app.api.seed import router as seed_router
from app.api.transactions import router as transactions_router
from app.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title="Application LBC/FT/FP API",
        description=(
            "API de filtrage clients et transactions pour la conformite "
            "LBC/FT/FP."
        ),
        version=__version__,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        # Keep local development robust when CORS_ORIGINS is overridden by
        # an environment variable that omits one loopback hostname.
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):5173$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health router: expose both the public /health endpoint (documented
    # since T07, checked by test_health_endpoint_returns_ok) and the
    # versioned /api/v1/health endpoint. Not a duplicate: two intentional
    # entry points for the same router, this is supported by FastAPI.
    app.include_router(health_router)
    app.include_router(health_router, prefix=settings.api_prefix)

    app.include_router(clients_router, prefix=settings.api_prefix)
    app.include_router(accounts_router, prefix=settings.api_prefix)
    app.include_router(transactions_router, prefix=settings.api_prefix)
    app.include_router(screening_router, prefix=settings.api_prefix)
    app.include_router(alerts_router, prefix=settings.api_prefix)
    app.include_router(audit_logs_router, prefix=settings.api_prefix)
    app.include_router(seed_router, prefix=settings.api_prefix)
    app.include_router(anomaly_router, prefix=settings.api_prefix)

    @app.get("/", tags=["root"])
    def root() -> dict[str, str]:
        return {
            "service": settings.app_name,
            "version": __version__,
            "health": "/health",
            "health_db": "/health/db",
            "health_v1": f"{settings.api_prefix}/health",
            "docs": "/docs",
        }

    return app


app = create_app()
