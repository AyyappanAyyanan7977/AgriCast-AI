# AgriCast AI: client vs backend responsibilities

## Client (what the customer sees)
Keep the interface focused on decisions and next actions:
- Executive overview: dataset freshness/status, trained model/version, recent evaluation metrics, and clearly labelled alerts.
- Yield forecast: selected field/crop context, validated input form, point estimate, model version, target units, and a visible limitation note.
- Climate analysis: filters, charts, missing-data indicators, and source/time range.
- Agronomy knowledge: question/search input, retrieved excerpts, document title/section, source link when available, and retrieval status. Do not show hidden chain-of-thought.
- Model performance: MAE, RMSE, R², evaluation date, test size, split strategy, dataset version, and model limitations.
- Integrations: connection state, last successful check, available tools, and actionable error message.
- Data sources: dataset source, last ingestion time, row/column counts, validation errors, missingness, duplicates, and target definition.

## Backend (never trust the browser for these)
- Data ingestion, file validation, schema/size limits, and provenance metadata.
- Model training, artifact versioning, prediction validation, and evaluation reports.
- RAG parsing/chunking, source hashes, indexing, retrieval, and access controls.
- MCP server tools, protocol validation, argument schemas, timeouts, and audit events.
- Authentication/authorization, secrets, rate limiting, logging, and data retention policies.
- API input validation, structured errors, request IDs, health checks, and metrics.
- Tests, CI checks, dependency pinning, backups, and model/data rollback procedures.

## Included in this repository
- Streamlit remains the current client UI.
- `agricast/api/main.py` adds a FastAPI service boundary for health, dataset summary, evaluation, forecast, and evidence search.
- Start API with `python -m uvicorn agricast.api.main:app --host 127.0.0.1 --port 8000`.
- Open API docs at `http://127.0.0.1:8000/docs`.
- Streamlit currently calls shared Python modules directly; connecting the Streamlit UI to HTTP endpoints is a separate integration task.

## Required before production deployment
1. Replace synthetic/demo data with a licensed, documented dataset and verify units/target semantics.
2. Add authentication and role-based authorization before exposing the API beyond localhost.
3. Add upload size/type limits, malware scanning where appropriate, and strict path handling.
4. Use temporal/geographic/grouped validation where data structure requires it; add baseline comparisons and drift monitoring.
5. Add request logging without secrets, audit trail, rate limits, timeouts, and operational monitoring.
6. Add calibrated uncertainty only after validating a suitable method; do not label an uncalibrated score as confidence.
7. Add real geospatial data before rendering field maps or heatmaps.
8. Add PDF export, share permissions, and scheduling only when implemented and tested.
