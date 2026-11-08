"""Offline retrieval evaluation: Chroma dense, disease filtering, and hybrid BM25+RRF."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from langchain_core.documents import Document
from swasthya_setu.retrieval.vectorstore import load_index

ROOT = Path(__file__).resolve().parents[1]


def _get_all_docs(store) -> list[Document]:
    data = store._collection.get(include=["documents", "metadatas"])
    return [
        Document(page_content=text, metadata=metadata or {})
        for text, metadata in zip(data["documents"], data["metadatas"])
    ]


def _lexical(query: str, docs: list[Document], k: int = 8) -> list[Document]:
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


def _retrieve_chroma(
    store,
    docs: list[Document],
    query: str,
    disease: str,
    filtered: bool,
    hybrid: bool,
    k: int = 4,
) -> list[Document]:
    # Dense retrieval
    if filtered:
        # Retrieve candidate pool from Chroma and filter by disease
        dense_candidates = store.similarity_search(query, k=20)
        filtered_dense = [
            doc for doc in dense_candidates
            if disease in doc.metadata.get("disease_ids", "").split(",")
        ]
        dense = filtered_dense[:k] if filtered_dense else dense_candidates[:k]
    else:
        dense = store.similarity_search(query, k=k)

    if not hybrid:
        return _unique(dense)

    # Hybrid BM25 + RRF
    lexical = _lexical(query, docs, k=k * 2)
    if filtered:
        lexical = [
            doc for doc in lexical
            if disease in doc.metadata.get("disease_ids", "").split(",")
        ] or lexical

    ranked = defaultdict(float)
    for rank, doc in enumerate(dense, start=1):
        ranked[doc.page_content] += 1.0 / (60.0 + rank)
    for rank, doc in enumerate(lexical, start=1):
        ranked[doc.page_content] += 1.0 / (60.0 + rank)

    by_text = {doc.page_content: doc for doc in docs}
    sorted_texts = sorted(ranked.items(), key=lambda item: item[1], reverse=True)[:k]
    return [by_text[text] for text, _ in sorted_texts if text in by_text]


def main() -> None:
    questions_path = ROOT / "eval" / "questions.jsonl"
    rows = [json.loads(line) for line in questions_path.read_text(encoding="utf-8").splitlines()]

    chroma = load_index()
    docs = _get_all_docs(chroma)
    print(f"Loaded index with {len(docs)} documents.")

    configs = [
        ("Chroma Dense (Unfiltered)", False, False),
        ("Chroma Dense (Filtered)", True, False),
        ("Chroma Hybrid BM25+RRF (Unfiltered)", False, True),
        ("Chroma Hybrid BM25+RRF (Filtered)", True, True),
    ]

    results = []
    for name, filtered, hybrid in configs:
        hits = 0
        by_disease = defaultdict(lambda: [0, 0])
        for row in rows:
            disease = row.get("disease")
            if not disease:
                continue
            retrieved = _retrieve_chroma(
                chroma, docs, row["question"], disease, filtered, hybrid, k=4
            )
            hit = any(disease in doc.metadata.get("disease_ids", "").split(",") for doc in retrieved)
            hits += int(hit)
            by_disease[disease][0] += int(hit)
            by_disease[disease][1] += 1

        total = sum(v[1] for v in by_disease.values())
        hit_rate = hits / total if total else 0
        results.append((name, filtered, hybrid, hits, total, hit_rate, by_disease))

    # Print summary
    print("\n" + "=" * 80)
    print("RETRIEVAL EVALUATION (COVERED QUESTIONS)")
    print("=" * 80)
    lines = [
        "# Retrieval-only evaluation",
        "",
        "| Configuration | Disease filter | Hybrid BM25+RRF | Hit-rate@4 | Overall Accuracy |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, filtered, hybrid, hits, total, hit_rate, _ in results:
        lines.append(
            f"| {name} | {str(filtered).lower()} | {str(hybrid).lower()} | {hits}/{total} | {hit_rate:.1%} |"
        )

    lines.append("\n### Hit-rate@4 per disease (Chroma Hybrid Filtered):\n")
    best_by_disease = results[-1][6]
    lines.append("| Disease | Hits / Questions | Hit-rate@4 |")
    lines.append("|---|---:|---:|")
    for disease, (h, t) in sorted(best_by_disease.items()):
        rate = h / t if t else 0
        lines.append(f"| {disease} | {h}/{t} | {rate:.1%} |")

    report_content = "\n".join(lines) + "\n"
    (ROOT / "docs" / "RETRIEVAL_EVALUATION.md").write_text(report_content, encoding="utf-8")
    print(report_content)


if __name__ == "__main__":
    main()
