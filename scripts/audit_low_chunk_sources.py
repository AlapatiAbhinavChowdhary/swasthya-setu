import json
import yaml
from pathlib import Path
import pypdf

ROOT = Path(__file__).resolve().parents[1]

manifest = json.loads((ROOT / "vectorstore" / "index-manifest.json").read_text(encoding="utf-8"))
chunks_by_source = manifest.get("chunks_by_source", {})

sources = yaml.safe_load((ROOT / "data" / "sources.yaml").read_text(encoding="utf-8")).get("sources", [])

print(f"{'Source ID':<35} | {'Pages':<6} | {'Total Chars':<12} | {'Chars/Page':<11} | {'Chunks':<7} | {'Type / Status'}")
print("-" * 105)

for s in sources:
    s_id = s.get("id", "")
    f_path = ROOT / s.get("file", "")
    chunks = chunks_by_source.get(s_id, 0)
    if not f_path.exists():
        continue
    
    pages = 1
    total_chars = 0
    is_diagram_or_image = "Text-based"
    
    if f_path.suffix.lower() == ".pdf":
        try:
            reader = pypdf.PdfReader(str(f_path))
            pages = len(reader.pages)
            for p in reader.pages:
                total_chars += len(p.extract_text() or "")
        except Exception:
            pages = 1
    elif f_path.suffix.lower() == ".html":
        raw = f_path.read_text(encoding="utf-8", errors="ignore")
        total_chars = len(raw)
        pages = 1
        
    chars_per_page = round(total_chars / max(pages, 1), 1)
    if chars_per_page < 300:
        is_diagram_or_image = "Image/Diagram-heavy or short STW"
    elif "guidelines" in s_id or "operational" in s_id:
        is_diagram_or_image = "Full text guideline"
    else:
        is_diagram_or_image = "Standard text fact sheet / STW"
        
    if chunks < 15 or any(k in s_id for k in ["diabetes", "influenza", "chikungunya", "typhoid", "hygiene"]):
        print(f"{s_id:<35} | {pages:<6} | {total_chars:<12} | {chars_per_page:<11} | {chunks:<7} | {is_diagram_or_image}")
