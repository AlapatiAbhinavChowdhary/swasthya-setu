import yaml
from collections import defaultdict
from swasthya_setu.coverage import get_coverage

cov = get_coverage()
diseases = cov.get("diseases", [])
print("=== COVERAGE SUMMARY ===")
print(f"Total target diseases: {len(diseases)}")
with_docs = [d for d in diseases if d["documents"] > 0]
print(f"Diseases with indexed documents: {len(with_docs)} / {len(diseases)}")

sources = yaml.safe_load(open("data/sources.yaml", encoding="utf-8"))["sources"]
disease_sources = defaultdict(list)
for s in sources:
    if s.get("coverage") == "disease-specific":
        for d in s.get("disease_ids", []):
            disease_sources[d].append(s["id"])

at_least_1 = [d for d, items in disease_sources.items() if len(items) >= 1]
at_least_3 = [d for d, items in disease_sources.items() if len(items) >= 3]
print(f"Diseases with at least 1 disease-specific source: {len(at_least_1)} / {len(diseases)}")
print(f"Diseases with 3+ disease-specific sources: {len(at_least_3)} ({len(at_least_3)} diseases: {at_least_3})")
print("\nDetails per disease:")
for d in diseases:
    ds_count = len(disease_sources.get(d["id"], []))
    print(f"  {d['id']:30}: {d['documents']:2d} docs ({ds_count} disease-specific), {d['chunks']:4d} chunks, status={d['status']}")
