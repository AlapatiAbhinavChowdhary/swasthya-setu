"""Verification script for RAW answers and snakebite chunk verification.

Queries:
1. ORS for a child with diarrhoea
2. Heat stroke warning signs
3. Snakebite first aid
"""
import json
import os
import sys
import time

from swasthya_setu.generation.agent import run_agent

QUERIES = [
    {
        "topic": "ORS for a child with diarrhoea",
        "question": "How to prepare and give ORS for a child with diarrhoea?",
    },
    {
        "topic": "Heat stroke warning signs",
        "question": "What are the warning signs of heat stroke?",
    },
    {
        "topic": "Snakebite first aid",
        "question": "What is the first aid for snakebite?",
    },
]

def main():
    for item in QUERIES:
        topic = item["topic"]
        q = item["question"]
        print("=" * 80)
        print(f"TOPIC: {topic}")
        print(f"QUESTION: {q}")
        print("-" * 80)
        
        state = run_agent(q)
        ans = state.get("answer", "")
        citation_indices = state.get("citations", [])
        sources = state.get("sources", [])
        docs = state.get("documents", [])

        print("RAW ANSWER:")
        print(ans)
        print("-" * 80)
        print(f"CITED SOURCE NUMBERS: {citation_indices}")
        print("SOURCES METADATA:")
        for s in sources:
            print(f"  [{s.get('number')}] Source: {s.get('source')} | Page: {s.get('page')} | Year: {s.get('year')} | URL: {s.get('url')}")
        
        if topic == "Snakebite first aid":
            print("=" * 80)
            print("SNAKEBITE CITED CHUNKS FULL TEXT:")
            for s in sources:
                c_num = s.get("number")
                if 1 <= c_num <= len(docs):
                    doc = docs[c_num - 1]
                    meta = getattr(doc, "metadata", {}) or {}
                    content = getattr(doc, "page_content", "") or ""
                    print(f"\n--- CITED CHUNK [{c_num}] ---")
                    print(f"Source: {meta.get('source', '')} | Page: {meta.get('page', '')} / {meta.get('page_label', '')} | Section: {meta.get('section', '')}")
                    print(f"Content:\n{content}")
            print("=" * 80)

        # Respect Gemini free-tier rate limits
        time.sleep(4.5)

if __name__ == "__main__":
    main()
