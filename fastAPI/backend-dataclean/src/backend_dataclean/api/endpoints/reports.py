
import json
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response

from backend_dataclean.core.cleaner import execute_pipeline
from backend_dataclean.core.loader import ErrorCarga, cargar_csv, cargar_excel, validar_archivo
from backend_dataclean.core.report_generator import (
    export_dataframe_to_bytes,
    generate_audit_pdf_bytes,
    generate_audit_summary_json,
)
from backend_dataclean.schemas.clean import CleanRequest

router = APIRouter()


@router.post("/export-file")
async def export_cleaned_file(
    file: UploadFile = File(...),
    options: str = Form(...),
    export_format: str = Query("csv", description="Formato de descarga: 'csv' o 'xlsx'"),
):
    """ejecuta la limpieza y retorna el archivo transformado listo para descarga (CSV o XLSX)."""
    try:
        clean_options_dict = json.loads(options)
        clean_request = CleanRequest(**clean_options_dict)

        contents = await file.read()
        formato = validar_archivo(file.filename, tamano_bytes=len(contents))

        if formato == "csv":
            resultado = cargar_csv(contents, nombre_archivo=file.filename)
        else:
            resultado = cargar_excel(contents, nombre_archivo=file.filename)

        # aplicar pipeline
        cleaned_df, _ = execute_pipeline(resultado.datos, clean_request)

        # generar archivo en bytes
        file_bytes, media_type, ext = export_dataframe_to_bytes(cleaned_df, format_type=export_format)

        base_name = file.filename.rsplit(".", 1)[0]
        download_filename = f"{base_name}_limpio.{ext}"

        return Response(
            content=file_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{download_filename}"'},
        )

    except ErrorCarga as err:
        raise HTTPException(status_code=400, detail=str(err))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="El parámetro 'options' no es un JSON válido.")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error al exportar el archivo: {str(err)}")


@router.post("/export-audit")
async def export_audit_log(
    file: UploadFile = File(...),
    options: str = Form(...),
    export_format: str = Query("pdf", description="Formato del reporte: 'pdf' o 'json'"),
):
    """Ejecuta la limpieza"""
    try:
        clean_options_dict = json.loads(options)
        clean_request = CleanRequest(**clean_options_dict)

        contents = await file.read()
        formato = validar_archivo(file.filename, tamano_bytes=len(contents))

        if formato == "csv":
            resultado = cargar_csv(contents, nombre_archivo=file.filename)
        else:
            resultado = cargar_excel(contents, nombre_archivo=file.filename)

        # aplicar pipeline
        _, clean_response = execute_pipeline(resultado.datos, clean_request)

        base_name = file.filename.rsplit(".", 1)[0]
        fmt = export_format.lower().strip()

        # generar formato deseado
        if fmt == "pdf":
            audit_bytes = generate_audit_pdf_bytes(clean_response)
            media_type = "application/pdf"
            ext = "pdf"
        else:
            audit_bytes = generate_audit_summary_json(clean_response)
            media_type = "application/json"
            ext = "json"

        return Response(
            content=audit_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{base_name}_auditoria.{ext}"'},
        )

    except ErrorCarga as err:
        raise HTTPException(status_code=400, detail=str(err))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="El parámetro 'options' no es un JSON válido.")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte de auditoría: {str(err)}")