from datetime import timedelta

from async_fastapi_jwt_auth import AuthJWT
from fastapi import status

from conf.settings import settings
from core.database.repository.redis import RedisRepository, TokenData, TokenKey
from helpers.raise_error import raise_error
from models.user import User
from repositories.user import UserRepository
from schemas.user import UserAuth, UserCreate, UserLogoutResponse, UserResponse, UserTokenGen


class UserService:
    """User service class."""

    __slots__ = ("_redis_repo", "_user_repo", "authjwt")

    def __init__(self, user_repo: UserRepository, authjwt: AuthJWT, redis_repo: RedisRepository):
        self._user_repo = user_repo
        self.authjwt = authjwt
        self._redis_repo = redis_repo

    async def _set_cookies(self, sbj: UserTokenGen) -> None:
        access_token = await self.authjwt.create_access_token(subject=sbj.model_dump_json(), fresh=True)
        refresh_token = await self.authjwt.create_refresh_token(subject=sbj.model_dump_json())
        await self.authjwt.set_access_cookies(access_token)
        await self.authjwt.set_refresh_cookies(refresh_token)

    async def signup(self, user_data: UserCreate) -> UserResponse:
        if await self._user_repo.get_by_username(user_data.username):
            raise_error(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
        user = User(**user_data.model_dump(by_alias=True))
        user = await self._user_repo.upsert(user)
        sbj = UserTokenGen(user_id=user.id)
        await self._set_cookies(sbj)
        return UserResponse.model_validate(user)

    async def login(self, user_data: UserAuth) -> UserResponse | None:
        user = await self._user_repo.get_by_username(user_data.username)
        if not user or not user_data.verify_password(user.hashed_password):
            raise_error(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        sbj = UserTokenGen(user_id=user.id)
        await self._set_cookies(sbj)
        return UserResponse.model_validate(user)

    async def logout(self, jti: str) -> UserLogoutResponse:
        token_key = TokenKey(jti=jti).key
        await self._redis_repo.set(TokenData(key=token_key, expires=timedelta(seconds=settings.auth.max_age)))
        await self._redis_repo.get_all()
        await self.authjwt.unset_jwt_cookies()
        return UserLogoutResponse()
