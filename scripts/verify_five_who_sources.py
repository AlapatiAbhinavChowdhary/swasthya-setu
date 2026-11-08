import json
from pathlib import Path
from swasthya_setu.ingestion.html_loader import extract_html_text

manifest = json.loads(Path("vectorstore/index-manifest.json").read_text(encoding="utf-8"))
chunks_by_source = manifest.get("chunks_by_source", {})

targets = [
    ("diabetes", "doc-who-factsheet-diabetes", "data/raw/diabetes/who-diabetes.html"),
    ("cholera", "doc-who-factsheet-cholera", "data/raw/cholera/who-cholera.html"),
    ("hepatitis-a", "doc-who-factsheet-hepatitis-a", "data/raw/hepatitis-a/who-hepatitis-a.html"),
    ("tetanus", "doc-who-factsheet-tetanus", "data/raw/diphtheria-pertussis-tetanus/who-tetanus.html"),
    ("diarrhoeal-disease", "doc-who-factsheet-diarrhoeal-disease", "data/raw/diarrhoeal-disease/who-diarrhoeal-disease.html"),
]

for name, sid, file_path in targets:
    p = Path(file_path)
    title, text = extract_html_text(p.read_text(encoding="utf-8"))
    chunk_count = chunks_by_source.get(sid, 0)
    print(f"=== {name.upper()} ({sid}) ===")
    print(f"File: {file_path}")
    print(f"Chunk count: {chunk_count}")
    print(f"First 600 characters:\n{text[:600]}")
    print("=" * 60 + "\n")
