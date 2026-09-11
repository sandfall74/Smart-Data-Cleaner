from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd

from backend_dataclean.schemas.clean import CleanRequest, CleanResponse, AuditEntry
from backend_dataclean.core.deduplication import remove_duplicates as deduplicar_avanzado
from backend_dataclean.core.outlier_detector import detect_outliers_iqr, detect_outliers_zscore
# marcadores textuales de nulos
NULOS_TEXTUALES = [
    "", " ", "na", "n/a", "n.a.", "null", "none", "nan", "-", "--",
    "sin dato", "sin datos", "desconocido", "?", "#n/a", "nd",
]

ESTRATEGIAS_NULOS = {
    "conservar": "Dejar los nulos como están",
    "eliminar_filas": "Eliminar las filas con nulo en esta columna",
    "media": "Rellenar con la media",
    "mediana": "Rellenar con la mediana",
    "moda": "Rellenar con el valor más frecuente",
    "cero": "Rellenar con 0",
    "constante": "Rellenar con un valor fijo",
}


@dataclass
class Bitacora:
    """historial de operaciones."""

    entradas: list[dict] = field(default_factory=list)

    def registrar(self, operacion: str, detalle: str, filas_antes: int, filas_despues: int) -> None:
        self.entradas.append(
            {
                "momento": datetime.now().strftime("%H:%M:%S"),
                "operacion": operacion,
                "detalle": detalle,
                "filas_antes": filas_antes,
                "filas_despues": filas_despues,
                "delta_filas": filas_despues - filas_antes,
            }
        )


