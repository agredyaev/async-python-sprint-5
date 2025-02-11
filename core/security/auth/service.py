from typing import Any

from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import HTTPException, Request, status

from core.logging.logger import CoreLogger

logger = CoreLogger.get_logger("auth_service")


class AuthService:
    def __init__(self, request: Request):
        self.authjwt = AuthJWT(request)

    async def authenticate(self) -> dict[str, Any]:
        try:
            await self.authjwt.jwt_required()
            return await self.authjwt.get_raw_jwt()
        except Exception as e:
            logger.exception("Auth error: %s", exc_info=e)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Session expired. Login again.") from e


@lru_cache
def get_auth_service(request: Request) -> AuthService:
    return AuthService(request)
