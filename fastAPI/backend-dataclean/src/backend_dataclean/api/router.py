from fastapi import APIRouter
from backend_dataclean.api.endpoints import clean,upload,reports

api_router = APIRouter()

api_router.include_router(upload.router, prefix="/dataset", tags=["Dataset"])
api_router.include_router(clean.router, prefix="/clean", tags=["Limpieza de Datasets"])
api_router.include_router(reports.router, prefix="/reports", tags=["Export & Reports"])