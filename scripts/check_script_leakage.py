import sqlite3
from pathlib import Path

db_path = Path("vectorstore/chroma/chroma.sqlite3")
if not db_path.exists():
    print("chroma.sqlite3 not found!")
    exit(1)

conn = sqlite3.connect(str(db_path))

# Check table structure
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"Tables found: {tables}")

# In Chroma SQLite, document text is usually in embedding_metadata, embedding_fulltext_search, or embeddings
# Let's inspect rows from tables with document text
search_terms = [
    "googletagmanager",
    "gtm.js",
    "dataLayer",
    "deleteCookie",
    "TrackingConsentManager",
    "function(",
    "window.",
    "<script",
]

# Find the column holding chunk document text
doc_column = None
doc_table = None

for table in tables:
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if "document" in cols:
        doc_column = "document"
        doc_table = table
        break
    elif "string_value" in cols:
        # Check if it holds chunk text
        pass

if not doc_table:
    # Try embeddings table
    if "embedding_fulltext_search" in tables:
        doc_table = "embedding_fulltext_search"
        doc_column = "string_value"
    elif "embeddings" in tables:
        doc_table = "embeddings"
        doc_column = "document"

print(f"Using table: {doc_table}, column: {doc_column}")

# Get all chunk texts
rows = conn.execute(f"SELECT {doc_column} FROM {doc_table} WHERE {doc_column} IS NOT NULL").fetchall()
all_chunks = [r[0] for r in rows if r[0]]
print(f"Total chunks retrieved: {len(all_chunks)}")

print("\n--- Leakage Counts Across All Indexed Chunks ---")
leakage_found = False
for term in search_terms:
    count = sum(1 for chunk in all_chunks if term.lower() in chunk.lower())
    exact_count = sum(1 for chunk in all_chunks if term in chunk)
    print(f"'{term}': exact={exact_count}, case_insensitive={count}")
    if exact_count > 0:
        leakage_found = True

if leakage_found:
    print("\nLEAKAGE DETECTED! Printing sample chunks:")
    for term in search_terms:
        matches = [c for c in all_chunks if term in c]
        if matches:
            print(f"\n--- Matches for '{term}' (showing first match, 300 chars) ---")
            print(matches[0][:300])
else:
    print("\nAll leak counts are 0.")
