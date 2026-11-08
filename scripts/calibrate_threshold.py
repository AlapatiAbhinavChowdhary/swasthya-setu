"""Calibrate retrieval relevance scores on hard out-of-scope vs in-scope questions."""

from collections.abc import Iterable
from pathlib import Path
import statistics

from swasthya_setu.retrieval.vectorstore import load_index

IN_SCOPE_QUESTIONS = (
    # Core target diseases (EN)
    "What are the warning signs of severe dengue?",
    "How is dengue treated at home without dangerous medicines?",
    "What are the most common early symptoms of malaria?",
    "How is tuberculosis treated, in simple words?",
    "Which vaccines are due at 9 months under the National Immunization Schedule?",
    "What is the first aid for snakebite before reaching hospital?",
    "How should oral rehydration salts ORS be prepared for diarrhoea?",
    "What are the key prevention steps for cholera during an outbreak?",
    "How does hepatitis A spread and how to prevent it?",
    "What is the recommended wound wash procedure for a dog bite to prevent rabies?",
    "What blood pressure reading indicates hypertension in adults?",
    "What are common symptoms of type 2 diabetes?",
    "What iron-rich foods help treat nutritional anaemia?",
    "How to recognize danger signs during pregnancy and newborn care?",
    "What precautions should be taken to prevent heat stroke during heat waves?",
    "What are basic symptoms of common mental disorders like depression?",
    "What are safe water handling and sanitation practices in villages?",
    "What is the treatment duration for lymphatic filariasis?",
    "What are the signs of Japanese Encephalitis in children?",
    "How is kala-azar transmitted by sandflies?",
    # Core target diseases (HI)
    "डेंगू के गंभीर लक्षण और खतरे के संकेत क्या हैं?",
    "मलेरिया के लक्षण और उससे बचाव के उपाय क्या हैं?",
    "टीबी का इलाज कितने महीने तक चलता है?",
    "9 महीने के बच्चे को कौन से टीके लगते हैं?",
    "दस्त होने पर ओआरएस का घोल कैसे बनाना चाहिए?",
    "कुत्ते के काटने पर तुरंत क्या प्राथमिक उपचार करना चाहिए?",
    "सांप के काटने पर क्या नहीं करना चाहिए?",
    "उच्च रक्तचाप से बचने के लिए क्या सावधानी बरतें?",
    "गर्भावस्था के दौरान खतरे के मुख्य लक्षण क्या हैं?",
    "लू से बचने के लिए क्या उपाय करने चाहिए?",
)

