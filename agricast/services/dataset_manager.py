"""Safe local dataset replacement helpers for the Streamlit workflow."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from .data_validation import keep_first_duplicate_columns


def validate_uploaded_dataset(frame: pd.DataFrame, target: str) -> pd.DataFrame:
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("Uploaded content did not produce a valid table.")
    frame = keep_first_duplicate_columns(frame)
    if frame.empty:
        raise ValueError("The CSV has no data rows.")
    if len(frame.columns) < 2:
        raise ValueError("At least two columns are required: a target and one feature.")
    if not all(str(c).strip() for c in frame.columns):
        raise ValueError("Every CSV column must have a non-empty header.")
    if target not in frame.columns:
        raise ValueError(f"Target column {target!r} is not present in the CSV.")
    numeric_target = pd.to_numeric(frame[target], errors="coerce")
    if numeric_target.notna().sum() < 2:
        raise ValueError("The selected target must contain at least two numeric values for regression.")
    result = frame.copy()
    result[target] = numeric_target
    return result


def save_uploaded_dataset(frame: pd.DataFrame, target: str, data_path, target_path,
                          model_path=None, report_path=None, provenance_path=None) -> pd.DataFrame:
    """Validate first, then save dataset/target and invalidate artifacts tied to old data."""
    validated = validate_uploaded_dataset(frame, target)
    data_path = Path(data_path); target_path = Path(target_path)
    data_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    validated.to_csv(data_path, index=False)
    target_path.write_text(target, encoding="utf-8")
    # Old model scores and weights must never be shown as if they describe the new CSV.
    for artifact in (model_path, report_path):
        if artifact:
            Path(artifact).unlink(missing_ok=True)
    if provenance_path:
        Path(provenance_path).unlink(missing_ok=True)
    return validated
