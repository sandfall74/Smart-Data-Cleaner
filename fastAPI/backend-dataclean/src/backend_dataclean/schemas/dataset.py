from pydantic import BaseModel  
from typing import List, Dict, Any, Optional

# ==============================================================================
# MÓDULO DE ESQUEMAS PARA EL DATASET
# ------------------------------------------------------------------------------
# Define la estructura de datos que la API de FastAPI utiliza para validar
# y formatear la información que se intercambia con el frontend en React.
# ==============================================================================

class ColumnDetail(BaseModel):
    name: str
    data_type: str
    missing_count: int
    missing_percentage: float
    unique_values_count: int
    suggested_type: Optional[str] = None  
    reason: Optional[str] = None          

class AnalysisResponse(BaseModel):
    filename: str
    total_rows: int
    total_columns: int
    duplicates_count: int
    total_missing_values: int
    data_health_score: float  
    columns_summary: List[ColumnDetail]
    preview: List[Dict[str, Any]]