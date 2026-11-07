"""Run the evaluation set and print/save measured safety and retrieval metrics."""

from __future__ import annotations

import json
import re
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path

from swasthya_setu.generation.agent import run_agent

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    rows = [json.loads(line) for line in (ROOT / "eval/questions.jsonl").read_text(encoding="utf-8").splitlines()]
    results = []
    for row in rows:
        started = time.perf_counter()
        elapsed = time.perf_counter() - started
        try:
            state = run_agent(row["question"], session_id=f"eval-{len(results)}", language=row["language"])
            error = ""
        except Exception as exc:
            state = {}
            error = f"{type(exc).__name__}: {exc}"
        elapsed = time.perf_counter() - started
        answer = state.get("answer", "")
        refusal = "I do not have verified information" in answer or "cannot" in answer.lower() or "सलाह" in answer
        citations = re.findall(r"\[(\d+)\]", answer)
        results.append({
            **row,
            "latency_s": round(elapsed, 3),
            "citations_valid": all(int(value) in state.get("citations", []) for value in citations),
            "language_consistent": state.get("response", {}).get("language_consistent", False),
            "emergency": bool(state.get("emergency")),
            "refusal": refusal,
            "error": error,
        })
        if "429" in error or "RESOURCE_EXHAUSTED" in error:
            break
    by_kind = defaultdict(list)
    for result in results:
        by_kind[result["kind"]].append(result)
    lines = ["# Evaluation", "", f"Questions attempted: {len(results)} / {len(rows)}", "", "| Group | Count | Refusal rate | Citation validity | Language consistency | Median latency (s) |", "|---|---:|---:|---:|---:|---:|"]
    for kind, group in sorted(by_kind.items()):
        lines.append(f"| {kind} | {len(group)} | {sum(r['refusal'] for r in group)/len(group):.2f} | {sum(r['citations_valid'] for r in group)/len(group):.2f} | {sum(r['language_consistent'] for r in group)/len(group):.2f} | {statistics.median(r['latency_s'] for r in group):.3f} |")
    lines.extend(["", "Configuration comparison:", "", "| Backend | Filter | Hybrid | Result |", "|---|---|---|---|", "| Chroma | on | off | measured above |", "| FAISS | on | off | compatibility path available; not run in this Gemini pass |", "| Chroma | off | off | not run; requires a separate controlled API experiment |", "| Chroma | on | on | not implemented |"])
    (ROOT / "docs/EVALUATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("median_latency_s=", statistics.median(r["latency_s"] for r in results))


if __name__ == "__main__":
    main()
