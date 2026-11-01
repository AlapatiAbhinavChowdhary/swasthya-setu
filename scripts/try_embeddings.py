import numpy as np

from swasthya_setu.retrieval.embedder import get_embeddings

emb = get_embeddings()

# E5 models expect these prefixes: "passage: " for documents, "query: " for questions
passages = [
    "passage: Dengue is spread by Aedes mosquitoes and causes high fever, headache and joint pain.",
    "passage: Children should receive the measles vaccine at 9 months of age.",
    "passage: Wash your hands with soap to prevent diarrhoea.",
]
queries = [
    "query: What are the symptoms of dengue?",
    "query: डेंगू के लक्षण क्या हैं?",
    "query: When should my baby get the measles shot?",
]

p_vecs = np.array(emb.embed_documents(passages))
q_vecs = np.array(emb.embed_documents(queries))

print("Vector shape (texts, dimensions):", p_vecs.shape)
print("First 5 numbers of one vector:", p_vecs[0][:5])

scores = q_vecs @ p_vecs.T  # cosine similarity matrix
for q, row in zip(queries, scores):
    best = int(row.argmax())
    print(f"\n{q}")
    print("  scores:", np.round(row, 3))
    print("  best match ->", passages[best][:60])