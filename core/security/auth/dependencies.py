from fastapi import FastAPI

from core.security.auth.middleware import AuthMiddleware
from core.security.auth.permissions import PermissionChecker, PermissionsCheck


def setup_auth_middleware(
    app: FastAPI,
    exempt_endpoints: list[str],
    blacklist: list[str],
    api_version: str,
    permissions_enabled: PermissionsCheck = PermissionsCheck.DISABLED,
) -> None:
    permission_checker = PermissionChecker(exempt_endpoints, permissions_enabled)

    app.add_middleware(
        AuthMiddleware, permission_checker=permission_checker, api_version=api_version, blacklist=blacklist
    )
