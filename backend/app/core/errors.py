from enum import Enum

class ErrorCategory(str, Enum):
    VALIDATION = "VALIDATION"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    INTERNAL = "INTERNAL"
    BAD_REQUEST = "BAD_REQUEST"

class DomainError(Exception):
    def __init__(self, message: str, category: ErrorCategory, code: str):
        self.message = message
        self.category = category
        self.code = code
        super().__init__(self.message)

def category_to_http_status(category: ErrorCategory) -> int:
    mapping = {
        ErrorCategory.VALIDATION: 400,
        ErrorCategory.BAD_REQUEST: 400,
        ErrorCategory.NOT_FOUND: 404,
        ErrorCategory.UNAUTHORIZED: 401,
        ErrorCategory.FORBIDDEN: 403,
        ErrorCategory.CONFLICT: 409,
        ErrorCategory.INTERNAL: 500,
    }
    return mapping.get(category, 500)
