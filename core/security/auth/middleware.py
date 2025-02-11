from typing import Any

from collections.abc import Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.logging.logger import CoreLogger
from core.security.auth.exceptions import AuthJWTError, BlacklistError, InternalServerError, PermissionDeniedError
from core.security.auth.ip_checker import IPChecker, NetworkConfig
from core.security.auth.permissions import PermissionChecker
from core.security.auth.schemas import UserId
from core.security.auth.service import get_auth_service

logger = CoreLogger.get_logger("auth_middleware")


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, permission_checker: PermissionChecker, blacklist: list[str], api_version: str):
        super().__init__(app)
        self.permission_checker = permission_checker
        self.api_version = api_version
        self.blacklist = NetworkConfig(blacklist=blacklist)

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
                current_user: dict[str, Any] = await auth_service.authenticate()
                logger.info("Current user: %s", current_user)
                if not current_user:
                    return self.handle_error(exc=AuthJWTError())

                if self.permission_checker.permissions_enabled:
                    user_perms = current_user.get("permissions", [])
                    if not self.permission_checker.has_permission(user_perms, path):
                        return self.handle_error(exc=PermissionDeniedError())

                user_id: str = current_user.get("sub", "")
                request.state.user_id = UserId.model_validate_json(json_data=user_id).user_id
                logger.info("User: %s", current_user)

            except Exception as e:
                logger.exception("Failed to authenticate user", exc_info=e)
                return self.handle_error(exc=InternalServerError())

        return await call_next(request)

    @staticmethod
    def handle_error(exc: AuthJWTError | PermissionDeniedError | InternalServerError | BlacklistError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
