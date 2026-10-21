import pandas as pd
import pytest
from agricast.services.data_validation import keep_first_duplicate_columns, dataset_quality_summary


def test_duplicate_columns_keep_first_occurrence():
    frame = pd.DataFrame([[10, 99, 3]], columns=["rainfall_mm", "rainfall_mm", "temperature_c"])
    result = keep_first_duplicate_columns(frame)
    assert result.columns.tolist() == ["rainfall_mm", "temperature_c"]
    assert result.iloc[0].tolist() == [10, 3]
    assert frame.shape[1] == 3  # original frame is not mutated


def test_quality_summary_reports_missing_and_duplicate_rows():
    frame = pd.DataFrame({"rainfall": [10, 10, None], "yield": [2, 2, 3]})
    summary = dataset_quality_summary(frame)
    assert summary["rows"] == 3
    assert summary["missing_cells"] == 1
    assert summary["duplicate_rows"] == 1
    assert "yield" in summary["numeric_columns"]


def test_non_dataframe_is_rejected():
    with pytest.raises(TypeError):
        keep_first_duplicate_columns([1, 2, 3])
