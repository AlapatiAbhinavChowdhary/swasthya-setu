import json
import logging
import re
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("final_verify")

from swasthya_setu.config import get_settings
from swasthya_setu.generation.agent import run_agent, _route_and_rewrite, _invoke_llm_with_retry
from swasthya_setu.generation.chain import _store, format_context
from swasthya_setu.generation.safety import is_emergency
from swasthya_setu.generation.verification import (
    is_chunk_supporting_sentence,
    verify_citations,
    drop_empty_headings,
    clean_redundant_phrasing,
    _STOPWORDS,
)

settings = get_settings()
store = _store()

def compute_sentence_support_score(sentence: str, doc_text: str) -> tuple[float, bool, str]:
    """Compute per-sentence lexical support score and check validity."""
    doc_lower = doc_text.lower()
    clean_sentence = re.sub(r"\[(?:\d+\s*,\s*)*\d+\]", "", sentence).strip()
    
    # Helplines: 108 and 112 must never be cited unless doc contains them
    if re.search(r"\b108\b", clean_sentence) and "108" not in doc_lower:
        return 0.0, False, "Helpline 108 not in document"
    if re.search(r"\b112\b", clean_sentence) and "112" not in doc_lower:
        return 0.0, False, "Helpline 112 not in document"
        
    is_non_latin = any(ord(c) >= 0x0900 for c in clean_sentence)
    if is_non_latin:
        words = re.findall(r"[\u0900-\u097f]+", clean_sentence)
        content_words = [w for w in words if w not in _STOPWORDS and len(w) >= 2]
        if not content_words:
            return 1.0, True, "No content words"
        matches = sum(1 for w in content_words if w.lower() in doc_lower)
        score = matches / len(content_words)
        supported = score >= 0.20
        return score, supported, f"Devanagari overlap: {matches}/{len(content_words)} ({score:.1%})"
    else:
        words = re.findall(r"\b[a-z0-9\-]{3,}\b", clean_sentence.lower())
        content_words = [w for w in words if w not in _STOPWORDS]
        if not content_words:
            return 1.0, True, "No content words"
        matches = sum(1 for w in content_words if w in doc_lower)
        score = matches / len(content_words)
        supported = score >= 0.20
        return score, supported, f"Latin overlap: {matches}/{len(content_words)} ({score:.1%})"


def verify_snakebite_answers():
    print("\n" + "=" * 80)
    print("STEP 1: SNAKEBITE EVIDENCE & GROUNDING AUDIT (BY CODE FROM CHROMA)")
    print("=" * 80)

    for q, lang in [
        ("What is the first aid for snakebite?", "en"),
        ("साँप के काटने पर प्राथमिक उपचार क्या है?", "hi"),
    ]:
        print(f"\n>>> QUERY ({lang}): {q}")
        time.sleep(4.2)
        res = run_agent(q, session_id=f"snake_{lang}", language=lang)
        answer = res["answer"]
        citations = res.get("citations", [])
        sources = res.get("sources", [])
        
        print("\n--- RAW GENERATED ANSWER ---")
        print(answer)
        print(f"Reported citations: {citations}")
        
        print("\n--- PER-SENTENCE SUPPORT SCORES ---")
        lines = [line.strip() for line in answer.split("\n") if line.strip()]
        for line in lines:
            cites = [int(v) for v in re.findall(r"\[(\d+)\]", line)]
            print(f"\nLine: {line}")
            if not cites:
                print("  [Uncited statement]")
                if "108" in line or "112" in line:
                    print("  -> Valid: Fixed uncited emergency helpline line.")
                continue
            for c in cites:
                if 1 <= c <= len(sources):
                    src_info = sources[c - 1]
                    doc_snippet = src_info.get("snippet", "")
                    score, supp, reason = compute_sentence_support_score(line, doc_snippet)
                    status = "SUPPORTED" if supp else "UNSUPPORTED"
                    print(f"  Chunk [{c}] Score: {score:.3f} | Status: {status} | Detail: {reason}")
                else:
                    print(f"  Chunk [{c}] OUT OF RANGE!")
        
        print("\n--- EXACT CHROMA STORED TEXTS FOR CITED CHUNKS ---")
        for c in sorted(set(citations)):
            if 1 <= c <= len(sources):
                src_info = sources[c - 1]
                print(f"\n>>> [Chunk {c}] Metadata:")
                print(f"    Source File: {src_info.get('source')}")
                print(f"    Page Number: {src_info.get('page')}")
                print(f"    Publisher:   {src_info.get('publisher')}")
                print(f"    Year:        {src_info.get('year')}")
                print(f"    Exact Stored Text Snippet:")
                print(f"    \"\"\"{src_info.get('snippet')}\"\"\"")


