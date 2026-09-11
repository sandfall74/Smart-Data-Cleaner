from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ColumnCleanInstruction(BaseModel):
    column_name: str = Field(..., description="Nombre de la columna a procesar")
    null_strategy: Optional[str] = Field(
        None,
        description="Estrategia para nulos: conservar, eliminar_filas, media, mediana, moda, cero, constante",
    )
    fill_value: Optional[Any] = Field(
        None, description="Valor usado si la estrategia es 'constante'"
    )
    target_type: Optional[str] = Field(
        None,
        description="Tipo de dato destino (ej: 'Numérica Continua', 'Fecha', 'Booleana', 'Texto')",
    )
    
    outlier_strategy: Optional[str] = Field(
        "conservar",
        description="Estrategia para outliers: conservar, eliminar_filas, clip",
    )
    outlier_method: Optional[str] = Field(
        "iqr",
        description="Método de detección de outliers: 'iqr' o 'zscore'",
    )


class CleanRequest(BaseModel):
    remove_duplicates: bool = Field(
        True, description="Indica si se deben eliminar filas duplicadas"
    )
    
    duplicate_subset: Optional[List[str]] = Field(
        None,
        description="Lista de nombres de columnas a considerar para identificar duplicados. Si es None o vacía, analiza la fila completa.",
    )
    normalize_null_strings: bool = Field(
        True, description="Convierte textos como 'N/A', '-' o 'sin dato' en NaN"
    )
    trim_strings: bool = Field(
        True, description="Elimina espacios al inicio y final de textos"
    )
    drop_empty_cols_threshold: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Umbral (0.0 a 1.0) para descartar columnas con exceso de nulos",
    )
    column_instructions: List[ColumnCleanInstruction] = Field(
        default_factory=list,
        description="Lista de reglas específicas por columna",
    )


class AuditEntry(BaseModel):
    momento: str
    operacion: str
    detalle: str
    filas_antes: int
    filas_despues: int
    delta_filas: int


class CleanResponse(BaseModel):
    message: str
    rows_before: int
    rows_after: int
    columns_before: int
    columns_after: int
    new_health_score: float
    audit_log: List[AuditEntry]
    preview: List[dict]