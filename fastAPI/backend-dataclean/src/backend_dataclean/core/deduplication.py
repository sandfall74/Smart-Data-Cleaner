# src/backend_dataclean/core/deduplication.py
import pandas as pd
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class DeduplicationReport(BaseModel):
    total_rows: int
    unique_rows: int
    duplicate_rows_count: int
    duplicate_percentage: float
    subset_used: List[str]
    sample_duplicates: List[Dict[str, Any]]


def analyze_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None, keep: str = "first") -> DeduplicationReport:
    """Calcula métricas detalladas sobre filas duplicadas."""
    valid_subset = [c for c in (subset or []) if c in df.columns] or None

    mask = df.duplicated(subset=valid_subset, keep=keep)
    dup_count = int(mask.sum())
    total = len(df)
    pct = round((dup_count / total) * 100, 2) if total > 0 else 0.0

    sample = df[mask].head(5).fillna("").to_dict(orient="records")

    return DeduplicationReport(
        total_rows=total,
        unique_rows=total - dup_count,
        duplicate_rows_count=dup_count,
        duplicate_percentage=pct,
        subset_used=valid_subset or list(df.columns),
        sample_duplicates=sample
    )


def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None, keep: str = "first") -> tuple[pd.DataFrame, int]:
    """Elimina duplicados """
    valid_subset = [c for c in (subset or []) if c in df.columns] or None
    initial_count = len(df)
    cleaned_df = df.drop_duplicates(subset=valid_subset, keep=keep).reset_index(drop=True)
    removed = initial_count - len(cleaned_df)
    return cleaned_df, removed