def verify_ors_answers():
    print("\n" + "=" * 80)
    print("STEP 2: ORS WORDING VERIFICATION (ENGLISH & HINDI)")
    print("=" * 80)

    for q, lang in [
        ("How is ORS prepared?", "en"),
        ("ओआरएस का घोल कैसे तैयार किया जाता है?", "hi"),
    ]:
        print(f"\n>>> QUERY ({lang}): {q}")
        time.sleep(4.2)
        res = run_agent(q, session_id=f"ors_{lang}", language=lang)
        answer = res["answer"]
        print("\n--- RAW GENERATED ANSWER ---")
        print(answer)
        print(f"Citations: {res.get('citations')}")
        
        if lang == "en":
            has_packet_guide = "instructions printed on the ors packet" in answer.lower() or "follow the instructions" in answer.lower()
            print(f"Verified packet instruction phrasing present: {has_packet_guide}")
        else:
            has_packet_guide = "पैकेट" in answer and ("निर्देश" in answer or "लिखे" in answer)
            print(f"Verified Hindi packet instruction phrasing present: {has_packet_guide}")


def run_emergency_holdouts():
    print("\n" + "=" * 80)
    print("STEP 5: GEMINI EMERGENCY HOLDOUTS RE-RUN WITH RETRY ACTIVE")
    print("=" * 80)

    # 1. Hold-Out 40 (eval/live_generated_holdout.json)
    h40_path = Path("eval/live_generated_holdout.json")
    with open(h40_path, "r", encoding="utf-8") as f:
        h40_data = json.load(f)
    emergencies_40 = h40_data.get("emergencies", [])[:40]
    print(f"\nEvaluating Hold-out 1: {len(emergencies_40)} emergency queries...")

    caught_40 = 0
    misses_40 = []
    both_40 = 0
    rule_only_40 = 0
    llm_only_40 = 0

    for idx, q in enumerate(emergencies_40, 1):
        rule_flag = is_emergency(q)
        if not rule_flag:
            time.sleep(4.2)  # Respect free tier rate limit
            intent, sq, urgency, asks_dose = _route_and_rewrite(q)
            llm_flag = (intent == "emergency" or urgency == "emergency")
            if llm_flag:
                caught_40 += 1
                llm_only_40 += 1
            else:
                misses_40.append((idx, q, intent, urgency))
        else:
            caught_40 += 1
            # Check if LLM also caught it
            time.sleep(4.2)
            intent, sq, urgency, asks_dose = _route_and_rewrite(q)
            llm_flag = (intent == "emergency" or urgency == "emergency")
            if llm_flag:
                both_40 += 1
            else:
                rule_only_40 += 1

    recall_40 = (caught_40 / len(emergencies_40)) * 100
    print(f"\nHold-out 1 Results: {caught_40}/{len(emergencies_40)} caught ({recall_40:.1f}%)")
    print(f"  - Caught by Both (Rule + LLM): {both_40}")
    print(f"  - Caught by Rule Layer Only:   {rule_only_40}")
    print(f"  - Caught by LLM Router Only:   {llm_only_40}")
    print(f"  - Misses: {len(misses_40)}")
    for m in misses_40:
        print(f"    Missed #{m[0]}: \"{m[1]}\" -> intent={m[2]}, urgency={m[3]}")

    # 2. Hold-Out 60 (eval/new_holdout_90.json)
    h60_path = Path("eval/new_holdout_90.json")
    with open(h60_path, "r", encoding="utf-8") as f:
        h60_data = json.load(f)
    emergencies_60 = h60_data.get("emergencies", [])[:60]
    print(f"\nEvaluating Hold-out 2: {len(emergencies_60)} emergency queries...")

    caught_60 = 0
    misses_60 = []
    both_60 = 0
    rule_only_60 = 0
    llm_only_60 = 0

    for idx, q in enumerate(emergencies_60, 1):
        rule_flag = is_emergency(q)
        if not rule_flag:
            time.sleep(4.2)
            intent, sq, urgency, asks_dose = _route_and_rewrite(q)
            llm_flag = (intent == "emergency" or urgency == "emergency")
            if llm_flag:
                caught_60 += 1
                llm_only_60 += 1
            else:
                misses_60.append((idx, q, intent, urgency))
        else:
            caught_60 += 1
            time.sleep(4.2)
            intent, sq, urgency, asks_dose = _route_and_rewrite(q)
            llm_flag = (intent == "emergency" or urgency == "emergency")
            if llm_flag:
                both_60 += 1
            else:
                rule_only_60 += 1

    recall_60 = (caught_60 / len(emergencies_60)) * 100
    print(f"\nHold-out 2 Results: {caught_60}/{len(emergencies_60)} caught ({recall_60:.1f}%)")
    print(f"  - Caught by Both (Rule + LLM): {both_60}")
    print(f"  - Caught by Rule Layer Only:   {rule_only_60}")
    print(f"  - Caught by LLM Router Only:   {llm_only_60}")
    print(f"  - Misses: {len(misses_60)}")
    for m in misses_60:
        print(f"    Missed #{m[0]}: \"{m[1]}\" -> intent={m[2]}, urgency={m[3]}")

    total_caught = caught_40 + caught_60
    total_emergencies = len(emergencies_40) + len(emergencies_60)
    total_recall = (total_caught / total_emergencies) * 100
    print(f"\n========================================================")
    print(f"COMBINED HOLDOUT RECALL: {total_caught}/{total_emergencies} ({total_recall:.1f}%)")
    print(f"========================================================")


if __name__ == "__main__":
    verify_snakebite_answers()
    verify_ors_answers()
    run_emergency_holdouts()
