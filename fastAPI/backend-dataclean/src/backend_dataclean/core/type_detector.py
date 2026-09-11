from __future__ import annotations

from dataclasses import asdict, dataclass
import pandas as pd
from pandas.api import types as pdt

# Tipos semánticos posibles
NUMERICA_CONTINUA = "numerica_continua"
NUMERICA_DISCRETA = "numerica_discreta"
CATEGORICA = "categorica"
BOOLEANA = "booleana"
FECHA = "fecha"
TEXTO = "texto"
IDENTIFICADOR = "identificador"
CONSTANTE = "constante"
VACIA = "vacia"


APTOS_NUMERICOS = {NUMERICA_CONTINUA, NUMERICA_DISCRETA}
APTOS_CATEGORICOS = {CATEGORICA, BOOLEANA}

DESCRIPCIONES = {
    NUMERICA_CONTINUA: "Número con decimales o de rango amplio. Apta para clustering, outliers y correlación.",
    NUMERICA_DISCRETA: "Número entero con pocos valores distintos. Apta para correlación; revisar si en realidad es categórica.",
    CATEGORICA: "Conjunto acotado de categorías. Requiere codificación antes de usarse en clustering.",
    BOOLEANA: "Dos valores (sí/no, 0/1, true/false).",
    FECHA: "Fecha u hora. Útil para derivar variables (mes, día, antigüedad).",
    TEXTO: "Texto libre de alta variabilidad. No se usa directo en los modelos.",
    IDENTIFICADOR: "Valor casi único por fila (ID, cédula, código). Debe excluirse de los análisis.",
    CONSTANTE: "Un solo valor en toda la columna. No aporta información.",
    VACIA: "Columna sin datos.",
}

VALORES_BOOLEANOS = {
    "si", "no", "s", "n", "true", "false", "verdadero", "falso",
    "yes", "y", "1", "0", "t", "f",
}

# Umbrales 
UMBRAL_UNICIDAD_IDENTIFICADOR = 0.95  
UMBRAL_CARDINALIDAD_CATEGORICA = 0.50  
MAXIMO_CATEGORIAS = 25                
MAXIMO_ENTEROS_DISCRETOS = 20         
MINIMO_EXITO_FECHA = 0.80              


@dataclass
class PerfilColumna:
    columna: str
    tipo: str
    dtype_pandas: str
    no_nulos: int
    nulos: int
    porcentaje_nulos: float
    unicos: int
    cardinalidad: float
    ejemplo: str
    razon: str

    def como_dict(self) -> dict:
        return asdict(self)


def es_texto(serie: pd.Series) -> bool:
    if pdt.is_numeric_dtype(serie) or pdt.is_bool_dtype(serie) or pdt.is_datetime64_any_dtype(serie):
        return False
    return pdt.is_object_dtype(serie) or pdt.is_string_dtype(serie)


def _muestra_texto(serie: pd.Series, limite: int = 1000) -> pd.Series:
    limpia = serie.dropna().astype(str).str.strip()
    return limpia.head(limite)


def _parece_booleana(serie: pd.Series) -> bool:
    valores = set(_muestra_texto(serie).str.lower().unique())
    return 0 < len(valores) <= 2 and valores.issubset(VALORES_BOOLEANOS)


def _parece_fecha(serie: pd.Series) -> bool:
    muestra = _muestra_texto(serie, limite=300)
    if muestra.empty:
        return False
    if muestra.str.fullmatch(r"-?\d+([.,]\d+)?").mean() > 0.9:
        return False
    convertidas = pd.to_datetime(muestra, errors="coerce", format="mixed", dayfirst=True)
    return convertidas.notna().mean() >= MINIMO_EXITO_FECHA


