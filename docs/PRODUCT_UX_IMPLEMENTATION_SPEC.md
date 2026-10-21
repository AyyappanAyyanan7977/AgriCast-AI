# AgriCast AI — Product UX & Engineering Implementation Specification

**Status:** Implementation contract / target behavior  
**Audience:** Product owner, frontend, backend, ML and QA  
**Principle:** Design around the farmer/advisor task, not around AI components.  
**Important:** This document describes the intended product. A feature is not considered implemented merely because it appears in this specification or UI. Mark it **Implemented**, **Demo-only**, or **Planned** in the app and release notes.

## 1. Product goals and non-goals

### Primary users
- **Farmer / farm owner:** wants clear, practical crop-planning information with minimal technical language.
- **Agronomist / field advisor:** wants to compare scenarios, inspect sources and explain results.
- **Analyst / system operator:** wants data-quality, model-evaluation, API and MCP diagnostics.

Start with the farmer/advisor journey. Technical controls belong in Advanced / System administration.

### Core user journey
1. Choose or configure farm/season context (until accounts exist, treat this as a local session selection, not a saved farm profile).
2. Upload and validate a dataset.
3. Review data coverage and climate patterns.
4. Generate a yield estimate only when a compatible trained model and valid features are available.
5. Inspect limitations and supporting agronomy passages.
6. Export/save only when persistence/export is implemented.

### Product non-goals for the first stable release
- No claims of live weather unless a live provider is integrated and its update time is displayed.
- No claim that a model prediction is a crop recommendation, guarantee, or calibrated confidence interval.
- No claim that BM25 passage retrieval is a generative RAG answer.
- No fake farm map, alerts, saved profiles, sharing, role permissions or PDF export.
- Synthetic demo data must be visibly labeled and must not be described as real-world validation.

## 2. Global information architecture

### Horizontal primary navigation
1. **Farm data** — upload, map schema, validate and confirm data.
2. **Farm overview** — status, data coverage and next recommended action.
3. **Yield forecasts** — input validation, prediction, assumptions and result history only if history storage exists.
4. **Weather & climate** — historical data analysis and charts supported by the selected dataset.
5. **Agronomy guidance** — search indexed documents and inspect source passages.
6. **Forecast quality** — evaluation protocol, baseline comparison and metrics.
7. **Advanced / System** — API health, MCP tools, model/data artifact status.

Default first-run route should be **Farm data** if no usable dataset has been validated; otherwise **Farm overview**. Navigation must remain visible on desktop and collapse into an accessible menu on narrow screens. Do not rely on icon-only controls.

### Persistent context strip
Show selected dataset name, source/status, selected crop/region/season only when those fields exist, and last refresh/validation timestamp when recorded. Never imply a selected farm is a persisted account unless persistence exists.

### Global UI states
Every page must support: initial/empty, loading, success, recoverable validation error, unavailable dependency, stale/unknown status, and demo-data notice where relevant. Errors must explain what failed and how to recover; do not show raw stack traces to ordinary clients.

## 3. Page-by-page specifications

## Page A — Farm data

**Client job:** safely bring data into the workspace and understand whether it is usable.

### Components
- Page title and one-sentence explanation.
- File uploader supporting CSV for the first release; document other formats as unsupported until implemented.
- Uploaded-file name, size where available, row/column count and encoding/read status.
- Data preview table with bounded row count.
- Schema mapping controls for target column and supported model features.
- Validation summary: missing cells, duplicate rows, duplicate column names, invalid numeric values, unparseable dates, and target availability.
- Errors/warnings table with column, issue, severity and suggested action.
- Buttons: **Preview data**, **Validate dataset**, **Use validated dataset** / **Clear selection**.

### Inputs
- CSV file.
- Optional target column selection (default only if a configured target exists and is valid).
- Optional feature-to-column mappings; units and categories only where supported.

### Outputs
- Parsed preview and schema.
- Validation report and actionable error list.
- A validated in-session dataset selection only after user confirmation.

### Behavior
- Validate file type and size before parsing; handle empty file, malformed CSV, duplicate headers, encoding problems and zero-row data.
- Duplicate columns must be normalized deterministically or rejected with a clear message. Never silently select a random duplicate.
- Do not silently drop rows/columns. If a repair is offered, show the proposed change and require confirmation.
- **Use validated dataset** stays disabled until required checks pass. Warnings may be allowed only when explicitly described.
- If the app currently only loads a fixed local CSV, label the uploader/selection as planned or demo-only; do not present a nonfunctional upload flow.

### Error states
- Unsupported format → “Upload a CSV file.”
- Empty/malformed CSV → explain file is empty or cannot be parsed.
- Duplicate headers → list duplicates and offer deterministic rename or explicit rejection.
- Missing target/required features → identify missing field names and link to mapping.
- Dataset contains no valid rows → block confirmation.

