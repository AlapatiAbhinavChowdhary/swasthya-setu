import time
import statistics
from swasthya_setu.generation.agent import run_agent

QUESTIONS = [
    ("What are the symptoms of malaria?", "en"),
    ("What are the symptoms of dengue?", "en"),
    ("How does cholera spread?", "en"),
    ("What is the first aid for snakebite?", "en"),
    ("Can I take paracetamol for dengue?", "en"),
    ("What medicine should I take for malaria?", "en"),  # Refusal / out of scope
    ("Are there any dengue alerts in Delhi?", "en"),     # Outbreak advisory tool
    ("Find hospitals in Delhi", "en"),                   # Facility locator tool
    ("डेंगू के लक्षण क्या हैं?", "hi"),
    ("मेरे बच्चे को सांस लेने में दिक्कत है", "hi"),       # Emergency triage (deterministic)
]

def run_bench():
    latencies = []
    deterministic_triage = 0
    results = []

    print("=" * 80)
    print("10-QUESTION LATENCY & ROUTING BENCHMARK")
    print("=" * 80)

    for idx, (query, lang) in enumerate(QUESTIONS, start=1):
        for attempt in range(4):
            try:
                t0 = time.time()
                state = run_agent(query, session_id=f"bench-{idx}", language=lang)
                elapsed = time.time() - t0
                break
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    print(f"  [Q{idx}] Rate-limited (429), pausing 50s before retry...")
                    time.sleep(50)
                else:
                    print(f"  [Q{idx}] Error {e}, retrying in 5s...")
                    time.sleep(5)
        else:
            print(f"  [Q{idx}] Failed after 4 attempts.")
            continue

        resp = state.get("response", {})
        intent = resp.get("intent", "unknown")
        emergency = resp.get("emergency", False)
        if emergency:
            deterministic_triage += 1

        latencies.append(elapsed)
        results.append({
            "idx": idx,
            "query": query,
            "lang": lang,
            "intent": intent,
            "emergency": emergency,
            "latency": elapsed,
        })
        print(f"[{idx:2d}/10] Latency: {elapsed:5.2f}s | Intent: {intent:<16} | Emergency: {str(emergency):<5} | Query: {query}")
        # Throttle between calls to respect Gemini Free Tier 15 RPM
        time.sleep(6.0)

    if latencies:
        sorted_lat = sorted(latencies)
        p90_idx = int(len(sorted_lat) * 0.9)
        p90 = sorted_lat[min(p90_idx, len(sorted_lat) - 1)]
        med = statistics.median(latencies)
        avg = statistics.mean(latencies)
        det_share = (deterministic_triage / len(latencies)) * 100.0

        print("\n" + "=" * 80)
        print("SUMMARY BENCHMARK METRICS")
        print("=" * 80)
        print(f"Total Questions Evaluated: {len(latencies)}")
        print(f"Median Latency:           {med:.2f}s")
        print(f"Mean Latency:             {avg:.2f}s")
        print(f"P90 Latency:              {p90:.2f}s")
        print(f"Min Latency:              {min(latencies):.2f}s")
        print(f"Max Latency:              {max(latencies):.2f}s")
        print(f"Deterministic Triage:     {deterministic_triage}/{len(latencies)} ({det_share:.1f}%)")

if __name__ == "__main__":
    run_bench()
