# Security and safety checklist

- Do not commit secrets, private datasets, or licensed data without permission.
- Do not expose the Streamlit development server directly to the public internet.
- Restrict uploaded file size and validate dataset schema before production deployment.
- Treat uploaded CSV and documents as untrusted input.
- Only load model artifacts you trained or otherwise trust; joblib/pickle loading can execute code.
- MCP tools are read-only in this starter. Keep schemas narrow, validate arguments, cap result sizes, and avoid arbitrary code/file access.
- Add authentication, authorization, rate limiting, TLS, audit retention, and deployment hardening before multi-user production use.
- BM25 score is a ranking score, not a calibrated probability or truth score.
