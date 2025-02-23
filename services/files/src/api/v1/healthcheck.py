from fastapi import APIRouter, status
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/check")
async def health_check() -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "OK"})
