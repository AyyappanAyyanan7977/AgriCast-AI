# Architecture

- Streamlit: dashboard, data setup, prediction form, climate exploration, RAG evidence explorer, MCP status, evaluation.
- scikit-learn pipeline: imputation, categorical encoding, baseline regression model, held-out metrics.
- RAG: text/Markdown ingestion, word-window chunking with overlap, BM25 ranking.
- MCP: local stdio server exposes dataset summary, latest evaluation report, and evidence search.
- Artifacts: CSV and target selection under `data/raw`, joblib model under `data/models`, evaluation JSON under `data/reports`, index chunks under `data/index`.

## Important boundary
The starter's random train/test split is a baseline only. If the dataset has year, location, farm, or temporal dependence, design a time-aware or group-aware split before claiming generalization. Do not interpret correlation or feature importance as causation. The MCP server is separate from Streamlit; the UI displays its catalog and status, but is not itself an MCP client. A compatible MCP client is needed to invoke tools through the protocol.
