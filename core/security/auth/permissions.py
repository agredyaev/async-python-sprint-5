from enum import IntEnum

from core.logging.logger import CoreLogger

logger = CoreLogger.get_logger("permissions")


class PermissionsCheck(IntEnum):
    ENABLED = 1
    DISABLED = 0


class PermissionChecker:
    """Class for checking permissions."""

    __slots__ = ("exempt_endpoints", "permissions_enabled")

    def __init__(self, exempt_endpoints: list[str], permissions_check: PermissionsCheck = PermissionsCheck.DISABLED):
        self.exempt_endpoints = exempt_endpoints
        self.permissions_enabled = permissions_check

    def is_exempt(self, path: str) -> bool:
        logger.info("Checking path %s in exempt list %s", path, self.exempt_endpoints)
        return path in self.exempt_endpoints

    @staticmethod
    def has_permission(user_permissions: list[str], path: str) -> bool:
        return any(path.startswith(permission) for permission in user_permissions)
