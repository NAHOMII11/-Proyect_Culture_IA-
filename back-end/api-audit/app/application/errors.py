class AppError(Exception):
    def __init__(
        self,
        message: str,
        error: str = "application_error",
        status_code: int = 400,
        details: list | None = None,
    ):
        self.message = message
        self.error = error
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)
