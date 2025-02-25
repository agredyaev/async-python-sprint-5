from fastapi import HTTPException, status


class AuthenticationError(Exception):
    def __init__(self, message: str, original_exception: Exception | None = None):
        super().__init__(message)
        self.original_exception = original_exception


class BlacklistError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")


class AuthJWTError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired. Login again.")


class PermissionDeniedError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


class InternalServerError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
