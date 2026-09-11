from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass, field
import pandas as pd

from backend_dataclean.schemas.dataset import AnalysisResponse, ColumnDetail
from backend_dataclean.core.type_detector import perfilar

# Configuraciones 

EXTENSIONES_CSV = {".csv", ".txt", ".tsv"}
EXTENSIONES_EXCEL = {".xlsx", ".xls", ".xlsm"}
EXTENSIONES_SOPORTADAS = EXTENSIONES_CSV | EXTENSIONES_EXCEL

TAMANO_MAXIMO_MB = 200
CODIFICACIONES = ("utf-8", "utf-8-sig", "latin-1", "cp1252")


class ErrorCarga(Exception):
    """Error controlado durante la carga: ."""


@dataclass
class ResultadoCarga:
    
    datos: pd.DataFrame
    nombre_archivo: str
    formato: str  # "csv" o "excel"
    filas: int
    columnas: int
    separador: str | None = None
    codificacion: str | None = None
    hoja: str | None = None
    advertencias: list[str] = field(default_factory=list)



# Validaciones 

def extension_de(nombre_archivo: str) -> str:
    return os.path.splitext(nombre_archivo)[1].lower()


def validar_archivo(nombre_archivo: str, tamano_bytes: int | None = None) -> str:
    if not nombre_archivo:
        raise ErrorCarga("No se recibió ningún archivo.")

    ext = extension_de(nombre_archivo)
    if ext not in EXTENSIONES_SOPORTADAS:
        soportadas = ", ".join(sorted(EXTENSIONES_SOPORTADAS))
        raise ErrorCarga(
            f"Formato '{ext or 'desconocido'}' no soportado. Formatos válidos: {soportadas}."
        )

    if tamano_bytes is not None:
        mb = tamano_bytes / (1024 * 1024)
        if tamano_bytes == 0:
            raise ErrorCarga("El archivo está vacío (0 bytes).")
        if mb > TAMANO_MAXIMO_MB:
            raise ErrorCarga(
                f"El archivo pesa {mb:.1f} MB y el límite permitido es {TAMANO_MAXIMO_MB} MB."
            )

    return "csv" if ext in EXTENSIONES_CSV else "excel"


def _leer_bytes(origen) -> bytes:
    if isinstance(origen, (bytes, bytearray)):
        return bytes(origen)
    if hasattr(origen, "read"):
        if hasattr(origen, "seek"):
            origen.seek(0)
        contenido = origen.read()
        if hasattr(origen, "seek"):
            origen.seek(0)
        return contenido if isinstance(contenido, bytes) else str(contenido).encode("utf-8")
    raise ErrorCarga("No se pudo leer el contenido del archivo.")


def detectar_codificacion(contenido: bytes) -> str:
    muestra = contenido[:200_000]
    for codificacion in CODIFICACIONES:
        try:
            muestra.decode(codificacion)
            return codificacion
        except UnicodeDecodeError:
            continue
    return "latin-1"


def detectar_separador(texto: str) -> str:
    muestra = texto[:10_000]
    try:
        return csv.Sniffer().sniff(muestra, delimiters=",;\t|").delimiter
    except csv.Error:
        pass

    primeras = [linea for linea in muestra.splitlines() if linea.strip()][:10]
    if not primeras:
        return ","
    conteos = {sep: sum(linea.count(sep) for linea in primeras) for sep in (",", ";", "\t", "|")}
    mejor = max(conteos, key=conteos.get)
    return mejor if conteos[mejor] > 0 else ","



# motores de lectura (CSV y Excel)

def cargar_csv(
    origen,
    nombre_archivo: str,
    separador: str | None = None,
    codificacion: str | None = None,
    decimal: str = ".",
) -> ResultadoCarga:
    contenido = _leer_bytes(origen)
    if not contenido.strip():
        raise ErrorCarga("El archivo está vacío.")

    codificacion = codificacion or detectar_codificacion(contenido)
    try:
        texto = contenido.decode(codificacion)
    except UnicodeDecodeError as exc:
        raise ErrorCarga(
            f"No se pudo leer la codificación '{codificacion}'. Intenta con latin-1 o cp1252."
        ) from exc

    separador = separador or detectar_separador(texto)
    advertencias: list[str] = []

    try:
        datos = pd.read_csv(
            io.StringIO(texto),
            sep=separador,
            decimal=decimal,
            skipinitialspace=True,
            on_bad_lines="skip",
        )
    except pd.errors.EmptyDataError as exc:
        raise ErrorCarga("El archivo no contiene datos legibles.") from exc
    except pd.errors.ParserError as exc:
        raise ErrorCarga(
            f"El archivo no pudo interpretarse como CSV con separador '{separador}'."
        ) from exc

    if datos.shape[1] == 1 and separador != ";":
        advertencias.append(
            "Solo se detectó una columna. Es probable que el separador real sea otro (ej. punto y coma)."
        )

    datos, avisos_col = normalizar_nombres_columnas(datos)
    advertencias.extend(avisos_col)
    _validar_dataframe(datos)

    return ResultadoCarga(
        datos=datos,
        nombre_archivo=nombre_archivo,
        formato="csv",
        filas=len(datos),
        columnas=datos.shape[1],
        separador=separador,
        codificacion=codificacion,
        advertencias=advertencias,
    )


