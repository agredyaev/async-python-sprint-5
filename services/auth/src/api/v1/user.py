from typing import Annotated

from fastapi import APIRouter, Depends, status

from schemas.user import UserAuth, UserCreate, UserLogoutResponse, UserResponse
from services import UserService, get_user_service

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/signup", summary="Sign up", description="Create a new user", status_code=status.HTTP_200_OK)
async def signup(data_in: UserCreate, service: Annotated[UserService, Depends(get_user_service)]) -> UserResponse:
    return await service.signup(user_data=data_in)


@router.post("/login", summary="Login", description="Login user", status_code=status.HTTP_200_OK)
async def login(data_in: UserAuth, service: Annotated[UserService, Depends(get_user_service)]) -> UserResponse:
    return await service.login(user_data=data_in)


@router.post("/logout", summary="Logout", description="Logout user", status_code=status.HTTP_200_OK)
async def logout(service: Annotated[UserService, Depends(get_user_service)]) -> UserLogoutResponse:
    return await service.logout()
