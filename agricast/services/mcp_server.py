"""Local MCP server using stdio. Run: python -m agricast.services.mcp_server"""
import json
from pathlib import Path
import pandas as pd
from agricast.rag.retriever import BM25Retriever

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def get_dataset_summary():
    path = PROJECT_ROOT / "data/raw/crop_yield.csv"
    if not path.exists():
        return {"status":"unavailable","message":"No dataset is configured."}
    df = pd.read_csv(path)
    return {"status":"ok","rows":int(len(df)),"columns":df.columns.tolist(),
            "missing_by_column":{str(k):int(v) for k,v in df.isna().sum().items()}}

def get_model_evaluation():
    path = PROJECT_ROOT / "data/reports/evaluation.json"
    if not path.exists(): return {"status":"unavailable","message":"No evaluation report found."}
    return json.loads(path.read_text(encoding="utf-8"))

def search_agricultural_evidence(query: str, top_k: int = 5):
    if not isinstance(query, str) or not query.strip(): return {"results":[],"message":"Query must not be empty."}
    top_k = max(1, min(int(top_k), 10))
    docs = PROJECT_ROOT / "data/documents"
    index = PROJECT_ROOT / "data/index/chunks.json"
    results = BM25Retriever.from_directory(docs, index_path=index).search(query, top_k)
    return {"results":results,"count":len(results)}

try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("agricast-ai")
    mcp.tool()(get_dataset_summary)
    mcp.tool()(get_model_evaluation)
    mcp.tool()(search_agricultural_evidence)
    if __name__ == "__main__":
        mcp.run(transport="stdio")
except ImportError:
    if __name__ == "__main__":
        raise SystemExit("MCP dependency missing. Install requirements.txt first.")
