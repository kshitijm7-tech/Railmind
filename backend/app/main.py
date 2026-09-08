from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.api.v1.endpoints.system import root_router, get_meta
from app.core.errors import DomainError, category_to_http_status
from app.api.models import ApiResponse, ApiError

app = FastAPI(title="RailMind Backend", version="1.0.0")

@app.exception_handler(DomainError)
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

app.include_router(root_router)
app.include_router(api_router, prefix="/api/v1")
