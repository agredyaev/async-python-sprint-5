from fastapi import APIRouter

from api.v1 import healthcheck, url, user

router = APIRouter()
router.include_router(healthcheck.router)
router.include_router(user.router)
router.include_router(url.router)