def cargar_excel(origen, nombre_archivo: str, hoja: str | int = 0) -> ResultadoCarga:
    contenido = _leer_bytes(origen)
    advertencias: list[str] = []

    try:
        datos = pd.read_excel(
            io.BytesIO(contenido),
            sheet_name=hoja,
            engine="openpyxl" if extension_de(nombre_archivo) != ".xls" else "xlrd",
        )
    except Exception as exc:
        raise ErrorCarga(f"No se pudo leer el archivo de Excel: {exc}") from exc

    datos, avisos_col = normalizar_nombres_columnas(datos)
    advertencias.extend(avisos_col)
    _validar_dataframe(datos)

    return ResultadoCarga(
        datos=datos,
        nombre_archivo=nombre_archivo,
        formato="excel",
        filas=len(datos),
        columnas=datos.shape[1],
        hoja=str(hoja),
        advertencias=advertencias,
    )


def normalizar_nombres_columnas(datos: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    advertencias: list[str] = []
    nombres: list[str] = []
    vistos: dict[str, int] = {}

    for indice, original in enumerate(datos.columns):
        nombre = str(original).strip()
        if not nombre or nombre.lower().startswith("unnamed"):
            nombre = f"columna_{indice + 1}"
            advertencias.append(f"La columna {indice + 1} no tenía nombre; se renombró a '{nombre}'.")
        if nombre in vistos:
            vistos[nombre] += 1
            nuevo = f"{nombre}_{vistos[nombre]}"
            advertencias.append(f"Nombre duplicado '{nombre}'; se renombró a '{nuevo}'.")
            nombre = nuevo
        else:
            vistos[nombre] = 0
        nombres.append(nombre)

    datos = datos.copy()
    datos.columns = nombres
    return datos, advertencias


def _validar_dataframe(datos: pd.DataFrame) -> None:
    if datos.empty:
        raise ErrorCarga("El archivo se leyó pero no contiene filas con datos.")
    if datos.shape[1] == 0:
        raise ErrorCarga("El archivo no contiene columnas.")




def process_file_bytes(file_bytes: bytes, filename: str) -> AnalysisResponse:
    
    # 1. Validar y cargar usando la lógica robusta
    formato = validar_archivo(filename, tamano_bytes=len(file_bytes))
    if formato == "csv":
        resultado = cargar_csv(file_bytes, nombre_archivo=filename)
    else:
        resultado = cargar_excel(file_bytes, nombre_archivo=filename)

    df = resultado.datos
    total_rows, total_cols = df.shape
    total_cells = total_rows * total_cols

    # 2. Metricas globales
    duplicates_count = int(df.duplicated().sum())
    total_missing = int(df.isnull().sum().sum())

    # 3. Calculo de Health Score 
    missing_ratio = (total_missing / total_cells) if total_cells > 0 else 0
    duplicate_ratio = (duplicates_count / total_rows) if total_rows > 0 else 0
    health_score = max(0.0, round((1.0 - (missing_ratio * 0.7 + duplicate_ratio * 0.3)) * 100, 2))

    # 4. desglose columna por columna
    perfil_df = perfilar(df)
    columns_summary = []
    for _, row in perfil_df.iterrows():
        columns_summary.append(
            ColumnDetail(
                name=str(row["columna"]),
                data_type=str(row["dtype_pandas"]),
                missing_count=int(row["nulos"]),
                missing_percentage=float(row["porcentaje_nulos"]),
                unique_values_count=int(row["unicos"]),
                suggested_type=str(row["tipo"]),  # 
                reason=str(row["razon"])           
            )
        )

    # 5. Vista previa de las primeras 5 filas 
    preview_data = df.head(5).fillna("").to_dict(orient="records")

    # 6. Retorno empaquetado en el esquema Pydantic
    return AnalysisResponse(
        filename=filename,
        total_rows=total_rows,
        total_columns=total_cols,
        duplicates_count=duplicates_count,
        total_missing_values=total_missing,
        data_health_score=health_score,
        columns_summary=columns_summary,
        preview=preview_data,
    )