import pandas as pd
from agricast.ml.pipeline import train_and_evaluate

def test_pipeline_trains_on_small_numeric_dataset(tmp_path):
    df = pd.DataFrame({
        "rainfall": list(range(1, 61)),
        "temperature": [25 + (i % 6) for i in range(60)],
        "region": ["A" if i % 2 else "B" for i in range(60)],
        "yield": [2.0 + i * 0.04 for i in range(60)],
    })
    result = train_and_evaluate(df, "yield", 0.2, "Random Forest", tmp_path/"model.joblib", tmp_path/"eval.json")
    assert result["n_test"] > 0
    assert result["mae"] >= 0
    assert (tmp_path/"model.joblib").exists()


def test_pipeline_rejects_missing_target():
    import pytest
    df = pd.DataFrame({"rainfall": range(25), "temperature": range(25)})
    with pytest.raises(ValueError, match="Target column"):
        train_and_evaluate(df, "yield", 0.2, "Ridge Regression", "unused.joblib", "unused.json")


def test_pipeline_rejects_too_few_rows():
    import pytest
    df = pd.DataFrame({"rainfall": range(10), "yield": range(10)})
    with pytest.raises(ValueError, match="At least 20 valid rows"):
        train_and_evaluate(df, "yield", 0.2, "Ridge Regression", "unused.joblib", "unused.json")
