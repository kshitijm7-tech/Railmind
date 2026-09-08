from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginationMeta(BaseModel):
    totalItems: int
    page: int
    pageSize: int
    totalPages: int

class ApiMeta(BaseModel):
    timestamp: str
    requestId: str
    version: str

class ApiError(BaseModel):
    code: str
    message: str
    httpStatus: int

class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    meta: ApiMeta
    error: Optional[ApiError] = None

class ApiListResponse(BaseModel, Generic[T]):
    data: Optional[List[T]] = None
    pagination: Optional[PaginationMeta] = None
    meta: ApiMeta
    error: Optional[ApiError] = None
