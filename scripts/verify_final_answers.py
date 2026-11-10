"""Verification script for:
1. Raw English ORS answer
2. Raw English Heat stroke answer
3. Raw English Snakebite answer with sentence-by-sentence supporting chunk text
4. Raw Hindi Snakebite answer to 'साँप के काटने पर प्राथमिक उपचार क्या है?'
"""
import json
import time
from swasthya_setu.generation.agent import run_agent

TARGETS = [
    {
        "id": "ors",
        "topic": "ORS for a child with diarrhoea",
        "question": "How to prepare and give ORS for a child with diarrhoea?",
        "lang": "en",
    },
    {
        "id": "heat_stroke",
        "topic": "Heat stroke warning signs",
        "question": "What are the warning signs of heat stroke?",
        "lang": "en",
    },
    {
        "id": "snakebite_en",
        "topic": "Snakebite first aid (English)",
        "question": "What is the first aid for snakebite?",
        "lang": "en",
    },
    {
        "id": "snakebite_hi",
        "topic": "Snakebite first aid (Hindi)",
        "question": "साँप के काटने पर प्राथमिक उपचार क्या है?",
        "lang": "hi",
    },
]

def main():
    results = {}
    for item in TARGETS:
        topic = item["topic"]
        q = item["question"]
        lang = item.get("lang", "en")
        print("=" * 80)
        print(f"TOPIC: {topic}")
        print(f"QUESTION: {q}")
        print("-" * 80)

        state = run_agent(q, language=lang)
        ans = state.get("answer", "")
        sources = state.get("sources", [])
        docs = state.get("documents", [])
        results[item["id"]] = {"answer": ans, "sources": sources, "docs": docs}

        print("RAW ANSWER:")
        print(ans)
        print("-" * 80)
        print(f"SOURCES ({len(sources)}):")
        for s in sources:
            print(f"  [{s.get('number')}] {s.get('source')} (p. {s.get('page')}) -> {s.get('url')}")

        if item["id"] == "snakebite_en":
            print("=" * 80)
            print("SNAKEBITE ENGLISH CITED CHUNKS FULL TEXT:")
            for s in sources:
                c_num = s.get("number")
                if 1 <= c_num <= len(docs):
                    doc = docs[c_num - 1]
                    meta = getattr(doc, "metadata", {}) or {}
                    content = getattr(doc, "page_content", "") or ""
                    print(f"\n--- CITED CHUNK [{c_num}] ---")
                    print(f"Source: {meta.get('source', '')} | Page: {meta.get('page', '')} / {meta.get('page_label', '')}")
                    print(f"Content:\n{content}")
            print("=" * 80)

        time.sleep(4.5)

if __name__ == "__main__":
    main()
