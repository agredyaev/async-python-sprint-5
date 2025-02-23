from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import HTTPException, Request, status

from core.logging.logger import CoreLogger
from core.security.auth.schemas import UserTokenGenData

logger = CoreLogger.get_logger("auth_service")


class AuthService:
    def __init__(self, request: Request):
        self.authjwt = AuthJWT(request)

    @staticmethod
    def _handle_error(
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY, detail: str = "Session expired. Login again."
    ) -> None:
        raise HTTPException(status_code=status_code, detail=detail)

    async def authenticate(self) -> UserTokenGenData | None:  # type: ignore[return]
        try:
            await self.authjwt.jwt_required()
            access_token = await self.authjwt.get_raw_jwt()
            if not access_token:
                self._handle_error(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials."
                )
            await self.authjwt.jwt_refresh_token_required()
            refresh_token = await self.authjwt.get_raw_jwt()
            if not refresh_token:
                self._handle_error()
            return UserTokenGenData(access_token=access_token, refresh_token=refresh_token)
        except Exception as e:
            logger.exception("Auth error: %s", exc_info=e)
            self._handle_error()


@lru_cache
def get_auth_service(request: Request) -> AuthService:
    return AuthService(request)
