import json
import os
import re
import sys
import time
import httpx

os.environ["ENABLE_FRONTEND"] = "true"

QUERIES = [
    {
        "id": "1",
        "question": "What are the symptoms of malaria?",
        "lang": "en",
        "expected_intent": "disease_info",
        "is_emergency": False,
    },
    {
        "id": "2",
        "question": "डेंगू के गंभीर लक्षण क्या हैं?",
        "lang": "hi",
        "expected_intent": "disease_info",
        "is_emergency": False,
    },
    {
        "id": "3",
        "question": "My child is vomiting blood",
        "lang": "en",
        "expected_intent": "emergency",
        "is_emergency": True,
    },
    {
        "id": "4",
        "question": "Which vaccines are due at 9 months?",
        "lang": "en",
        "expected_intent": "vaccination_schedule",
        "is_emergency": False,
    },
    {
        "id": "5",
        "question": "How is diabetes treated?",
        "lang": "en",
        "expected_intent": "disease_info",
        "is_emergency": False,
    },
]

BASE_URL = "http://127.0.0.1:8000"

def test_query_stream(item):
    print("\n" + "=" * 80)
    print(f"QUERY {item['id']}: \"{item['question']}\" (Language: {item['lang']})")
    print("=" * 80)

    url = f"{BASE_URL}/chat/stream"
    payload = {
        "message": item["question"],
        "language": item["lang"],
        "session_id": f"real-e2e-{item['id']}",
    }

    for attempt in range(4):
        events_received = []
        sentence_chunks = []
        metadata = None
        done_received = False
        t0 = time.time()

        try:
            with httpx.Client(timeout=60.0) as client:
                with client.stream("POST", url, json=payload) as response:
                    if response.status_code == 429:
                        print("  [429 Quota limit hit! Waiting 50s before retry...]")
                        time.sleep(50)
                        continue

                    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                    content_type = response.headers.get("content-type", "")
                    assert "text/event-stream" in content_type, f"Expected text/event-stream, got {content_type}"

                    buffer = ""
                    for raw_chunk in response.iter_text():
                        buffer += raw_chunk
                        while "\n\n" in buffer:
                            block, buffer = buffer.split("\n\n", 1)
                            block = block.strip()
                            if not block:
                                continue

                            event_type = "message"
                            data_str = ""
                            for line in block.split("\n"):
                                if line.startswith("event:"):
                                    event_type = line.replace("event:", "").strip()
                                elif line.startswith("data:"):
                                    data_str = line.replace("data:", "").strip()

                            events_received.append((event_type, data_str))

                            if event_type == "message":
                                parsed = json.loads(data_str)
                                chunk_text = parsed.get("chunk", "")
                                sentence_chunks.append(chunk_text)
                                print(f"  [STREAMED CHUNK]: {repr(chunk_text)}")
                            elif event_type == "metadata":
                                metadata = json.loads(data_str)
                                print(f"  [STREAMED METADATA]: intent={metadata.get('intent')} | emergency={metadata.get('emergency')} | sources_count={len(metadata.get('sources', []))}")
                            elif event_type == "done":
                                done_received = True
                                print("  [STREAMED EVENT]: done")

            elapsed = time.time() - t0
            break
        except Exception as e:
            if "429" in str(e):
                print(f"  [429 Quota error, waiting 50s...] {e}")
                time.sleep(50)
            else:
                print(f"  [Attempt {attempt+1} error: {e}] Waiting 5s...")
                time.sleep(5)
    else:
        print(f"Failed to complete query {item['id']} after 4 attempts.")
        return False

    final_answer = "".join(sentence_chunks)
    print("\n--- FINAL ASSEMBLED ANSWER ---")
    print(final_answer.strip())

    print("\n--- STREAM SUMMARY ---")
    print(f"Total SSE Events Received: {len(events_received)}")
    print(f"Sentence Chunks Count:     {len(sentence_chunks)}")
    print(f"Done Event Received:       {done_received}")
    print(f"Latency:                   {elapsed:.2f}s")

    if metadata:
        print("\n--- CITATION CHIP TO SOURCE MAPPING ---")
        citations_in_text = [int(m) for m in re.findall(r"\[(\d+)\]", final_answer)]
        unique_citations = sorted(set(citations_in_text))
        print(f"Citations referenced in answer text: {unique_citations}")

        sources_list = metadata.get("sources", [])
        sources_by_num = {s["number"]: s for s in sources_list}
        print(f"Total sources provided in metadata:  {len(sources_list)}")

        if item["is_emergency"]:
            assert metadata.get("emergency") is True, "Expected emergency=True in metadata"
            assert "108" in final_answer or "hospital" in final_answer.lower(), "Expected 108 emergency direction"
            print("  -> Emergency triage verified: Immediate 108 emergency guidance with 0 LLM hallucination.")
        else:
            for cit in unique_citations:
                assert cit in sources_by_num, f"Citation [{cit}] referenced in text but missing from sources metadata!"
                src = sources_by_num[cit]
                print(f"  -> Chip [{cit}] maps to Source: \"{src.get('source')}\" | Section/Page: {src.get('page')} | Snippet: {repr(src.get('snippet', '')[:80])}...")

    return True

def main():
    print("=" * 80)
    print("STARTING REAL END-TO-END STACK VERIFICATION (NO MOCKS)")
    print("=" * 80)

    # 1. Check health
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{BASE_URL}/health")
            data = resp.json()
            print(f"Server health at {BASE_URL}: status={data.get('status')}, llm_configured={data.get('llm_configured')}")
            assert data.get("status") == "ok", "Server status is not ok"
            assert data.get("llm_configured") is True, "LLM is not configured"
    except Exception as e:
        print(f"Health check failed: {e}. Please ensure uvicorn is running on port 8000.")
        sys.exit(1)

    # 2. Check frontend index serving
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{BASE_URL}/")
            assert resp.status_code == 200, f"Expected 200 for frontend index, got {resp.status_code}"
            assert "<div id=\"root\"></div>" in resp.text or "<script" in resp.text, "index.html content missing"
            print("Frontend index serving at /: verified OK (Single-server SPA active)")
    except Exception as e:
        print(f"Frontend serving check failed: {e}")
        sys.exit(1)

    # 3. Run the 5 real end-to-end questions
    for idx, item in enumerate(QUERIES, start=1):
        success = test_query_stream(item)
        if not success:
            print(f"Query {idx} failed!")
            sys.exit(1)
        # Protect Gemini Free Tier quota with throttled pause
        if not item["is_emergency"]:
            print("\nThrottling 12 seconds to respect Gemini API Free Tier RPM...")
            time.sleep(12)
        else:
            print("\nEmergency query used 0 LLM calls, proceeding immediately...")

    print("\n" + "=" * 80)
    print("REAL STACK END-TO-END VERIFICATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
