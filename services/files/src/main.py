import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import setup_routers
from conf.constraints import BLACKLIST, EXEMPT_ENDPOINTS
from conf.exceptions import register_exception_handlers
from conf.settings import settings
from core.database.repository.redis import RedisConfig
from core.logging import CoreLogger
from core.security import setup_auth_middleware
from helpers.lifspan import lifespan

CoreLogger.setup()

app = FastAPI(
    lifespan=lifespan,
    root_path=settings.app.root_path,
    title=settings.app.name,
    default_response_class=ORJSONResponse,
    docs_url=settings.api.docs_url,
    openapi_url=settings.api.openapi_url,
    debug=settings.app.debug,
)


setup_auth_middleware(
    app=app,
    api_version=settings.api.version,
    exempt_endpoints=EXEMPT_ENDPOINTS,
    blacklist=BLACKLIST,
    redis_config=RedisConfig(dsn=settings.redis.dsn, password=settings.redis.password),
)
register_exception_handlers(app=app)
setup_routers(app=app)

if __name__ == "__main__":
    uvicorn.run(app=settings.app.app, host=settings.app.host, port=settings.app.port)
