"""
app/core/exceptions.py
──────────────────────
Domain-level exceptions. These are raised by application services and caught by
the API layer's exception handlers to produce proper HTTP error responses.

By keeping exceptions framework-agnostic, the domain/application layers stay
independent of FastAPI.
"""


class TaskFlowException(Exception):
    """Base exception for all TaskFlow domain errors."""

    def __init__(self, message: str = "an error occurred"):
        self.message = message
        super().__init__(self.message)


class ValidationError(TaskFlowException):
    """Raised when input validation fails. Carries a dict of field-level errors."""

    def __init__(self, fields: dict[str, str]):
        self.fields = fields
        super().__init__("validation failed")


class AuthenticationError(TaskFlowException):
    """Raised when credentials are invalid or token is missing/expired (→ 401)."""

    def __init__(self, message: str = "invalid credentials"):
        super().__init__(message)


class AuthorizationError(TaskFlowException):
    """Raised when the user lacks permission for the requested action (→ 403)."""

    def __init__(self, message: str = "permission denied"):
        super().__init__(message)


class NotFoundError(TaskFlowException):
    """Raised when a requested resource does not exist (→ 404)."""

    def __init__(self, message: str = "not found"):
        super().__init__(message)


class ConflictError(TaskFlowException):
    """Raised on unique constraint violations, e.g. duplicate email (→ 409)."""

    def __init__(self, message: str = "resource already exists"):
        super().__init__(message)