### Backend/service dependencies
- `agricast.services.data_validation` for schema and quality checks.
- Shared dataset-loading service; avoid separate validation rules in UI and API.
- Future API contract: `POST /v1/datasets/validate`, `POST /v1/datasets/activate`, with file limits and safe temporary storage. These endpoints are **planned unless present in code**.

### Acceptance tests
- Valid CSV produces preview and correct row/column counts.
- Empty file, malformed CSV and unsupported extension return user-readable errors.
- Duplicate `rainfall_mm` headers do not reach Plotly or the model as ambiguous duplicate labels.
- Missing target/feature blocks activation and identifies the field.
- UI does not claim upload persistence after app restart unless implemented.

## Page B — Farm overview

**Client job:** understand current data readiness and choose the next action.

### Components
- Welcome/intro with selected dataset and season context, if known.
- Status cards: data readiness, climate coverage, forecast availability, evidence library status. Values must come from actual service responses.
- “Recommended next step” card based on real state, e.g. Validate data, Generate forecast, or Explore climate.
- Small climate/yield summary charts only when valid columns and enough rows exist.
- Recent activity only if event history is stored; otherwise omit.

### Inputs
- Selected active dataset and optional crop/region/season filters.

### Outputs
- Data readiness, supported analysis availability, links to the next task.

### Behavior
- Cards are clickable and route to the relevant page.
- “No dataset” leads to Farm data; “dataset invalid” leads to validation; “no model” explains how to train/load one; valid data/model leads to forecast.
- Never show made-up weather, yield, farm area, notifications or activity.

### Backend/service dependencies
- Shared status service, dataset summary, model status and evidence-index status.
- Existing API includes `GET /v1/dataset/summary` and `GET /v1/system/status`; UI may still call Python modules directly. Do not claim HTTP integration until it is implemented.

### Acceptance tests
- Every card and primary CTA navigates to the correct page.
- Empty/missing dataset produces an onboarding state rather than an exception.
- Values shown match service responses and include units/updated time when applicable.
- Demo data has a visible synthetic-data banner.

## Page C — Yield forecasts

**Client job:** obtain a point estimate for a valid scenario and understand the limitations.

### Components
1. Scenario form: supported crop/category and only model-required features.
2. Unit hints and field-level validation.
3. Input review summary before submission.
4. **Generate estimate** primary action and loading state.
5. Result panel: estimated target, unit, model/version, timestamp and input summary.
6. Model evaluation context: MAE/RMSE/R² from a separate evaluation report, with split/protocol details.
7. Assumptions/limitations and link to relevant agronomy evidence.
8. Export button only after export is implemented.

### Inputs
- Exact feature set required by the loaded model; typed and range-checked using metadata/schema.
- Do not invent fields or use hard-coded sample values as if they were user data.

### Outputs
- Point estimate, target name, model version/estimator and explicit statement if calibrated uncertainty is unavailable.

### Behavior
- Disable submission while invalid or processing.
- Reject missing required features, invalid types, non-finite numbers and unsupported categories with field-level errors.
- Extra fields should be either explicitly ignored with a warning or rejected consistently; document the policy.
- Never label MAE/RMSE as a confidence interval. Do not call a model result “accurate” without supporting held-out evaluation.
- If model artifact is absent/incompatible, explain that no compatible model is available and provide the operator next step.

### Backend/service dependencies
- `agricast.ml.pipeline` for load/predict/metadata; shared forecast service should be called by Streamlit/API/MCP.
- Existing API: `POST /v1/forecast`, `GET /v1/model/evaluation`.
- Pydantic request schema must validate expected feature names, values and ranges.

### Acceptance tests
- Valid input returns a numeric point estimate with target/model metadata.
- Missing required features return a readable validation error.
- Bad types, NaN/infinity and invalid categories are rejected.
- Missing model and malformed model metadata produce controlled errors.
- Evaluation metrics show their evaluation split and units; no fake confidence interval is shown.

## Page D — Weather & climate

**Client job:** explore historical climate/yield relationships in the available dataset.

### Components
- Dataset and coverage banner.
- Available date/region/crop filters, rendered only if corresponding columns exist.
- Time-series chart when a valid time column exists.
- Scatter plot with X/Y selectors, optional grouping, optional trend line.
- Correlation heatmap for numeric columns.
- Chart description, units, record count and missing-value note.

### Inputs
- X/Y columns from unique, supported columns; optional grouping variable; date/crop/region filters only if present.

### Outputs
- Charts and descriptive statistics, not causal claims.

### Behavior
- Normalize/reject duplicate column labels before plotting.
- Prevent X and Y selecting the same field unless explicitly supported.
- Trendline must not introduce an undeclared `statsmodels` dependency; use a declared dependency or NumPy least-squares implementation.
- Handle empty data, all-null columns, constant X, nonnumeric values and fewer than two valid observations.
- Clearly distinguish historical observations from live weather or future forecast data.