HARD_OUT_OF_SCOPE_QUESTIONS = (
    # 1. Unindexed Medical Conditions (Cancer, Asthma, Kidney stones, Migraine, Thyroid, etc.)
    "What are the common warning signs of breast cancer in women?",
    "How is lung cancer diagnosed and what are the main stages?",
    "What triggers an acute asthma attack and how to use an inhaler?",
    "Best ways to pass a kidney stone naturally and prevent recurrence?",
    "What causes severe migraine headaches with visual aura?",
    "What are the symptoms of hypothyroidism and high TSH levels?",
    "How is rheumatoid arthritis treated in older adults?",
    "What are the early stages of Alzheimer disease and memory loss?",
    "How to relieve severe eczema itching and skin dryness?",
    "Do gallstones always require surgical removal of gallbladder?",
    "How do doctors treat cataract in the eye and what is lens replacement?",
    "Is psoriasis contagious and what causes chronic flareups?",
    "What are the early motor symptoms of Parkinson disease?",
    "How is chronic kidney disease stage 3 managed with diet?",
    "What causes glaucoma and high intraocular eye pressure?",
    "कैंसर के शुरुआती लक्षण क्या होते हैं और जांच कब करानी चाहिए?",
    "अस्थमा के दौरे को तुरंत रोकने के लिए क्या करें?",
    "गुर्दे की पथरी के क्या कारण और लक्षण हैं?",
    "माइग्रेन के सिरदर्द से राहत पाने के घरेलू उपाय?",
    "थायराइड की समस्या में वजन कैसे नियंत्रित रखें?",

    # 2. Borderline Wellness, Gym, Beauty, Diet, Supplements
    "How much whey protein powder should I take daily for muscle gain?",
    "Best 4-day gym workout split for burning visceral belly fat?",
    "Can biotin and collagen gummies really stop hair loss?",
    "How to get glowing skin using natural turmeric and gram flour face packs?",
    "Is 16:8 intermittent fasting safe for boosting metabolism?",
    "Does creatine monohydrate supplementation cause kidney damage in athletes?",
    "How many hours of REM and deep sleep does a smart watch track?",
    "Best anti-aging retinol serum concentration for dark spots and wrinkles?",
    "Should I take vitamin D3 60000 IU softgel capsules weekly?",
    "How to do intermittent cold showers for mental clarity and energy?",
    "वजन बढ़ाने के लिए कौन सा प्रोटीन पाउडर सबसे अच्छा है?",
    "चेहरे पर चमक लाने और मुहांसे हटाने के लिए घरेलू उपाय क्या हैं?",
    "जिम वर्कआउट के बाद क्या खाना चाहिए ताकि मांसपेशियां मजबूत हों?",
    "बालों का झड़ना रोकने के लिए कौन सा आयुर्वेदिक तेल लगाएं?",
    "अच्छी और गहरी नींद के लिए रात में क्या करना चाहिए?",

    # 3. Non-medical queries that use health words ("virus", "health", "injection", "fatal", "economic")
    "How to remove a trojan virus and malware from Windows 11 computer?",
    "What is the economic health and fiscal deficit of India in 2026?",
    "How to troubleshoot a fatal memory dump and kernel panic on Linux server?",
    "Preventing SQL injection vulnerabilities in Python backend code.",
    "What is the remedy for high corporate inflation in modern banking?",
    "How to check battery health and cycle count on Android smartphone?",
    "Is cabin fever a genuine psychological disorder in harsh winters?",
    "What is the best recipe for hot vegetable soup to stay warm in December?",
    "कंप्यूटर से मैलवेयर और कंप्यूटर वायरस कैसे हटाएं?",
    "भारतीय अर्थव्यवस्था का वित्तीय स्वास्थ्य इस तिमाही में कैसा है?",
)


def _scores(store, questions: Iterable[str]) -> list[tuple[str, float]]:
    scored_items = []
    for question in questions:
        matches = store.similarity_search_with_relevance_scores(question, k=1)
        if matches:
            scored_items.append((question, matches[0][1]))
        else:
            scored_items.append((question, 0.0))
    return scored_items


def _summary(label: str, items: list[tuple[str, float]]) -> None:
    if not items:
        print(f"{label}: no scores")
        return
    scores = sorted(score for _, score in items)
    p25 = scores[len(scores) // 4]
    p50 = statistics.median(scores)
    p75 = scores[(len(scores) * 3) // 4]
    print(
        f"{label} (count={len(scores)}): "
        f"min={scores[0]:.4f}  p25={p25:.4f}  p50={p50:.4f}  p75={p75:.4f}  max={scores[-1]:.4f}"
    )


def main() -> None:
    store = load_index(Path("vectorstore"))
    print(f"Total in-scope test questions: {len(IN_SCOPE_QUESTIONS)}")
    print(f"Total hard out-of-scope test questions: {len(HARD_OUT_OF_SCOPE_QUESTIONS)}\n")

    in_scope = _scores(store, IN_SCOPE_QUESTIONS)
    out_of_scope = _scores(store, HARD_OUT_OF_SCOPE_QUESTIONS)

    print("--- SCORE DISTRIBUTIONS ---")
    _summary("In-scope questions       ", in_scope)
    _summary("Hard out-of-scope queries", out_of_scope)

    in_min = min(score for _, score in in_scope)
    out_max = max(score for _, score in out_of_scope)
    print(f"\nIn-scope MIN score      : {in_min:.4f}")
    print(f"Hard out-of-scope MAX score: {out_max:.4f}")

    # Check overlaps
    overlaps = []
    for q, score in out_of_scope:
        if score >= in_min:
            overlaps.append((q, score))

    if overlaps:
        print(f"\n[!] Detected {len(overlaps)} overlapping out-of-scope queries with score >= in-scope min ({in_min:.4f}):")
        for q, score in sorted(overlaps, key=lambda x: x[1], reverse=True):
            print(f"  Score: {score:.4f} | Query: {q}")
        print("\nRecommendation: Implement explicit LLM intent gate for queries in the ambiguous score band.")
    else:
        print(f"\nClean separation achieved! No hard out-of-scope queries score above {in_min:.4f}.")


if __name__ == "__main__":
    main()
