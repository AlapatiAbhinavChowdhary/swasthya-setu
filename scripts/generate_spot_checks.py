from swasthya_setu.generation.agent import run_agent

queries = [
    "What are the symptoms of malaria?",
    "How is tuberculosis treated, in simple words?",
    "Which vaccines are due at 9 months?",
]

for q in queries:
    print(f"\n{'='*70}\nQUESTION: {q}\n{'='*70}")
    state = run_agent(q, session_id="spot-check-session", language="en")
    response = state.get("response", {})
    answer = response.get("answer", "")
    citations = state.get("citations", [])
    sources = response.get("sources", [])
    print(f"ANSWER:\n{answer}\n")
    print(f"CITATIONS: {citations}")
    print("SOURCES:")
    for s in sources:
        print(f"  - [{s.get('number', '?')}] {s.get('source')} (Page/Section: {s.get('page')})")
        if s.get("publisher"):
            print(f"    Publisher: {s.get('publisher')} | Year: {s.get('year')} | URL: {s.get('url')}")
        print(f"    Snippet: {s.get('snippet')[:120]}...")

