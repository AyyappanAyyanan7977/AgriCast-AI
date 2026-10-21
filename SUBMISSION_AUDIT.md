# AgriCast AI — Pre-submission audit

## Automated checks performed in the build environment

- Python compilation: passed (`python -m compileall -q app.py agricast tests`).
- Unit/API/navigation/dataset workflow tests: 26 passed.
- CSV replacement helper test: verifies saved rows/target, removal of stale model/evaluation artifacts, and removal of the bundled synthetic-data provenance marker.
- Navigation regression tests: legacy labels including `Climate & weather`, `Yield forecast`, and `Agronomy library` normalize to valid navigation options.
- RAG retrieval smoke test: local Markdown corpus indexed and a query returned a matching passage.
- ZIP integrity: checked before delivery.

## External/manual checks still required before claiming production readiness

1. Supabase: set `.env` using `.env.example`, enable email/password auth, then test signup, email confirmation (if enabled), login, profile/region update, logout, and a second user. This build environment has no project credentials, so a live auth round-trip was not performed.
2. Browser: run `python run.py`; inspect every page at desktop and mobile widths, including CSV upload, weather refresh, prediction, model quality, retrieval, and MCP integration status.
3. Weather: Open-Meteo request succeeded from the user's Windows machine in their supplied terminal log. Verify the in-app response for multiple selected regions and offline fallback.
4. ML: train on the sample upload, confirm the held-out MAE/RMSE/R² report is generated, and check prediction feature schema. The sample is synthetic and its scores are not real-world evidence.
5. MCP: protocol handshake requires the `mcp` dependency installed from requirements. It was not executable in this isolated build environment because the MCP package is absent here; the UI has a live handshake button for local verification.
6. Security: use only the Supabase public anon/publishable key in the Streamlit app; never commit `.env`; do not expose a service-role key. This local Streamlit demo does not provide production-grade per-user data isolation.

## Data semantics

- Uploaded CSV values drive dataset summary and climate charts.
- Saving a new CSV invalidates the previous model artifact and evaluation report so old metrics cannot be mistaken for results on the new data. Retrain explicitly in Model Quality.
- Weather is independent of the CSV and follows the saved/selected region. If live weather is unavailable, the temperature fallback is explicitly labeled as a demo default; missing humidity/rainfall/wind are shown as unavailable.
- The retrieval subsystem is BM25 lexical retrieval over TXT/Markdown passages, not an LLM-generated RAG answer system.
- The bundled and sample data are synthetic. Do not claim agronomic validity from them.
