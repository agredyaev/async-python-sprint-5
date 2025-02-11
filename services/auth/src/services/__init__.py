from typing import Annotated

from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends

from repositories import UserRepository, get_user_repo
from services.user import UserService


@lru_cache
def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)], authjwt: Annotated[AuthJWT, Depends()]
) -> UserService:
    return UserService(user_repo=user_repo, authjwt=authjwt)
