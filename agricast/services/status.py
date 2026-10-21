from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS = [
 {"name":"get_dataset_summary","description":"Return dataset dimensions, columns, and missingness summary","access":"read-only"},
 {"name":"get_model_evaluation","description":"Return the latest persisted model evaluation report","access":"read-only"},
 {"name":"search_agricultural_evidence","description":"Search indexed local agricultural text passages using BM25","access":"read-only"},
]
def system_status():
    docs_dir = PROJECT_ROOT / "data/documents"
    docs = list(docs_dir.glob("*.txt")) + list(docs_dir.glob("*.md")) if docs_dir.exists() else []
    return {"mcp_entrypoint_exists":(PROJECT_ROOT / "agricast/services/mcp_server.py").exists(),
            "mcp_tool_count":len(TOOLS), "tools":TOOLS, "rag_documents":len(docs)}
