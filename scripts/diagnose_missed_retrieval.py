import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swasthya_setu.retrieval.vectorstore import load_index
from scripts.evaluate_retrieval import _get_all_docs, _retrieve_chroma

def diagnose():
    store = load_index()
    docs = _get_all_docs(store)
    questions = [
        json.loads(line)
        for line in Path("eval/questions.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    missed = []
    for q in questions:
        disease = q["disease"]
        query = q["question"]
        retrieved = _retrieve_chroma(store, docs, query, disease, filtered=True, hybrid=True, k=4)
        hit = any(disease in d.metadata.get("disease_ids", []) for d in retrieved)
        if not hit:
            missed.append((q, retrieved))

    print(f"Total Missed: {len(missed)}")
    for q, ret in missed:
        print("\n" + "=" * 80)
        print(f"DISEASE: {q['disease']} | LANG: {q.get('lang', 'en')} | QUERY: \"{q['question']}\"")
        print("RETRIEVED CHUNKS:")
        for idx, doc in enumerate(ret):
            print(f"  [{idx+1}] Source: {doc.metadata.get('source')} | Diseases: {doc.metadata.get('disease_ids')}")
            print(f"      Snippet: {repr(doc.page_content.strip()[:150])}")

if __name__ == "__main__":
    diagnose()
