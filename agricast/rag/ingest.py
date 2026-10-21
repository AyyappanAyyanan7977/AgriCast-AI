"""Ingest local TXT/Markdown documents into a portable JSON chunk index."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json


def ingest_directory(directory="data/documents", chunk_words=180, overlap_words=35, index_path=None):
    directory = Path(directory).expanduser().resolve()
    if chunk_words < 1:
        raise ValueError("chunk_words must be at least 1")
    if overlap_words < 0 or overlap_words >= chunk_words:
        raise ValueError("overlap_words must be >= 0 and smaller than chunk_words")
    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(f"Document directory does not exist: {directory}")

    chunks = []
    for path in sorted([*directory.glob("*.txt"), *directory.glob("*.md")]):
        text = path.read_text(encoding="utf-8", errors="replace")
        words = text.split()
        if not words:
            continue
        step = chunk_words - overlap_words
        for start in range(0, len(words), step):
            part = " ".join(words[start:start + chunk_words])
            if not part:
                continue
            digest = hashlib.sha256((path.name + str(start) + part).encode("utf-8")).hexdigest()[:16]
            chunks.append({
                "chunk_id": digest,
                "source": path.name,
                "text": part,
                "start_word": start,
            })

    output = Path(index_path).expanduser().resolve() if index_path else directory.parent / "index" / "chunks.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8")
    return chunks
