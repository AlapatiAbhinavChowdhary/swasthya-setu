from swasthya_setu.generation.chain import _store
from swasthya_setu.generation.disease_filter import detect_asked_diseases, filter_cross_disease_documents
from swasthya_setu.config import get_settings

settings = get_settings()
store = _store()

queries = [
    ("What is the first aid for snakebite?", "en"),
    ("साँप के काटने पर प्राथमिक उपचार क्या है?", "hi"),
]

for q, lang in queries:
    print(f"\n========================================================")
    print(f"QUERY ({lang}): {q}")
    print(f"========================================================")
    
    matches = store.similarity_search_with_relevance_scores(q, k=15)
    asked = detect_asked_diseases(q)
    print(f"Asked diseases: {asked}")
    if asked:
        matches = filter_cross_disease_documents(matches, asked)
    
    # deduplicate chunks as in agent.py
    seen = set()
    unique = []
    import hashlib
    for doc, rel in matches:
        digest = hashlib.sha256(doc.page_content.strip().encode("utf-8")).hexdigest()
        if digest not in seen:
            seen.add(digest)
            unique.append((doc, rel))
            
    print(f"Unique matching documents count: {len(unique)}")
    for idx, (doc, rel) in enumerate(unique[:8], start=1):
        print(f"\n--- [Chunk {idx}] (Relevance Score: {rel:.4f}) ---")
        print(f"Metadata:")
        for k, v in doc.metadata.items():
            print(f"  {k}: {v}")
        print(f"Exact Stored Content ({len(doc.page_content)} chars):")
        print(doc.page_content)
        print("-" * 50)
