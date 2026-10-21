# AgriCast AI — Field & Crop Intelligence

AgriCast AI is a local-first agricultural analytics portfolio project combining a consistent, reference-inspired green-and-white Streamlit workspace, a scikit-learn yield-regression baseline, climate exploration, lexical agronomy-document retrieval, a FastAPI service boundary, and an MCP stdio tool server.

The shared UI shell is used on every page: branded farm-photo hero, workspace navigation, utility search, weather-connection status, white cards, green accents, and decorative crop-row curves. The weather panel requests current conditions from Open-Meteo for the selected region. If the provider is unavailable, it clearly labels the temperature fallback as a demo default and leaves unavailable measurements blank.

> **Data caution:** the bundled `data/raw/crop_yield.csv` is synthetic demonstration data. Its metrics and predictions are not evidence of real agricultural performance and must not be used for farm decisions. Replace it with a licensed, documented dataset before making substantive claims.

## Quick start — Windows PowerShell

From the extracted `AgriCast_AI_Client_Ready` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

The launcher starts FastAPI and Streamlit, waits for both health checks, and stops both when you press Ctrl+C. Open `http://localhost:8501`. If the virtual environment already exists, skip its creation and run the install command to synchronize dependencies.

Use Python 3.13 or 3.11 if available and compatible with the pinned model artifact; the bundled scikit-learn model was saved with scikit-learn 1.8.0.

## Main workflows

1. **Farm data:** upload a CSV, review its schema and missingness, choose the numeric target, and save it. A new upload invalidates the old model and report; retrain in Model quality before forecasting. A synthetic test file is bundled at `data/sample_upload.csv`.
2. **Model quality:** train a baseline estimator and review held-out MAE, RMSE, and R².
3. **Yield forecast:** submit feature values that match the trained model's schema. Outputs are point estimates, not calibrated intervals.
4. **Climate & weather:** explore scatter plots and Pearson/Spearman correlations from available columns. Correlation is not causation.
5. **Agronomy library:** index trusted `.txt` or `.md` sources and search the returned passages. This is lexical retrieval, not an LLM answer-generation system.
6. **Integrations:** inspect MCP tool metadata and test the local stdio protocol connection.

## Start the API

In a second terminal, from the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn agricast.api.main:app --host 127.0.0.1 --port 8000
```

- Health: `http://127.0.0.1:8000/health`
- Interactive API docs: `http://127.0.0.1:8000/docs`

The Streamlit UI currently calls shared Python modules directly; it does not yet use HTTP as its transport. The API and MCP adapter are separate interfaces over the project capabilities. The weather card uses Open-Meteo current conditions when reachable; its fallback is labeled and is not live weather.

## Test before changing or releasing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q app.py agricast tests
```

Tests cover baseline training guards, retrieval ranking, empty/irrelevant queries, indexing with paths containing spaces, API health/capability contracts, and query validation. They do not replace a live browser walkthrough or evaluation on a real dataset.

## Project structure

```text
agricast/
├── api/          # FastAPI routes and request schemas
├── ml/           # Training, evaluation, model loading, prediction
├── rag/          # TXT/Markdown ingestion and BM25-style lexical retrieval
└── services/     # MCP server and system status
app.py            # Streamlit client
data/             # Demo CSV, model artifact, documents, index and report
 tests/           # Unit and API contract tests
 docs/            # Architecture, security, UX and evaluation guidance
```

## Architecture decisions

- **Modular monolith:** appropriate for a laptop-first project; avoids microservice deployment overhead.
- **Shared Python services:** UI, API, and MCP should call the same business logic to avoid divergent implementations.
- **Local paths anchored to the project:** avoids behavior changing with the current working directory and supports Windows paths.
- **Dependency-light retrieval:** a small in-repository BM25 implementation removes a runtime dependency on `rank-bm25` while preserving lexical retrieval behavior.
- **Honest status:** MCP entrypoint presence is not proof of uptime; synthetic-data scores are not real-world validation; lexical passage retrieval is not generative RAG.

## Known limitations — not represented as shipped functionality

- Bundled dataset and initial model artifact are demonstration-only.
- The training workflow uses a random holdout split. Temporal or geographic leakage must be investigated and an appropriate split implemented when real data has those structures.
- No calibrated prediction intervals or validated confidence score.
- RAG supports plain text and Markdown only, with no LLM answer generation or automatic claim-level citation verification.
- No GIS field heatmap or live weather service.
- The Streamlit client does not yet call FastAPI over HTTP.
- No production authentication/authorization, multi-user isolation, rate limiting, TLS termination, deployment hardening, scheduled delivery, or centralized audit observability.

See `docs/ARCHITECTURE.md`, `docs/ML_EVALUATION.md`, `docs/SECURITY.md`, and `RELEASE_CHECKLIST.md` before presenting the project as production-ready.


## Client-friendly UX update

The dashboard now uses a task-led home page: add farm data, review climate, estimate yield, and inspect agronomy evidence. Page introductions explain what each feature does and what its results mean. The app labels bundled synthetic data as demo-only and clarifies that climate charts are based on uploaded data rather than automatically live weather.

## Run the complete application with one command (Windows)

From this project folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

The final command starts both FastAPI (`http://127.0.0.1:8000`) and Streamlit (`http://localhost:8501`). Use only `run.py` for normal development; do not open a second terminal for Uvicorn. Press Ctrl+C in the same terminal to stop both processes.

To verify the test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```


## Run the complete application (single command)

Create the environment and install dependencies once:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start both FastAPI and Streamlit from one PowerShell terminal:

```powershell
.\.venv\Scripts\python.exe run.py
```

The launcher checks required packages and port availability, waits for both HTTP health checks, writes FastAPI logs to `data/logs/api.log`, and stops both services when you press `Ctrl+C`. If startup fails, follow the explicit error message rather than assuming the dashboard is ready. The bundled model was serialized with scikit-learn 1.8.0, so `requirements.txt` pins that version to avoid incompatible model-loading warnings.

## Supabase login and farm-region weather

1. Copy `.env.example` to `.env`.
2. Set `SUPABASE_URL` and the project's **public anon/publishable key**. Never use the Supabase service-role key in this app.
3. Enable Email auth in Supabase Authentication. Email confirmation may need to be completed before the first sign-in, depending on project settings.
4. Launch with `python run.py`. Users can create an account with their name and farm region, then sign in. Name and region are stored in Supabase user metadata; the access token remains in the Streamlit session.
5. Weather is fetched from Open-Meteo for the selected region. If the live provider cannot be reached, the panel displays a region-specific demo temperature marked **DEMO DEFAULT — not live weather**; humidity/rainfall/wind remain unavailable instead of being invented.

If Supabase is not configured, the login page offers an explicitly labelled local demo mode. Demo mode is not authentication and should not be used for a production deployment.


## Supabase setup and profile persistence

Copy `.env.example` to `.env`, set `SUPABASE_URL` and `SUPABASE_ANON_KEY` (public anon/publishable key only), and enable email/password auth in Supabase. Signup stores the client's full name and selected region in user metadata; sign-in reads that metadata. Use **Save profile and region** in Workspace settings to persist later edits. If Supabase is not configured, local demo mode is explicitly unauthenticated and does not persist a real account.

## CSV refresh and stale-model protection

The upload path validates that the chosen target contains numeric values, removes duplicate column names (keeping the first), saves the dataset and target, and deletes any previous model/evaluation report. This prevents old metrics from being presented as if they belong to the new dataset. Train and evaluate the new data before running predictions.
