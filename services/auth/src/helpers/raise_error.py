from fastapi import HTTPException
from starlette import status


def raise_error(status_code: int = status.HTTP_200_OK, detail: str = "") -> None:
    raise HTTPException(status_code=status_code, detail=detail)
