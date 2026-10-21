from pathlib import Path
import json
from datetime import datetime, timezone
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def load_dataset(path="data/raw/crop_yield.csv"):
    return pd.read_csv(path)

def _build_pipeline(X, choice):
    numeric = X.select_dtypes(include=np.number).columns.tolist()
    categorical = [c for c in X.columns if c not in numeric]
    transformers = []
    if numeric:
        transformers.append(("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric))
    if categorical:
        transformers.append(("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), categorical))
    prep = ColumnTransformer(transformers=transformers, remainder="drop")
    if choice == "Random Forest":
        estimator = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1, min_samples_leaf=2)
    elif choice == "Extra Trees":
        estimator = ExtraTreesRegressor(n_estimators=200, random_state=42, n_jobs=-1, min_samples_leaf=2)
    else:
        estimator = Ridge(alpha=1.0)
        if numeric and not categorical:
            prep = ColumnTransformer([("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric)])
    return Pipeline([("preprocess", prep), ("model", estimator)])

def train_and_evaluate(df, target, test_size, choice, model_path, report_path):
    if target not in df.columns:
        raise ValueError(f"Target column {target!r} not found.")
    clean = df.dropna(subset=[target]).copy()
    y = pd.to_numeric(clean[target], errors="coerce")
    clean = clean.loc[y.notna()].copy()
    y = y.loc[y.notna()]
    X = clean.drop(columns=[target])
    if X.empty:
        raise ValueError("No feature columns remain after removing the target.")
    if len(clean) < 20:
        raise ValueError("At least 20 valid rows are required for this starter split; more data is strongly recommended.")
    if not pd.api.types.is_numeric_dtype(y):
        raise ValueError("This baseline supports a numeric regression target.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    pipeline = _build_pipeline(X_train, choice)
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = float(r2_score(y_test, preds)) if len(y_test) > 1 else None
    model_path = Path(model_path); model_path.parent.mkdir(parents=True, exist_ok=True)
    meta = {"target_column": target, "feature_columns": X.columns.tolist(), "model_version": datetime.now(timezone.utc).strftime("baseline-%Y%m%dT%H%M%SZ"), "estimator": choice, "trained_at_utc": datetime.now(timezone.utc).isoformat(), "n_rows": len(clean)}
    joblib.dump({"pipeline": pipeline, "metadata": meta}, model_path)
    report = {"mae":mae, "rmse":rmse, "r2":r2, "n_rows":len(clean), "n_test":len(y_test), "random_state":42, "test_size":test_size, "estimator":choice, "target_column":target, "model_version":meta["model_version"], "evaluation_note":"Random holdout baseline. Review time/geographic leakage and use a suitable split before claiming generalization."}
    report_path = Path(report_path); report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

def load_model(path):
    obj = joblib.load(path)
    return obj["pipeline"], obj["metadata"]

def predict_one(model, values):
    return float(model.predict(pd.DataFrame([values]))[0])
