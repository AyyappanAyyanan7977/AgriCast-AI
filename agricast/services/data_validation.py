"""Small reusable dataset guards used by UI/API tests and workflows."""
from __future__ import annotations
import pandas as pd


def keep_first_duplicate_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with repeated column labels removed, preserving first occurrence."""
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame")
    return frame.loc[:, ~frame.columns.duplicated(keep="first")].copy()


def dataset_quality_summary(frame: pd.DataFrame) -> dict:
    """Return transparent descriptive quality checks without inferring data validity."""
    clean = keep_first_duplicate_columns(frame)
    return {
        "rows": int(len(clean)),
        "columns": list(map(str, clean.columns)),
        "missing_cells": int(clean.isna().sum().sum()),
        "duplicate_rows": int(clean.duplicated().sum()),
        "numeric_columns": list(map(str, clean.select_dtypes(include="number").columns)),
    }
