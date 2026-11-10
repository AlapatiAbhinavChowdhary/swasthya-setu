import json
import yaml
from pathlib import Path

sources_yaml_path = Path("data/sources.yaml")
lock_json_path = Path("data/sources.lock.json")

data = yaml.safe_load(sources_yaml_path.read_text(encoding="utf-8"))
existing_ids = {s["id"] for s in data["sources"]}

new_entries = [
    {
        "id": "doc-heat-naphri-ncdc",
        "title": "National Action Plan on Heat-Related Illnesses",
        "publisher": "National Centre for Disease Control (NCDC), Ministry of Health and Family Welfare, Government of India",
        "url": "https://ncdc.mohfw.gov.in/uploads/pdf/heat12.pdf",
        "file": "data/raw/heat-illness/ncdc-national-action-plan-heat-illness.pdf",
        "disease_ids": ["heat-illness"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2021,
        "doc_id": "7ac5dd1421d41d050ca8743e8eebfbed859658897cb5b6c9235a1ef108b47b50",
        "status": "downloaded",
    },
    {
        "id": "doc-heat-guidelines-ndma",
        "title": "National Guidelines for Preparation of Action Plan - Prevention and Management of Heat Wave",
        "publisher": "National Disaster Management Authority (NDMA), Government of India",
        "url": "https://ndma.gov.in/sites/default/files/PDF/Heat-Wave.pdf",
        "file": "data/raw/heat-illness/ndma-heat-wave-guidelines.pdf",
        "disease_ids": ["heat-illness"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2019,
        "doc_id": "a4138fd9d5e7925f8a874742e823d62b482d67464fd6e7190b5306baa9bb2aa6",
        "status": "downloaded",
    },
    {
        "id": "doc-snakebite-guidelines-who-sear",
        "title": "Guidelines for the Management of Snakebites in the South-East Asia Region",
        "publisher": "World Health Organization Regional Office for South-East Asia",
        "url": "https://iris.who.int/handle/10665/249547",
        "file": "data/raw/snakebite/who-guidelines-management-snakebites-sear.pdf",
        "disease_ids": ["snakebite"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2016,
        "doc_id": "6743bfcbf6ed27612bf2e81b1e7829b3755e0b3af6bdcc17c34827f557b14373",
        "status": "downloaded",
    },
    {
        "id": "doc-diarrhoea-treatment-manual-who",
        "title": "The Treatment of Diarrhoea: A manual for physicians and other senior health workers",
        "publisher": "World Health Organization",
        "url": "https://iris.who.int/handle/10665/43209",
        "file": "data/raw/diarrhoeal-disease/who-treatment-of-diarrhoea-manual.pdf",
        "disease_ids": ["diarrhoeal-disease"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2005,
        "doc_id": "433c62fbdbe2a33c95f9b813de62675ca610e185e97f679875266bb1a5f87b3b",
        "status": "downloaded",
    },
]

added = 0
for entry in new_entries:
    if entry["id"] not in existing_ids:
        data["sources"].append(entry)
        added += 1

sources_yaml_path.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
print(f"Added {added} sources to data/sources.yaml. Total sources: {len(data['sources'])}")

# Update lockfile
lock_data = json.loads(lock_json_path.read_text(encoding="utf-8"))
existing_hashes = {x.get("hash") for x in lock_data}
lock_added = 0
for entry in new_entries:
    if entry["doc_id"] not in existing_hashes:
        p = Path(entry["file"])
        lock_data.append({
            "url": entry["url"],
            "file": str(p).replace("/", "\\"),
            "date": "2026-11-10",
            "status": "downloaded",
            "hash": entry["doc_id"],
            "bytes": p.stat().st_size,
            "fallback": "urllib/requests (verified official)",
        })
        lock_added += 1

lock_json_path.write_text(json.dumps(lock_data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Added {lock_added} entries to data/sources.lock.json. Total lock entries: {len(lock_data)}")