### Backend/service dependencies
- Shared dataset service and climate-analysis functions.
- Plotly for charts; NumPy/Pandas for calculations. Dependency list must match actual imports.

### Acceptance tests
- Scatter plot works without `statsmodels` if the app claims no such dependency.
- Duplicate headers are handled before chart construction.
- Empty and all-null selections show helpful messages.
- Trendline is omitted with explanation when there are too few distinct X values.
- Filters alter the displayed dataset and chart as expected.

## Page E — Agronomy guidance

**Client job:** find relevant passages and inspect their original sources.

### Components
- Search box with example questions and clear button.
- Top-K selector with safe bounded values.
- Search results cards containing document title/source, passage, retrieval score/rank and location/section metadata if available.
- “Open source” action only if a valid URL or local source reference exists.
- Empty-results guidance and indexed-document count/status.
- Clear notice: retrieved passages are evidence candidates, not guaranteed facts.

### Inputs
- Query string (minimum length and maximum length enforced).
- Top-K integer in allowed range.

### Outputs
- Ranked text passages, source metadata and retrieval method. Current BM25/lexical search is not an LLM-generated answer.

### Behavior
- Empty index, missing directory, unsupported document type and no-match query must be handled distinctly.
- Preserve metadata through ingestion and retrieval. Never invent source URL, author, date or citation.
- If a grounded LLM answer is added later, cite supporting passages and abstain when evidence is insufficient.

### Backend/service dependencies
- `agricast.rag.ingest`, `agricast.rag.retriever` and shared evidence service.
- Existing API: `GET /v1/evidence/search?q=...&top_k=...`.

### Acceptance tests
- Known query retrieves the expected source passage in a small fixture corpus.
- No-match query returns a clear empty state.
- Missing documents/index does not crash the page.
- Every displayed source field maps to stored metadata.
- Path handling works with Windows paths and spaces.

## Page F — Forecast quality

**Client job:** understand model evaluation and limits; this is mainly for advisors/analysts.

### Components
- Model and dataset identifiers/version.
- Evaluation protocol: train/validation/test or time/region holdout details.
- MAE, RMSE and R² cards with target units and definitions.
- Baseline versus selected model comparison.
- Per-crop/region breakdown only when sample sizes support it.
- Data limitations, leakage audit, evaluation date and report provenance.

### Inputs
- Read-only model/evaluation report filters where available; no retraining controls until safe training workflow exists.

### Outputs
- Reproducible metrics and a clear interpretation.

### Behavior
- If report is missing/stale/malformed, show that state; do not fabricate metrics.
- Display `R²` as undefined where mathematically inappropriate rather than silently replacing it.
- Metrics from synthetic data must be labeled as demo-only and not as real-world validation.

### Backend/service dependencies
- `agricast.ml.pipeline`, versioned evaluation report under `data/reports/` and `GET /v1/model/evaluation`.
- Future: reproducible evaluation command and report schema validation.

### Acceptance tests
- UI metrics exactly match the report file.
- Missing/malformed report produces an actionable empty state.
- Report includes dataset provenance, split method and target units.
- Baseline comparison is only shown when both models were evaluated on the same split.

## Page G — Advanced / System

**Client job:** let an authorized operator troubleshoot integrations and local components.

### Components
- API health and dependency status, each with last-checked time if recorded.
- Model/data/index artifact availability.
- MCP server/tool list, transport type and tool descriptions.
- Copyable diagnostic details that omit secrets and private data.
- Configuration instructions and a safe retry/check action where applicable.

### Inputs
- Health-check/retry actions; configuration values must come from secure environment settings, not UI text or source code.

### Outputs
- Accurate status per component: available, unavailable, not configured, or unknown.

### Behavior
- A config file existing does not prove a remote integration is connected.
- Never display API keys, tokens, raw environment variables or full sensitive paths.
- MCP tools must validate arguments and call shared service functions; no arbitrary filesystem access or uncontrolled shell execution.
- Keep advanced system content out of the farmer's primary navigation if it causes confusion.

### Backend/service dependencies
- `agricast.services.status`, FastAPI health/status endpoints and MCP stdio server.
- Existing API includes `/health`, `/v1/system/status`, `/v1/system/capabilities`.

### Acceptance tests
- Missing model/dataset/index reports the correct status without crashing.
- Health endpoint responds independently of UI rendering.
- MCP tool schemas reject invalid inputs and return structured errors.
- Diagnostics contain no secrets.
- Status labels distinguish configured from verified-connected.

## 4. Shared interaction and visual contract

