"""Print FAISS relevance distributions for threshold calibration."""

from collections.abc import Iterable
from pathlib import Path

from swasthya_setu.retrieval.vectorstore import load_index

IN_SCOPE_QUESTIONS = (
    "What are the warning signs of severe dengue?",
    "How is dengue treated at home?",
    "What are the common symptoms of malaria?",
    "How is tuberculosis treated, in simple words?",
    "Which vaccines are due at 9 months?",
    "डेंगू के गंभीर लक्षण क्या हैं?",
    "मलेरिया से बचाव के क्या उपाय हैं?",
)
OUT_OF_SCOPE_QUESTIONS = (
    "How do I fix a broken car engine?",
    "What is the capital of France?",
    "What are the latest stock market prices for Tesla?",
    "Can you write a poem about the moon and stars?",
    "What is the recipe for baking a chocolate cake?",
    "What is the airspeed velocity of an unladen swallow?",
    "कार का इंजन कैसे ठीक करें?",
)


def _scores(store, questions: Iterable[str]) -> list[float]:
    scores = []
    for question in questions:
        matches = store.similarity_search_with_relevance_scores(question, k=4)
        scores.extend(score for _, score in matches)
    return scores


def _summary(label: str, scores: list[float]) -> None:
    if not scores:
        print(f"{label}: no scores")
        return
    ordered = sorted(scores)
    print(
        f"{label}: count={len(ordered)} min={ordered[0]:.4f} "
        f"p25={ordered[len(ordered) // 4]:.4f} "
        f"median={ordered[len(ordered) // 2]:.4f} "
        f"max={ordered[-1]:.4f}"
    )


def main() -> None:
    store = load_index(Path("vectorstore"))
    in_scope = _scores(store, IN_SCOPE_QUESTIONS)
    out_of_scope = _scores(store, OUT_OF_SCOPE_QUESTIONS)
    _summary("in_scope", in_scope)
    _summary("out_of_scope", out_of_scope)
    print("Use the lowest in-scope score above the highest out-of-scope score as the candidate threshold.")


if __name__ == "__main__":
    main()
