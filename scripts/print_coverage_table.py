from swasthya_setu.coverage import get_coverage

cov = get_coverage()
print(f"Total diseases: {len(cov['diseases'])}")
print("-" * 90)
print(f"{'Disease ID':32} | Docs (Spec) | Chunks | Depth | Year | Has General")
print("-" * 90)
for d in cov["diseases"]:
    docs_str = f"{d['documents']} ({d['specific_documents']})"
    print(f"{d['id']:32} | {docs_str:11} | {d['chunks']:6} | {d['depth']:5} | {str(d['newest_source_year']):4} | {d['has_general_source']}")

