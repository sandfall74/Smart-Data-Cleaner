
import numpy as np
import pandas as pd
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class OutlierSummary(BaseModel):
    column_name: str
    method: str
    outliers_count: int
    outliers_percentage: float
    lower_bound: float
    upper_bound: float
    outlier_indices: List[int]


def detect_outliers_iqr(series: pd.Series, factor: float = 1.5) -> tuple[pd.Series, float, float]:
    
    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
    if numeric_series.empty:
        return pd.Series(False, index=series.index), 0.0, 0.0

    q1 = numeric_series.quantile(0.25)
    q3 = numeric_series.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - (factor * iqr)
    upper_bound = q3 + (factor * iqr)

    is_outlier = (series < lower_bound) | (series > upper_bound)
    return is_outlier.fillna(False), float(lower_bound), float(upper_bound)


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> tuple[pd.Series, float, float]:
    
    numeric_series = pd.to_numeric(series, errors="coerce")
    mean = numeric_series.mean()
    std = numeric_series.std()

    if std == 0 or np.isnan(std):
        return pd.Series(False, index=series.index), float(mean or 0.0), float(mean or 0.0)

    z_scores = (numeric_series - mean) / std
    is_outlier = z_scores.abs() > threshold

    lower_bound = mean - (threshold * std)
    upper_bound = mean + (threshold * std)

    return is_outlier.fillna(False), float(lower_bound), float(upper_bound)


def analyze_dataframe_outliers(df: pd.DataFrame, columns: Optional[List[str]] = None, method: str = "iqr") -> List[OutlierSummary]:
    
    summaries = []
    target_cols = columns if columns is not None else df.select_dtypes(include=[np.number]).columns.tolist()

    for col in target_cols:
        if col not in df.columns:
            continue

        series = pd.to_numeric(df[col], errors="coerce")
        if series.dropna().empty:
            continue

        if method.lower() == "zscore":
            mask, lower, upper = detect_outliers_zscore(series)
        else:
            mask, lower, upper = detect_outliers_iqr(series)

        count = int(mask.sum())
        total = len(series)
        pct = round((count / total) * 100, 2) if total > 0 else 0.0
        indices = df.index[mask].tolist()

        summaries.append(
            OutlierSummary(
                column_name=col,
                method=method,
                outliers_count=count,
                outliers_percentage=pct,
                lower_bound=round(lower, 4),
                upper_bound=round(upper, 4),
                outlier_indices=indices[:100] 
            )
        )

    return summaries