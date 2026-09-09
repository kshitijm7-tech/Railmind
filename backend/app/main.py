from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.api.v1.endpoints.system import root_router, get_meta
from app.core.errors import DomainError, category_to_http_status
from app.api.models import ApiResponse, ApiError
from app.core.runtime import (
    RuntimeContext,
    RequestObservabilityMiddleware,
    configure_logging,
)


def create_app(runtime: RuntimeContext = None) -> FastAPI:
    """Assemble the application (E08 testability: runtime is injectable).

    Default behavior is unchanged: the module-level ``app`` below is built
    from the environment exactly as before the factory existed.
    """
    runtime = runtime or RuntimeContext.from_env()

    # TRD §47: the structured JSON logs must actually be emitted at runtime.
    configure_logging()

    # --- E08 startup verification (§5/§15) ---------------------------------
    # The engine bridge must initialize with the application: importing it
    # here fails the process at startup (not on first request) if the
    # RailMind engine is missing — the service must never report healthy
    # when startup is broken.
    from app import engine_bridge  # noqa: F401 — startup probe

    application = FastAPI(title="RailMind Backend", version="1.0.0")

    # TRD §46 API Security — CORS restrictions: configured exclusively via
    # the environment (RAILMIND_CORS_ALLOWED_ORIGINS). Secure default = no
    # CORS middleware at all (same-origin only); a wildcard is never
    # silently applied.
    if runtime.cors_allowed_origins:
        allow_all = "*" in runtime.cors_allowed_origins
        application.add_middleware(
            CORSMiddleware,
            allow_origins=list(runtime.cors_allowed_origins),
            allow_credentials=not allow_all,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )

    # TRD §47 Tier-1 observability: structured JSON request logs with
    # latency, engine phase, and request correlation (X-Request-Id header).
    application.add_middleware(RequestObservabilityMiddleware)

    @application.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        http_status = category_to_http_status(exc.category)
        error_response = ApiResponse(
            meta=get_meta(),
            error=ApiError(
                code=exc.code,
                message=exc.message,
                httpStatus=http_status
            )
        )
        return JSONResponse(
            status_code=http_status,
            content=error_response.model_dump(exclude_none=True)
        )

    application.include_router(root_router)
    application.include_router(api_router, prefix="/api/v1")
    return application


# Module-level app: the canonical uvicorn target ("uvicorn app.main:app"),
# unchanged in behavior from the pre-E08 application.
configure_logging()
app = create_app()
