import json
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from backend_dataclean.core.cleaner import execute_pipeline
from backend_dataclean.core.loader import ErrorCarga, cargar_csv, cargar_excel, validar_archivo
from backend_dataclean.schemas.clean import CleanRequest, CleanResponse

router = APIRouter()


@router.post("/process", response_model=CleanResponse)
async def clean_dataset(
    file: UploadFile = File(...),
    options: str = Form(
        ...,
        description="JSON serializado con el objeto CleanRequest",
        example='{"remove_duplicates": true, "normalize_null_strings": true}',
    ),
):
   
    try:
        # parsear las opciones JSON enviadas desde la petición 
        clean_options_dict = json.loads(options)
        clean_request = CleanRequest(**clean_options_dict)

        # leer archivo
        contents = await file.read()
        formato = validar_archivo(file.filename, tamano_bytes=len(contents))

        if formato == "csv":
            resultado = cargar_csv(contents, nombre_archivo=file.filename)
        else:
            resultado = cargar_excel(contents, nombre_archivo=file.filename)

        # Aplicar limpieza
        _, response = execute_pipeline(resultado.datos, clean_request)

        return response

    except ErrorCarga as err:
        raise HTTPException(status_code=400, detail=str(err))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="El parámetro 'options' no es un JSON válido."
        )
    except Exception as err:
        raise HTTPException(
            status_code=500, detail=f"Error durante el proceso de limpieza: {str(err)}"
        )