import sys

from swasthya_setu.generation.chain import answer

question = " ".join(sys.argv[1:])
text, docs = answer(question)

print("\n=== ANSWER ===")
print(text)
print("\n=== SOURCES ===")
for i, d in enumerate(docs, start=1):
    print(f"[{i}] {d.metadata.get('source')} (page {d.metadata.get('page_label')})")