# AgriCast AI release checklist

## Automated checks

- [ ] Create a clean virtual environment and install `requirements.txt` (scikit-learn pinned to the bundled model version).
- [ ] Run `python -m compileall -q app.py agricast tests`.
- [ ] Run `python -m pytest -q`.
- [ ] Confirm the test workflow passes in CI.

## Manual smoke test

- [ ] Run `python run.py`; verify the launcher reports both FastAPI and Streamlit health checks as passed.
- [ ] Confirm missing dependencies, occupied ports, and startup failures produce actionable errors.
- [ ] Press `Ctrl+C`; confirm both services stop and API logs are available at `data/logs/api.log`.
- [ ] Launch Streamlit and confirm the brand header/subtitle are fully visible.
- [ ] Click each horizontal navigation item and verify the expected page opens.
- [ ] From Field overview, test every shortcut button.
- [ ] Upload a CSV; verify target selection, saving, and schema/missingness review.
- [ ] Train a model; confirm the evaluation report and artifact are created.
- [ ] Make a forecast with the saved feature schema; confirm it is labelled as a point estimate.
- [ ] Plot two numeric fields, try optional grouping, and inspect the correlation heatmap.
- [ ] Index TXT/Markdown documents and test a relevant query, an irrelevant query, and an empty index.
- [ ] Test MCP handshake and inspect tool names/outputs.
- [ ] Start FastAPI separately and verify `/health`, `/docs`, and `/v1/system/capabilities`.
- [ ] Confirm synthetic-data warnings remain visible and no placeholder metric is presented as real-world evidence.

## Release decision

Do not call the project production-ready until automated checks and the manual smoke test pass, real-data evaluation is documented, and security/deployment gaps have an explicit plan.


## Final feature audit (2026-10-21)

- [x] Legacy home quick-action labels resolve to valid navigation choices.
- [x] CSV save validates the target and invalidates stale model/evaluation artifacts.
- [x] Sample CSV bundled at `data/sample_upload.csv`; model train/evaluate/predict smoke test completed on synthetic sample.
- [x] Unit/API/navigation/dataset tests: 26 passed; Python compilation passed.
- [x] Local BM25 retrieval smoke test returned a passage from the bundled agronomy corpus.
- [ ] Supabase live signup/login/profile persistence: requires the user's Supabase project credentials and browser verification.
- [ ] MCP live protocol handshake: run the Integrations page's **Test MCP connection** after installing `requirements.txt`.
- [ ] Browser walkthrough across all pages at desktop/mobile sizes.
- [ ] Verify Open-Meteo live panel and fallback inside the user's local browser for several regions.

Do not mark the project production-ready until all unchecked external/manual checks are completed. Sample and bundled datasets are synthetic.
