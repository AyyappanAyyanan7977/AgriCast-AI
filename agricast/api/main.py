"""AgriCast AI HTTP API.

The Streamlit app remains the human-facing client. This API is the service boundary
for future web/mobile clients and integrations. It deliberately returns estimates
with provenance metadata and does not claim calibrated confidence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from agricast.ml.pipeline import load_dataset, load_model, predict_one
from agricast.rag.retriever import BM25Retriever
from agricast.services.status import system_status

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data/raw/crop_yield.csv"
MODEL_PATH = ROOT / "data/models/crop_yield_pipeline.joblib"
REPORT_PATH = ROOT / "data/reports/evaluation.json"
DOC_DIR = ROOT / "data/documents"

app = FastAPI(
    title="AgriCast AI API",
    version="0.2.0",
    description="API for crop data, yield estimates, evaluation reports, and agronomy evidence retrieval.",
)

class ForecastRequest(BaseModel):
    features: dict[str, Any] = Field(..., description="Feature values matching the trained model's feature columns.")

@app.get("/health")
def health() -> dict:
    """Service health; dependency checks are reported separately."""
    return {"status": "ok", "service": "agricast-api", "version": app.version}

@app.get("/v1/system/status")
def system_health() -> dict:
    """Report configured local service components; this is not a production uptime SLA."""
    return system_status()

@app.get("/v1/dataset/summary")
def dataset_summary() -> dict:
    if not DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="No dataset is connected.")
    try:
        df = load_dataset(DATA_PATH)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Dataset could not be read: {type(exc).__name__}")
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "source": "configured_local_dataset",
    }

@app.get("/v1/model/evaluation")
def model_evaluation() -> dict:
    if not REPORT_PATH.exists():
        raise HTTPException(status_code=404, detail="No evaluation report is available. Train and evaluate a model first.")
    try:
        return json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="The evaluation report could not be read.")

@app.post("/v1/forecast")
def forecast(request: ForecastRequest) -> dict:
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=409, detail="No trained model is available.")
    try:
        model, metadata = load_model(MODEL_PATH)
        expected = set(metadata.get("feature_columns", []))
        supplied = set(request.features)
        missing = sorted(expected - supplied)
        extra = sorted(supplied - expected)
        if missing:
            raise HTTPException(status_code=422, detail={"message": "Required model features are missing.", "missing": missing})
        # Extra values are ignored rather than forwarded to the model.
        clean_values = {key: request.features[key] for key in expected}
        value = predict_one(model, clean_values)
        return {
            "estimate": value,
            "target_column": metadata.get("target_column"),
            "model_version": metadata.get("model_version"),
            "estimator": metadata.get("estimator"),
            "extra_fields_ignored": extra,
            "interpretation": "Point estimate only. No calibrated prediction interval is available.",
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Prediction input could not be processed: {type(exc).__name__}")

@app.get("/v1/evidence/search")
def evidence_search(
    q: str = Query(..., min_length=2, max_length=500),
    top_k: int = Query(5, ge=1, le=10),
) -> dict:
    try:
        retriever = BM25Retriever.from_directory(DOC_DIR)
        results = retriever.search(q, top_k)
        return {
            "query": q,
            "retrieval_method": "BM25 lexical retrieval",
            "results": results,
            "note": "Retrieved passages are evidence candidates, not independently verified facts.",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Evidence retrieval failed: {type(exc).__name__}")

@app.get("/v1/system/capabilities")
def capabilities() -> dict:
    return {
        "features": [
            "dataset_summary", "model_evaluation", "yield_forecast",
            "agronomy_evidence_search", "mcp_tool_integration",
        ],
        "not_available": [
            "calibrated_prediction_intervals", "geospatial_field_heatmap",
            "user_role_management", "scheduled_forecast_delivery",
        ],
    }
