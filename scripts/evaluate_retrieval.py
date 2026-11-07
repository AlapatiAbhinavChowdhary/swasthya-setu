"""Offline retrieval comparison: Chroma/FAISS, disease filtering, and BM25-RRF."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from swasthya_setu.retrieval.vectorstore import load_index
from swasthya_setu.retrieval.embedder import get_embeddings

ROOT = Path(__file__).resolve().parents[1]


def _docs(store) -> list[Document]:
    data = store._collection.get(include=["documents", "metadatas"])
    return [Document(page_content=text, metadata=metadata or {}) for text, metadata in zip(data["documents"], data["metadatas"])]


def _lexical(query: str, docs: list[Document], k: int = 4) -> list[Document]:
    terms = set(re.findall(r"\w+", query.lower()))
    scored = []
    for doc in docs:
        words = re.findall(r"\w+", doc.page_content.lower())
        score = sum(words.count(term) for term in terms)
        if score:
            scored.append((score, doc))
    return [doc for _, doc in sorted(scored, key=lambda item: item[0], reverse=True)[:k]]


def _unique(docs: list[Document]) -> list[Document]:
    seen = set()
    result = []
    for doc in docs:
        key = doc.page_content.strip()
        if key in seen:
            continue
        seen.add(key)
        result.append(doc)
    return result


def _retrieve(store, docs, query, disease, filtered, hybrid, filtered_stores, embeddings):
    if filtered:
        candidates = [doc for doc in docs if disease in doc.metadata.get("disease_ids", "").split(",")]
        if candidates:
            if disease not in filtered_stores:
                filtered_stores[disease] = FAISS.from_documents(candidates, embeddings)
            filtered_store = filtered_stores[disease]
            dense = filtered_store.similarity_search(query, k=4)
        else:
            dense = []
    else:
        dense = store.similarity_search(query, k=4)
    if filtered and not dense:
        dense = store.similarity_search(query, k=4)
    if not hybrid:
        return _unique(dense)
    lexical = _lexical(query, docs, k=8)
    ranked = defaultdict(float)
    for rank, doc in enumerate(dense, start=1):
        ranked[doc.page_content] += 1 / (60 + rank)
    for rank, doc in enumerate(lexical, start=1):
        ranked[doc.page_content] += 1 / (60 + rank)
    by_text = {doc.page_content: doc for doc in docs}
    return [by_text[text] for text, _ in sorted(ranked.items(), key=lambda item: item[1], reverse=True)[:4]]


def main() -> None:
    rows = [json.loads(line) for line in (ROOT / "eval/questions.jsonl").read_text(encoding="utf-8").splitlines()]
    embeddings = get_embeddings()
    chroma = load_index()
    docs = _docs(chroma)
    faiss = FAISS.from_documents(docs, embeddings)
    configs = [
        ("Chroma", False, False, chroma),
        ("Chroma", True, False, chroma),
        ("Chroma", False, True, chroma),
        ("Chroma", True, True, chroma),
        ("FAISS", False, False, faiss),
        ("FAISS", True, False, faiss),
    ]
    results = []
    for backend, filtered, hybrid, store in configs:
        filtered_stores = {}
        hits = 0
        by_disease = defaultdict(lambda: [0, 0])
        for row in rows:
            disease = row["disease"]
            if not disease:
                continue
            retrieved = _retrieve(
                store, docs, row["question"], disease, filtered, hybrid, filtered_stores, embeddings
            )
            hit = any(disease in doc.metadata.get("disease_ids", "").split(",") for doc in retrieved)
            hits += hit
            by_disease[disease][0] += hit
            by_disease[disease][1] += 1
        results.append((backend, filtered, hybrid, hits, sum(v[1] for v in by_disease.values()), by_disease))
    lines = ["# Retrieval-only evaluation", "", "| Backend | Disease filter | Hybrid BM25+RRF | Hit-rate@4 |", "|---|---:|---:|---:|"]
    for backend, filtered, hybrid, hits, total, _ in results:
        lines.append(f"| {backend} | {str(filtered).lower()} | {str(hybrid).lower()} | {hits / total:.3f} ({hits}/{total}) |")
    (ROOT / "docs/RETRIEVAL_EVALUATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    for backend, filtered, hybrid, _, _, by_disease in results:
        print(backend, "filter=", filtered, "hybrid=", hybrid, "per_disease=", dict(by_disease))


if __name__ == "__main__":
    main()
