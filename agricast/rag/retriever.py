"""Dependency-light BM25 lexical retrieval with portable project-relative paths."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import math
import re

from .ingest import ingest_directory


def tokenize(text):
    """Normalize text with a consistent, dependency-light tokenizer."""
    return re.findall(r"[a-zA-Z0-9]+", str(text).lower())


class BM25Retriever:
    def __init__(self, chunks, k1=1.5, b=0.75):
        self.chunks = list(chunks)
        self.corpus = [tokenize(chunk.get("text", "")) for chunk in self.chunks]
        self.k1 = float(k1)
        self.b = float(b)
        self.doc_freq = Counter()
        for tokens in self.corpus:
            self.doc_freq.update(set(tokens))
        self.avgdl = (sum(map(len, self.corpus)) / len(self.corpus)) if self.corpus else 0.0

    @classmethod
    def from_directory(cls, directory="data/documents", index_path=None, rebuild=False):
        directory = Path(directory).expanduser().resolve()
        index = Path(index_path).expanduser().resolve() if index_path else directory.parent / "index" / "chunks.json"
        if rebuild or not index.exists():
            ingest_directory(directory, index_path=index)
        try:
            chunks = json.loads(index.read_text(encoding="utf-8"))
            if not isinstance(chunks, list):
                raise ValueError("The document index must contain a JSON list.")
        except json.JSONDecodeError as exc:
            raise ValueError(f"Document index is invalid JSON: {index}") from exc
        return cls(chunks)

    def search(self, query, top_k=5):
        query_tokens = tokenize(query)
        if not self.corpus or not query_tokens or not isinstance(top_k, int) or top_k <= 0:
            return []
        n_docs = len(self.corpus)
        scores = []
        for tokens in self.corpus:
            counts = Counter(tokens)
            length = len(tokens)
            score = 0.0
            for term in set(query_tokens):
                frequency = counts.get(term, 0)
                if not frequency:
                    continue
                # BM25+ style positive IDF avoids zero/negative scores for tiny corpora.
                idf = math.log(1.0 + (n_docs - self.doc_freq[term] + 0.5) / (self.doc_freq[term] + 0.5))
                denominator = frequency + self.k1 * (1.0 - self.b + self.b * length / (self.avgdl or 1.0))
                score += idf * frequency * (self.k1 + 1.0) / denominator
            scores.append(score)
        matched = [i for i, score in enumerate(scores) if score > 0]
        matched.sort(key=lambda i: scores[i], reverse=True)
        return [{
            "chunk_id": self.chunks[i].get("chunk_id", str(i)),
            "source": self.chunks[i].get("source", "unknown"),
            "text": self.chunks[i].get("text", ""),
            "score": float(scores[i]),
        } for i in matched[:top_k]]
