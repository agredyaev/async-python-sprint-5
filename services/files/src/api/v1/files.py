from typing import Annotated

from uuid import UUID

from fastapi import APIRouter, Depends, Request, UploadFile, status
from starlette.responses import JSONResponse

from schemas.file import FileCreateData, FileResponse, FileVersionResponse, ListUserFilesResponse, ServiceStatusResponse
from services import FileServiceProtocol, get_file_service

router = APIRouter(prefix="/files", tags=["files"])


@router.get(
    "/ping", status_code=status.HTTP_200_OK, summary="Ping for service status", description="Ping for service status"
)
async def ping_status(file_service: Annotated[FileServiceProtocol, Depends(get_file_service)]) -> ServiceStatusResponse:
    return await file_service.get_service_status()


@router.get("/", status_code=status.HTTP_200_OK, summary="Get list of files", description="Get list of files")
async def get_files(
    request: Request, file_service: Annotated[FileServiceProtocol, Depends(get_file_service)]
) -> ListUserFilesResponse:
    user_id = request.state.user_id
    return await file_service.list_files(user_id=user_id)


@router.post("/upload", status_code=status.HTTP_200_OK, summary="Upload file", description="Upload file")
async def upload_file(
    file: UploadFile, data: FileCreateData, file_service: Annotated[FileServiceProtocol, Depends(get_file_service)]
) -> FileResponse:
    return await file_service.upload(file=file, data=data)


@router.get("/download/", status_code=status.HTTP_200_OK, summary="Download file", description="Download file")
async def download_file(
    path: str | UUID, file_service: Annotated[FileServiceProtocol, Depends(get_file_service)]
) -> JSONResponse:
    await file_service.download(path=path)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "OK"})


@router.get(
    "/revisions/", status_code=status.HTTP_200_OK, summary="Get file revisions", description="Get file revisions"
)
async def get_file_revisions(
    path: str, limit: int, file_service: Annotated[FileServiceProtocol, Depends(get_file_service)]
) -> list[FileVersionResponse]:
    return await file_service.get_revisions(path=path, limit=limit)
