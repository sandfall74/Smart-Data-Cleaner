from fastapi import APIRouter, File, HTTPException, UploadFile
from backend_dataclean.core.loader import ErrorCarga, process_file_bytes
from backend_dataclean.schemas.dataset import AnalysisResponse

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_dataset(file: UploadFile = File(...)):
    
    try:
       
        contents = await file.read()

        # 2. Procesar el archivo 
        analysis = process_file_bytes(file_bytes=contents, filename=file.filename)

        return analysis

    except ErrorCarga as err:
        
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        
        raise HTTPException(
            status_code=500, detail=f"Error interno procesando el archivo: {str(err)}"
        )