def normalizar_nulos(datos: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    resultado = datos.copy()
    nulos_antes = int(resultado.isna().sum().sum())

    for columna in resultado.columns:
        if pd.api.types.is_string_dtype(resultado[columna]) or pd.api.types.is_object_dtype(resultado[columna]):
            serie = resultado[columna].astype(str).str.strip()
            mascara = serie.str.lower().isin(NULOS_TEXTUALES)
            if mascara.any():
                resultado[columna] = resultado[columna].astype("object").mask(mascara, None)

    nulos_despues = int(resultado.isna().sum().sum())
    return resultado, nulos_despues - nulos_antes


def recortar_espacios(datos: pd.DataFrame) -> pd.DataFrame:
    resultado = datos.copy()
    for columna in resultado.columns:
        if pd.api.types.is_string_dtype(resultado[columna]) or pd.api.types.is_object_dtype(resultado[columna]):
            resultado[columna] = resultado[columna].apply(
                lambda v: v.strip() if isinstance(v, str) else v
            )
    return resultado


def eliminar_duplicados(datos: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    antes = len(datos)
    resultado = datos.drop_duplicates().reset_index(drop=True)
    return resultado, antes - len(resultado)


def aplicar_estrategia_nulos(
    datos: pd.DataFrame,
    columna: str,
    estrategia: str,
    valor_constante: Any = None,
) -> tuple[pd.DataFrame, str]:
    if columna not in datos.columns:
        return datos, f"Columna '{columna}' no encontrada."

    resultado = datos.copy()
    serie = resultado[columna]
    faltantes = int(serie.isna().sum())

    if estrategia == "conservar" or faltantes == 0:
        return resultado, f"'{columna}': sin cambios ({faltantes} nulos)."

    if estrategia == "eliminar_filas":
        resultado = resultado.dropna(subset=[columna]).reset_index(drop=True)
        return resultado, f"'{columna}': se eliminaron {faltantes} filas con nulo."

    if estrategia in ("media", "mediana", "cero"):
        if not pd.api.types.is_numeric_dtype(serie):
            # Convertir a numérico por si venía como string
            serie_num = pd.to_numeric(serie, errors="coerce")
            if serie_num.notna().sum() == 0:
                raise ValueError(f"'{columna}' no es numérica; la estrategia '{estrategia}' no aplica.")
            serie = serie_num

        relleno = {"media": serie.mean(), "mediana": serie.median(), "cero": 0}[estrategia]
        resultado[columna] = serie.fillna(relleno)
        return resultado, f"'{columna}': {faltantes} nulos rellenados con {estrategia} ({relleno:.4g})."

    if estrategia == "moda":
        moda = serie.mode(dropna=True)
        if moda.empty:
            return resultado, f"'{columna}': sin moda calculable, se conservaron los nulos."
        resultado[columna] = serie.fillna(moda.iloc[0])
        return resultado, f"'{columna}': {faltantes} nulos rellenados con la moda ({moda.iloc[0]!r})."

    # Constante
    resultado[columna] = serie.fillna(valor_constante)
    return resultado, f"'{columna}': {faltantes} nulos rellenados con {valor_constante!r}."

def aplicar_estrategia_outliers(
    datos: pd.DataFrame,
    columna: str,
    estrategia: str = "conservar",
    metodo: str = "iqr",
) -> tuple[pd.DataFrame, str]:
    """Aplica la detección y el tratamiento de outliers."""
    if columna not in datos.columns or estrategia == "conservar":
        return datos, f"'{columna}': sin cambios en outliers."

    resultado = datos.copy()
    serie = pd.to_numeric(resultado[columna], errors="coerce")

    if serie.dropna().empty:
        return datos, f"'{columna}': no es numérica o no posee datos válidos para evaluar outliers."

    # seleccion de método
    if metodo.lower() == "zscore":
        mascara, lower, upper = detect_outliers_zscore(serie)
    else:
        mascara, lower, upper = detect_outliers_iqr(serie)

    outliers_count = int(mascara.sum())
    if outliers_count == 0:
        return resultado, f"'{columna}': no se detectaron outliers ({metodo.upper()})."

    # tratamiento
    if estrategia == "eliminar_filas":
        resultado = resultado[~mascara].reset_index(drop=True)
        return resultado, f"'{columna}': se eliminaron {outliers_count} filas consideradas outliers ({metodo.upper()})."

    elif estrategia == "clip":
        resultado[columna] = serie.clip(lower=lower, upper=upper)
        return resultado, f"'{columna}': {outliers_count} outliers ajustados al rango [{lower:.4g}, {upper:.4g}]."

    return resultado, f"'{columna}': sin cambios."


def execute_pipeline(df: pd.DataFrame, request: CleanRequest) -> tuple[pd.DataFrame, CleanResponse]:
    bitacora = Bitacora()
    datos = df.copy()

    filas_orig, cols_orig = datos.shape

    # normalización de marcadores de texto a nulos reales 
    if request.normalize_null_strings:
        filas_antes = len(datos)
        datos, nulos_convertidos = normalizar_nulos(datos)
        if nulos_convertidos > 0:
            bitacora.registrar(
                "Normalización de Nulos",
                f"Se convirtieron {nulos_convertidos} marcadores de texto a NaN reales.",
                filas_antes,
                len(datos),
            )

    # recorte de espacios en blanco
    if request.trim_strings:
        datos = recortar_espacios(datos)

    # deduplicación inteligente 
    if request.remove_duplicates:
        filas_antes = len(datos)
        datos, eliminados = deduplicar_avanzado(datos, subset=request.duplicate_subset)
        if eliminados > 0:
            detalle_subset = f" en las columnas {request.duplicate_subset}" if request.duplicate_subset else " (filas completas)"
            bitacora.registrar(
                "Eliminar Duplicados",
                f"Se eliminaron {eliminados} filas duplicadas{detalle_subset}.",
                filas_antes,
                len(datos),
            )

    # estrategias por columna 
    for col_inst in request.column_instructions:
        if col_inst.null_strategy and col_inst.null_strategy != "conservar":
            filas_antes = len(datos)
            datos, detalle = aplicar_estrategia_nulos(
                datos,
                columna=col_inst.column_name,
                estrategia=col_inst.null_strategy,
                valor_constante=col_inst.fill_value,
            )
            bitacora.registrar("Imputación / Nulos", detalle, filas_antes, len(datos))

    # estrategias por columna 
    for col_inst in request.column_instructions:
        if col_inst.outlier_strategy and col_inst.outlier_strategy != "conservar":
            filas_antes = len(datos)
            datos, detalle = aplicar_estrategia_outliers(
                datos,
                columna=col_inst.column_name,
                estrategia=col_inst.outlier_strategy,
                metodo=col_inst.outlier_method or "iqr",
            )
            bitacora.registrar("Tratamiento de Outliers", detalle, filas_antes, len(datos))

    # descarte de columnas que superen el umbral de nulos
    if request.drop_empty_cols_threshold is not None:
        proporcion = datos.isna().mean()
        a_eliminar = proporcion[proporcion >= request.drop_empty_cols_threshold].index.tolist()
        if a_eliminar:
            datos = datos.drop(columns=a_eliminar)
            bitacora.registrar(
                "Descarte de Columnas",
                f"Se eliminaron columnas con >= {request.drop_empty_cols_threshold * 100}% de nulos: {', '.join(a_eliminar)}.",
                len(datos),
                len(datos),
            )

    filas_fin, cols_fin = datos.shape

    # Recálculo del Data Health Score 
    tot_cells = filas_fin * cols_fin
    tot_missing = int(datos.isnull().sum().sum())
    dups = int(datos.duplicated().sum())
    missing_ratio = (tot_missing / tot_cells) if tot_cells > 0 else 0
    dup_ratio = (dups / filas_fin) if filas_fin > 0 else 0
    health_score = max(0.0, round((1.0 - (missing_ratio * 0.7 + dup_ratio * 0.3)) * 100, 2))

    preview_data = datos.head(5).fillna("").to_dict(orient="records")
    audit_entries = [AuditEntry(**item) for item in bitacora.entradas]

    response = CleanResponse(
        message="Dataset limpiado con éxito.",
        rows_before=filas_orig,
        rows_after=filas_fin,
        columns_before=cols_orig,
        columns_after=cols_fin,
        new_health_score=health_score,
        audit_log=audit_entries,
        preview=preview_data,
    )

    return datos, response