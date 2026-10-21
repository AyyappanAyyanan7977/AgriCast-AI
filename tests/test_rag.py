import json
from pathlib import Path
import pytest
from agricast.rag.retriever import BM25Retriever
from agricast.rag.ingest import ingest_directory


def test_empty_query_returns_empty():
    retriever = BM25Retriever([{"chunk_id": "1", "source": "x.txt", "text": "rainfall and crop yield"}])
    assert retriever.search("", 5) == []


def test_matching_query_returns_document():
    retriever = BM25Retriever([{"chunk_id": "1", "source": "x.txt", "text": "rainfall variability affects crop yield"}])
    result = retriever.search("rainfall crop", 3)
    assert result and result[0]["source"] == "x.txt"
    assert result[0]["score"] > 0


def test_irrelevant_query_returns_no_results():
    retriever = BM25Retriever([{"chunk_id": "1", "source": "x.txt", "text": "rainfall variability affects crop yield"}])
    assert retriever.search("quantum spacecraft", 3) == []


def test_ingest_and_retrieve_use_custom_windows_safe_paths(tmp_path):
    docs = tmp_path / "source documents"
    docs.mkdir()
    (docs / "rainfall.md").write_text("Rainfall variability affects rice crop yield.", encoding="utf-8")
    index = tmp_path / "local index" / "chunks.json"
    chunks = ingest_directory(docs, index_path=index)
    assert len(chunks) == 1 and index.exists()
    retriever = BM25Retriever.from_directory(docs, index_path=index)
    result = retriever.search("rainfall rice", 5)
    assert result and result[0]["source"] == "rainfall.md"


def test_from_directory_builds_index_when_missing(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "notes.txt").write_text("Soil moisture supports healthy crops.", encoding="utf-8")
    index = tmp_path / "index" / "chunks.json"
    retriever = BM25Retriever.from_directory(docs, index_path=index)
    assert index.exists()
    assert retriever.search("soil moisture")


def test_missing_document_directory_fails_clearly(tmp_path):
    with pytest.raises(FileNotFoundError, match="Document directory does not exist"):
        BM25Retriever.from_directory(tmp_path / "missing")


def test_nonpositive_top_k_returns_empty():
    retriever = BM25Retriever([{"chunk_id": "1", "source": "x.txt", "text": "rainfall crop"}])
    assert retriever.search("rainfall", 0) == []
