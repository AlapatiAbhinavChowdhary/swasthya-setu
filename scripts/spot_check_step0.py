import time
from swasthya_setu.generation.agent import run_agent

print("=" * 80)
print("1. TUBERCULOSIS TREATMENT ANSWER (EN)")
print("=" * 80)
for attempt in range(3):
    try:
        tb_state = run_agent("How is tuberculosis treated, in simple words?", session_id="step0-tb-fixed", language="en")
        break
    except Exception as e:
        print(f"Attempt {attempt+1} failed with {e}, waiting 55s...")
        time.sleep(55)

tb_resp = tb_state.get("response", {})
print("\n--- FULL ANSWER ---")
print(tb_resp.get("answer"))
print("\n--- CITATIONS ---")
print(tb_state.get("citations"))
print("\n--- SOURCES ---")
for s in tb_resp.get("sources", []):
    print(f"  [{s.get('number')}] {s.get('source')} (Section/Page: {s.get('page')})")

print("\n--- RETRIEVED CHUNK TEXT FOR TB CITATIONS ---")
for i, doc in enumerate(tb_state.get("documents", [])):
    print(f"\n[Chunk {i+1}] Source: {doc.metadata.get('source')} | Page: {doc.metadata.get('page_label')}")
    print(doc.page_content.strip()[:600])

print("\nWaiting 20 seconds before next query to respect API quota...")
time.sleep(20)

print("\n" + "=" * 80)
print("2. MALARIA SYMPTOMS ANSWER (EN)")
print("=" * 80)
for attempt in range(3):
    try:
        mal_state = run_agent("What are the symptoms of malaria?", session_id="step0-mal-fixed", language="en")
        break
    except Exception as e:
        print(f"Attempt {attempt+1} failed with {e}, waiting 55s...")
        time.sleep(55)

mal_resp = mal_state.get("response", {})
print("\n--- FULL ANSWER ---")
print(mal_resp.get("answer"))
print("\n--- CITATIONS ---")
print(mal_state.get("citations"))
print("\n--- SOURCES ---")
for s in mal_resp.get("sources", []):
    print(f"  [{s.get('number')}] {s.get('source')} (Section/Page: {s.get('page')})")

print("\nDONE.")
