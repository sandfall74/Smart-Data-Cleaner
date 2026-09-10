from fastapi import APIRouter
from backend_dataclean.api.endpoints import upload

api_router = APIRouter()

api_router.include_router(upload.router, prefix="/dataset", tags=["Dataset"])