import sys

from swasthya_setu.retrieval.vectorstore import load_index

query = " ".join(sys.argv[1:])
store = load_index()

for doc, score in store.similarity_search_with_score(query, k=3):
    page = doc.metadata.get("page_label")
    src = doc.metadata.get("source")
    print(f"\n[distance={score:.3f}] {src} (page {page})")
    print(doc.page_content[:400])