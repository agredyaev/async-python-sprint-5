from fastapi import APIRouter

from api.v1 import files, healthcheck

router = APIRouter()
router.include_router(healthcheck.router)
router.include_router(files.router)
