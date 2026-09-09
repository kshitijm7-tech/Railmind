"""Runtime hardening for the running application (E08) — TRD §46/§47 Tier-1.

Authoritative scope (nothing more):

- **TRD §46 API Security (Tier-1 subset)**: CORS restrictions — configured
  exclusively through the environment (``RAILMIND_CORS_ALLOWED_ORIGINS``,
  comma-separated). The default is the SECURE one: no CORS headers at all
  (same-origin only); a wildcard default is never applied and ``*`` mixed
  with explicit origins is rejected at startup.
- **TRD §47 Observability (Tier-1)**: structured JSON logs — one line per
  request with timestamp/service/run_id/endpoint/method/status/duration_ms;
  latency tracked for the API, simulation and prediction operations (the
  §47 metrics list minus the solver/DB/queue items that do not exist here).
- **Request correlation (§18)**: a fresh UUID per request at the HTTP
  boundary (existing ``ApiMeta.requestId`` mechanism), attached to the log
  line and never merged with domain provenance.

No new telemetry framework (§47: OpenTelemetry/Prometheus are Tier 2+), no
persistence, no async jobs (§24/§25).
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

SERVICE_NAME = "railmind-backend"

#: TRD §47 metrics are tracked per-operation; the engine phase is derived
#: from the URL path so log lines carry the §19 "engine phase" metadata
#: without coupling middleware to engine internals.
_ENGINE_PHASES = (
    ("/maintenance/prioritize", "E02"),
    # Order matters: the specific E09 route precedes the general /plans/ E05
    # prefix so generation is attributed to the CP-SAT phase, not simulation.
    ("/plans/generate", "E09"),
    ("/plans/", "E05"),
    ("/scenarios/", "E05"),
    ("/predictions/", "E06"),
)

logger = logging.getLogger("railmind.api")


class RuntimeContext:
    """Process-wide runtime settings (E08 §16: one settings mechanism).

    A single frozen snapshot built once from the environment at startup —
    no second configuration framework, no per-request env reads, no secrets
    in source (TRD §46). ``cors_allowed_origins`` is empty by default
    (secure: same-origin only).
    """

    __slots__ = ("cors_allowed_origins",)

    def __init__(self, cors_allowed_origins: tuple = ()):
        self.cors_allowed_origins = tuple(cors_allowed_origins)

    @classmethod
    def from_env(cls, environ=None) -> "RuntimeContext":
        env = os.environ if environ is None else environ
        raw = (env.get("RAILMIND_CORS_ALLOWED_ORIGINS") or "").strip()
        if not raw:
            return cls(())
        if raw == "*":
            return cls(("*",))
        origins = tuple(o.strip() for o in raw.split(",") if o.strip())
        if "*" in origins and len(origins) > 1:
            raise ValueError(
                "RAILMIND_CORS_ALLOWED_ORIGINS mixes '*' with explicit "
                "origins; that weakens CORS — configure one or the other"
            )
        return cls(origins)


def engine_phase_for_path(path: str) -> str:
    """Engine phase label for a request path ("" when not engine-owned)."""
    for prefix, phase in _ENGINE_PHASES:
        if path.startswith(f"/api/v1{prefix}") or path.startswith(prefix):
            return phase
    return ""


def build_json_log(
    *,
    request_id: str,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    engine_phase: str = "",
) -> str:
    """One structured JSON log line (TRD §47 shape, deterministic field order).

    Carries request correlation + operation metadata only — never request
    payloads (§19).
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": SERVICE_NAME,
        "run_id": request_id,
        "method": method,
        "path": path,
        "status": status_code,
        "duration_ms": round(duration_ms, 3),
        "engine_phase": engine_phase,
    }
    return json.dumps(record, separators=(",", ":"))


def new_request_id() -> str:
    """Fresh request-correlation UUID (§18: HTTP-boundary identity).

    Uses the stdlib generator directly — no global-random mutation (the
    uuid module owns its own internal generator state and is the project's
    existing request-ID mechanism, system.py).
    """
    return str(uuid.uuid4())


def configure_logging() -> None:
    """Make the §47 structured logs actually visible at runtime.

    Idempotent. Without this, ``logger.info`` records would be dropped by
    Python's last-resort stderr handler (WARNING+ only) — the JSON lines
    would never reach the console in a default ``uvicorn app.main:app``
    run. A bare ``%(message)s`` formatter avoids double-wrapping the
    already-structured JSON payload.
    """
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # uvicorn's access logs stay separate


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    """TRD §47 Tier-1 observability at the HTTP boundary.

    Per request: correlate (request_id), time the operation, emit one
    structured JSON log line, and expose the id via response header
    ``X-Request-Id``. Domain semantics untouched — the middleware never
    reads or modifies request/response bodies.
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_id = new_request_id()
        request.state.request_id = request_id
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - started) * 1000.0
            logger.error(
                build_json_log(
                    request_id=request_id,
                    method=request.method,
                    path=request.url.path,
                    status_code=500,
                    duration_ms=duration_ms,
                    engine_phase=engine_phase_for_path(request.url.path),
                )
            )
            raise
        duration_ms = (time.perf_counter() - started) * 1000.0
        response.headers["X-Request-Id"] = request_id
        logger.info(
            build_json_log(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                engine_phase=engine_phase_for_path(request.url.path),
            )
        )
        return response


__all__ = [
    "RuntimeContext",
    "RequestObservabilityMiddleware",
    "build_json_log",
    "engine_phase_for_path",
    "new_request_id",
    "configure_logging",
    "SERVICE_NAME",
]
