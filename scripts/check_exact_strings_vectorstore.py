from swasthya_setu.retrieval.vectorstore import load_index

vs = load_index()
coll = vs._collection
results = coll.get(include=['documents', 'metadatas'])
docs = results['documents']
metas = results['metadatas']
print(f'Total chunks in vectorstore: {len(docs)}')

target_strings = ['Newsroom', 'Select language', 'Emergencies', 'Disease Outbreak News', 'Member States', 'cookie']

for s in target_strings:
    matching = [(d, m) for d, m in zip(docs, metas) if s in d]
    print(f'String "{s}": {len(matching)} occurrences')
    for d, m in matching[:3]:
        print(f'   Source: {m.get("source")} | Text: {d[:100]}...')
