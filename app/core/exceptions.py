from typing import Any


class WaygoException(Exception):
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None, **kwargs: Any):
        self.detail = detail or self.__class__.detail
        self.extra = kwargs
        super().__init__(self.detail)


class NotFoundError(WaygoException):
    status_code = 404
    detail = "Resource not found"


class AlreadyExistsError(WaygoException):
    status_code = 409
    detail = "Resource already exists"


class UnauthorizedError(WaygoException):
    status_code = 401
    detail = "Authentication required"


class ForbiddenError(WaygoException):
    status_code = 403
    detail = "Insufficient permissions"


class ValidationError(WaygoException):
    status_code = 422
    detail = "Validation error"


class InvalidTokenError(WaygoException):
    status_code = 401
    detail = "Invalid or malformed token"


class TokenExpiredError(WaygoException):
    status_code = 401
    detail = "Token has expired"


class GeoValidationError(WaygoException):
    status_code = 400
    detail = "Location too far from place"


class DuplicateVisitError(WaygoException):
    status_code = 409
    detail = "User has already validated this place"


class InvalidCredentialsError(WaygoException):
    status_code = 401
    detail = "Invalid email or password"


class EmailNotVerifiedError(WaygoException):
    status_code = 403
    detail = "Email address not verified"


class RateLimitError(WaygoException):
    status_code = 429
    detail = "Too many requests"


class StorageError(WaygoException):
    status_code = 500
    detail = "Storage operation failed"
