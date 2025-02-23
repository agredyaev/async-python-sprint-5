from typing import Any

from collections.abc import Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.database.repository.redis import RedisConfig, RedisRepository, TokenKey, get_redis_client
from core.logging.logger import CoreLogger
from core.security.auth.exceptions import (
    AuthenticationError,
    AuthJWTError,
    BlacklistError,
    InternalServerError,
    PermissionDeniedError,
)
from core.security.auth.ip_checker import IPChecker, NetworkConfig
from core.security.auth.permissions import PermissionChecker
from core.security.auth.schemas import UserId, UserTokenGenData
from core.security.auth.service import get_auth_service

logger = CoreLogger.get_logger("auth_middleware")


class AuthMiddleware(BaseHTTPMiddleware):
    """Auth middleware."""

    __slots__ = ("_redis_config", "_redis_repo", "api_version", "blacklist", "permission_checker")

    def __init__(
        self,
        app: FastAPI,
        permission_checker: PermissionChecker,
        blacklist: list[str],
        api_version: str,
        redis_config: RedisConfig,
    ):
        super().__init__(app)
        self.permission_checker = permission_checker
        self.api_version = api_version
        self.blacklist = NetworkConfig(blacklist=blacklist)
        self._redis_config = redis_config
        self._redis_repo: RedisRepository | None = None

    async def get_redis_repo(self) -> RedisRepository:
        if self._redis_repo is None:
            redis_client = await get_redis_client(config=self._redis_config)
            self._redis_repo = RedisRepository(redis=redis_client)
        return self._redis_repo

    async def check_blacklist(self, jti: str) -> bool:
        key = TokenKey(jti=jti).key
        if not self._redis_repo:
            return False
        return await self._redis_repo.exists(key)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> JSONResponse:
        logger.info("Request: query params: %s; headers: %s", request.query_params, request.headers)
        auth_service = get_auth_service(request=request)
        path = request.url.path.split(self.api_version)[-1]
        client_ip = request.client.host

        logger.info("Client IP: %s, Path: %s", client_ip, path)
        is_blocked = IPChecker(self.blacklist).is_blocked(client_ip)

        logger.info("Checking Client IP is blocked: %s", is_blocked)

        if is_blocked:
            return self.handle_error(exc=BlacklistError())

        logger.info("Client IP is not blocked")

        if not self.permission_checker.is_exempt(path):
            logger.info("Checking permissions for path: %s", path)
            try:
                current_user: UserTokenGenData | None = await auth_service.authenticate()
                logger.info("Current user: %s", current_user)
                if not current_user:
                    return self.handle_error(exc=AuthJWTError())

                refresh_token_jti = current_user.refresh_token.get("jti", "")
                if await self.check_blacklist(jti=refresh_token_jti):
                    return self.handle_error(exc=AuthJWTError())

                if self.permission_checker.permissions_enabled:
                    user_perms = current_user.access_token.get("permissions", [])
                    if not self.permission_checker.has_permission(user_perms, path):
                        return self.handle_error(exc=PermissionDeniedError())

                request.state.user_id = UserId.model_validate_json(
                    json_data=current_user.access_token.get("sub", "")
                ).user_id
                request.state.jti = refresh_token_jti
                logger.info("Current user extracted: user_id %s, jti %s", request.state.user_id, request.state.jti)

            except AuthenticationError as e:
                logger.exception("Failed to authenticate user", exc_info=e)
                return self.handle_error(exc=InternalServerError())

        return await call_next(request)

    @staticmethod
    def handle_error(exc: AuthJWTError | PermissionDeniedError | InternalServerError | BlacklistError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
