from conf.settings import settings as config
from core.utils import get_list_from_string

EXEMPT_ENDPOINTS: list[str] = [
    "/user/login",
    "/user/signup",
    "/check",
    config.api.docs_url.split(config.api.version)[-1],
    config.api.openapi_url.split(config.api.version)[-1],
]


BLACKLIST: list[str] = get_list_from_string(config.api.blacklist)
