# UX review and design rationale

References to apply:
- Steve Krug, *Don't Make Me Think, Revisited*: obvious actions, scannability, predictable navigation.
- Don Norman, *The Design of Everyday Things*: feedback, discoverability, error prevention.
- Jakob Nielsen's 10 usability heuristics: visible system status, consistency, error recovery, recognition rather than recall.
- Streamlit official multipage, state, and chart documentation.
- Plotly heatmap documentation and MCP official specification.

Implemented principles:
- A compact navigation model for distinct user tasks.
- Explicit dataset/model/RAG/MCP status.
- Real-data-only visualizations; no silent synthetic data.
- Input validation and explainable missing-model states.
- Retrieval scores and source identifiers displayed separately from generated answers.
- Expandable detail to avoid overwhelming novice users.

Usability test:
1. Ask 3–5 users to upload a CSV, train a model, locate the MAE, search documents, and identify what an MCP tool does.
2. Measure completion, time, errors, and whether they distinguish retrieval score from truth.
3. Ask them to identify limitations without prompting.
4. Fix the most severe observed issue and repeat.


## Enterprise refresh notes
- Updated palette to deep forest emerald `#0F382C`, mint `#10B981`, slate `#0F172A`, and off-white `#F8FAFC`.
- Added a compact command bar with search and region context. Search filters the overview data preview and can seed evidence search.
- Avoids claiming live MCP uptime from entrypoint existence; the pill is deliberately labelled as configuration status.
- Retained a no-shadow, hairline-first style to keep dense analytics readable. Rounded surfaces remain 8–12px.
- Real map, grounded generative assistant, role management, PDF export, share links, and scheduled jobs are explicit future work, not mocked as functional features.


## Agricultural landing page and horizontal navigation revision (2026-10-16)
- Replaced the dark developer-console landing visual with an agriculture-oriented palette: leaf green, warm field cream, white surfaces, and restrained botanical accents.
- Hero content now speaks to crop planning, season planning, weather signals, and water awareness. It does not imply live weather feeds or farm telemetry.
- Primary navigation is horizontal and located under the AgriCast brand header, like a conventional website menu; the sidebar is secondary/help content only.
- Fixed the route-button navigation state bug: before the keyed navigation widget is created on rerun, the selected horizontal-nav label is updated from the requested destination.
- Route buttons should be manually verified in the running app for Yield forecast, Climate & weather, and Agronomy library. Automated checks can verify syntax but cannot establish browser-level usability.
- Applied Krug/Norman/Nielsen principles from the design notes above: visible destinations, consistent labels, discoverable primary actions, and honest data/model status.


## Reference-matched visual refresh (2026-10-21)

Implemented in the current Streamlit client:
- Persistent white sidebar with AgriCast branding, nine workspace destinations, and an active green navigation state.
- Shared agricultural landscape hero on every page, with page-specific headings and the same glass-style weather/status panel.
- Green/white surfaces, rounded cards, hover transitions, responsive layout adjustments, visible focus states, and reduced-motion handling.
- Persistent bottom crop-row curve decoration.
- A distinct Farm Overview route with live dataset-derived row, column, missing-cell, duplicate-row, schema, and preview details.

Not claimed as implemented:
- Live weather is not connected. The shared weather card clearly says so and does not display invented temperature/humidity values.
- The Knowledge Assistant uses lexical BM25-style passage retrieval, not generative LLM answers.
- The bundled yield data remains synthetic demo data. UI mockup figures such as 92% accuracy, 32°C, or 4.2 tons/acre are not hardcoded as real metrics.
- Browser-level visual regression testing remains a manual release gate; unit tests and compilation do not establish pixel-perfect rendering.
