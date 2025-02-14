from typing import Annotated

from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends

from core.database.repository.redis import RedisRepository
from repositories import UserRepository, get_redis_repo, get_user_repo
from services.user import UserService


@lru_cache
def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    authjwt: Annotated[AuthJWT, Depends()],
    redis_repo: Annotated[RedisRepository, Depends(get_redis_repo)],
) -> UserService:
    return UserService(user_repo=user_repo, authjwt=authjwt, redis_repo=redis_repo)