- Keep agriculture-inspired green/cream palette, clear typography, consistent spacing and horizontal navigation.
- One primary CTA per page; secondary actions use lower visual emphasis.
- All controls have visible labels; icons supplement rather than replace text.
- Desktop navigation must not clip; mobile navigation must be keyboard/touch accessible.
- Use consistent success/warning/error states with text and icon, not color alone.
- Tables need clear empty states and bounded previews; charts need axis labels and units.
- Preserve selected filters on rerun where sensible, but reset dependent state when the dataset changes.
- Use stable Streamlit widget keys. Do not mutate widget state after the widget is instantiated in the same run.
- Provide actionable errors to clients and log technical details for developers without exposing tracebacks in the normal UI.

## 5. Target architecture and service boundaries

Use a modular monolith for the current resource constraints. Streamlit, FastAPI and MCP should call the same service functions; they must not each reimplement business logic.

```text
app.py (Streamlit client)
        |
        v
agricast/services/  <-- shared application use-cases
   |       |       |
   v       v       v
 data     ml      rag
validation pipeline retrieval
        ^
        |
FastAPI routes + MCP tools (adapters, not duplicate business logic)
```

Suggested future modules:
- `agricast/services/datasets.py`: load, validate, activate dataset.
- `agricast/services/forecasting.py`: validate features and invoke model.
- `agricast/services/climate.py`: chart-ready filtered data and descriptive analysis.
- `agricast/services/evidence.py`: index/search and source metadata.
- `agricast/schemas/`: shared Pydantic request/response models.
- `tests/unit`, `tests/integration`, `tests/evaluation`.

The existing UI may still invoke Python modules directly. Do not claim that Streamlit uses FastAPI as its transport until that integration is actually implemented. A modular monolith does not require microservices or a cloud deployment.

## 6. API contract inventory

### Existing routes in current release (verify against code before release)
- `GET /health`
- `GET /v1/system/status`
- `GET /v1/dataset/summary`
- `GET /v1/model/evaluation`
- `POST /v1/forecast`
- `GET /v1/evidence/search?q=&top_k=`
- `GET /v1/system/capabilities`

### Planned routes, not to be represented as existing
- `POST /v1/datasets/validate`
- `POST /v1/datasets/activate`
- `GET /v1/climate/summary` (only after a shared climate service exists)
- `POST /v1/reports` or equivalent export endpoint (only after report generation is implemented)

All APIs must define request/response schemas, status codes, input limits, and error payloads. Never accept arbitrary local file paths from untrusted clients.

## 7. Test strategy and release gates

### Unit tests
- Duplicate and blank column names; empty/malformed CSV; missing columns; invalid numeric/date values.
- Model feature validation; missing model; invalid/non-finite input; target metadata.
- Retrieval relevance, empty corpus, no matches, metadata preservation and Windows paths.
- Climate chart preparation for duplicate headers, empty frames, nulls, constant X and invalid selections.

### Integration tests
- API health, dataset summary, model evaluation, forecast, evidence search and error cases.
- Streamlit page helpers/service calls with representative valid and invalid states.
- MCP tool arguments and returned payloads.

### Manual acceptance walkthrough
1. Start from a clean environment using documented setup.
2. Open each primary navigation page and verify there is no clipping or broken route.
3. Load/validate data; try a malformed file and duplicate columns.
4. Create a climate scatter plot with and without trendline.
5. Generate a forecast with valid inputs, then missing/invalid inputs.
6. Search a known agronomy phrase and verify source metadata.
7. Open Forecast quality and confirm metrics match the report.
8. Open Advanced/System and verify missing components are accurately represented.
9. Repeat at a narrow viewport and use keyboard navigation.
10. Confirm synthetic data, unavailable capabilities and limitations are clearly labeled.

### Release gate
Release only when:
- All automated tests pass in a clean environment.
- No critical page/action fails in the manual walkthrough.
- Dependency installation is reproducible from `requirements.txt`.
- README and UI do not claim unavailable functionality.
- Demo-data provenance and model limitations are visible.
- Remaining issues are documented with severity and workaround.

## 8. Definition of done for each feature

A feature is done only when all of these are true:
1. UI control and label are clear to a nontechnical user.
2. Input schema and validation are defined.
3. Success, empty, loading, and error states are implemented.
4. Service/backend behavior is defined and shared where possible.
5. Unit and integration tests cover the important success and failure paths.
6. The UI displays truthful provenance, status and limitations.
7. The feature has been manually exercised in the running application.
8. README and release notes accurately describe its implementation status.


## Implementation update — client clarity and single-command startup

- The overview is task-led and guides the user through data, climate, yield and evidence.
- Page intros explain purpose and interpretation in plain language.
- Synthetic demo data is explicitly labeled.
- Added `run.py` to start FastAPI and Streamlit from one terminal; Ctrl+C shuts down both.
- Acceptance command: `python -m pytest -q`.
