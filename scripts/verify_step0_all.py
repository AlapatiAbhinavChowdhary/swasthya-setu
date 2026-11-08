import time
from swasthya_setu.generation.agent import run_agent

print("=" * 80)
print("1. TUBERCULOSIS TREATMENT ANSWER (EN)")
print("=" * 80)
t0 = time.time()
tb_state = run_agent("How is tuberculosis treated, in simple words?", session_id="step0-tb", language="en")
tb_dur = time.time() - t0
tb_resp = tb_state.get("response", {})
print("ANSWER:\n", tb_resp.get("answer"))
print("\nCITATIONS:", tb_state.get("citations"))
print("\nSOURCES:")
for s in tb_resp.get("sources", []):
    print(f"  [{s.get('number')}] {s.get('source')} (Section/Page: {s.get('page')})")

print("\nRETRIEVED CHUNK TEXT FOR TB CITATIONS:")
for doc in tb_state.get("documents", []):
    print("-" * 60)
    print("SOURCE:", doc.metadata.get("source"), "| Page:", doc.metadata.get("page_label"))
    print("CONTENT:\n", doc.page_content.strip()[:600])

time.sleep(1.0)

print("\n" + "=" * 80)
print("2. MALARIA SYMPTOMS ANSWER (EN)")
print("=" * 80)
mal_state = run_agent("What are the symptoms of malaria?", session_id="step0-mal", language="en")
mal_resp = mal_state.get("response", {})
print("ANSWER:\n", mal_resp.get("answer"))
print("\nCITATIONS:", mal_state.get("citations"))
print("\nSOURCES:")
for s in mal_resp.get("sources", []):
    print(f"  [{s.get('number')}] {s.get('source')} (Section/Page: {s.get('page')})")

time.sleep(1.0)

print("\n" + "=" * 80)
print("3. VACCINATION AT 9 MONTHS (EN & HI)")
print("=" * 80)
vax_en = run_agent("Which vaccines are due at 9 months under the National Immunization Schedule?", session_id="step0-vax-en", language="en")
print("ENGLISH ANSWER:\n", vax_en.get("response", {}).get("answer"))

time.sleep(1.0)
vax_hi = run_agent("9 महीने के बच्चे को कौन से टीके लगते हैं?", session_id="step0-vax-hi", language="hi")
print("\nHINDI ANSWER:\n", vax_hi.get("response", {}).get("answer"))

print("\n" + "=" * 80)
print("4. LATENCY & CALLS BENCHMARK (10 REPRESENTATIVE QUESTIONS)")
print("=" * 80)
test_questions = [
    ("What are the symptoms of dengue?", "en"),
    ("How does cholera spread?", "en"),
    ("What is the first aid for snakebite?", "en"),
    ("Can I take paracetamol for dengue?", "en"),
    ("What medicine should I take for malaria?", "en"), # Out of scope
    ("Are there any dengue alerts in Delhi?", "en"),    # Outbreak tool
    ("Find hospitals in Delhi", "en"),                  # Facility tool
    ("डेंगू के लक्षण क्या हैं?", "hi"),
    ("दस्त होने पर ओआरएस कैसे बनाएं?", "hi"),
    ("मेरे बच्चे को सांस लेने में दिक्कत है", "hi"),       # Emergency
]

latencies = []
for q, lang in test_questions:
    t_start = time.time()
    res = run_agent(q, session_id="bench", language=lang)
    elapsed = time.time() - t_start
    latencies.append(elapsed)
    intent = res.get("response", {}).get("intent")
    emergency = res.get("response", {}).get("emergency")
    print(f"Query: {q:<45} | Intent: {intent:<16} | Emerg: {str(emergency):<5} | Latency: {elapsed:.2f}s", flush=True)
    time.sleep(1.0)

import statistics
print(f"\nLatency: min={min(latencies):.2f}s  median={statistics.median(latencies):.2f}s  max={max(latencies):.2f}s")