def _numerica_encubierta(serie: pd.Series) -> pd.Series | None:
    muestra = _muestra_texto(serie, limite=500)
    if muestra.empty:
        return None
    limpia = (
        muestra.str.replace(r"[$₡€\s%]", "", regex=True)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    convertida = pd.to_numeric(limpia, errors="coerce")
    if convertida.notna().mean() >= 0.9:
        return convertida
    return None


def detectar_tipo(serie: pd.Series) -> tuple[str, str]:
    no_nulos = serie.dropna()
    total = len(no_nulos)

    if total == 0:
        return VACIA, "Todos los valores son nulos."

    unicos = no_nulos.nunique(dropna=True)
    if unicos == 1:
        return CONSTANTE, f"Un único valor repetido ({no_nulos.iloc[0]!r})."

    cardinalidad = unicos / total

    if pdt.is_bool_dtype(serie):
        return BOOLEANA, "dtype booleano de pandas."

    if pdt.is_datetime64_any_dtype(serie):
        return FECHA, "dtype de fecha de pandas."

    if pdt.is_numeric_dtype(serie):
        if unicos == 2:
            return BOOLEANA, "Solo dos valores numéricos distintos (binaria)."
        if pdt.is_integer_dtype(serie) or (no_nulos % 1 == 0).all():
            if unicos <= MAXIMO_ENTEROS_DISCRETOS:
                return NUMERICA_DISCRETA, f"Enteros con {unicos} valores distintos."
            if cardinalidad >= UMBRAL_UNICIDAD_IDENTIFICADOR:
                return IDENTIFICADOR, f"Enteros casi únicos ({cardinalidad:.0%} distintos)."
            return NUMERICA_CONTINUA, f"Enteros con {unicos} valores distintos."
        return NUMERICA_CONTINUA, "Valores numéricos con decimales."

    if _parece_booleana(serie):
        return BOOLEANA, "Dos valores de tipo sí/no."

    if _numerica_encubierta(serie) is not None:
        return NUMERICA_CONTINUA, "Texto que representa números (símbolos o separadores de miles)."

    if _parece_fecha(serie):
        return FECHA, "La mayoría de los valores se interpretan como fecha."

    if cardinalidad >= UMBRAL_UNICIDAD_IDENTIFICADOR:
        return IDENTIFICADOR, f"Casi un valor distinto por fila ({cardinalidad:.0%})."

    if unicos <= MAXIMO_CATEGORIAS and cardinalidad < UMBRAL_CARDINALIDAD_CATEGORICA:
        return CATEGORICA, f"{unicos} categorías distintas."

    return TEXTO, f"Texto de alta variabilidad ({unicos} valores distintos)."


def perfilar_columna(serie: pd.Series, nombre: str) -> PerfilColumna:
    tipo, razon = detectar_tipo(serie)
    no_nulos = int(serie.notna().sum())
    nulos = int(serie.isna().sum())
    total = len(serie)
    unicos = int(serie.nunique(dropna=True))
    muestra = serie.dropna()
    ejemplo = str(muestra.iloc[0])[:60] if not muestra.empty else "-"

    return PerfilColumna(
        columna=nombre,
        tipo=tipo,
        dtype_pandas=str(serie.dtype),
        no_nulos=no_nulos,
        nulos=nulos,
        porcentaje_nulos=round(nulos / total * 100, 2) if total else 0.0,
        unicos=unicos,
        cardinalidad=round(unicos / no_nulos, 4) if no_nulos else 0.0,
        ejemplo=ejemplo,
        razon=razon,
    )


def perfilar(datos: pd.DataFrame) -> pd.DataFrame:
    perfiles = [perfilar_columna(datos[col], col).como_dict() for col in datos.columns]
    return pd.DataFrame(perfiles)


def columnas_por_tipo(perfil: pd.DataFrame, tipos: set[str]) -> list[str]:
    return perfil.loc[perfil["tipo"].isin(tipos), "columna"].tolist()


def columnas_analizables(perfil: pd.DataFrame) -> dict[str, list[str]]:
    return {
        "numericas": columnas_por_tipo(perfil, APTOS_NUMERICOS),
        "categoricas": columnas_por_tipo(perfil, APTOS_CATEGORICOS),
        "fechas": columnas_por_tipo(perfil, {FECHA}),
        "excluir": columnas_por_tipo(perfil, {IDENTIFICADOR, CONSTANTE, VACIA, TEXTO}),
    }


def a_numerico(serie: pd.Series) -> pd.Series:
    directo = pd.to_numeric(serie, errors="coerce")
    if directo.notna().mean() >= 0.9:
        return directo

    limpia = (
        serie.astype(str).str.strip()
        .str.replace(r"[$₡¢€\s%]", "", regex=True)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(limpia, errors="coerce")