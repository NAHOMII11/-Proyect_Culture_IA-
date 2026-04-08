from typing import Any


class AppError(Exception):
    def __init__(
        self,
        error: str,
        message: str,
        details: list[Any] | None = None,
        status_code: int = 400,
    ):
        self.error = error
        self.message = message
        self.details = details or []
        self.status_code = status_code
        super().__init__(message)
