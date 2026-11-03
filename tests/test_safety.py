from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

from swasthya_setu.generation.agent import (
    _generate_answer,
    _verify_answer,
    _format_response,
    is_prescription_or_diagnosis,
    route_intent,
)
from swasthya_setu.generation.safety import emergency_response, is_emergency
from swasthya_setu.generation.verification import (
    FIXED_MESSAGES,
    PRESCRIPTION_REFUSAL,
    SAFE_REFUSAL,
    is_language_consistent,
    normalize_mixed_script_tokens,
    verify_citations,
)


def test_emergency_keywords_are_detected_in_english_and_hindi():
    assert is_emergency("My child is vomiting blood")
    assert is_emergency("बच्चा बहुत बीमार है और सांस लेने में दिक्कत है")


def test_citations_are_limited_to_retrieved_documents():
    documents = [Document(page_content="verified")]
    answer, citations = verify_citations("Fact [1] and fake [9].", documents)
    assert answer == "Fact [1] and fake ."
    assert citations == [1]


def test_grouped_citations_and_sources_match_exactly():
    documents = [
        Document(page_content="one"),
        Document(page_content="two"),
        Document(page_content="three"),
    ]
    answer, citations = verify_citations("Evidence [1, 2, 3].", documents)
    assert answer == "Evidence [1, 2, 3]."
    assert citations == [1, 2, 3]


def test_mocked_grouped_llm_citations_produce_matching_sources(monkeypatch):
    monkeypatch.setattr(
        "swasthya_setu.generation.agent._llm",
        lambda: RunnableLambda(lambda _input: "Evidence [1, 2, 3]."),
    )
    documents = [
        Document(page_content=f"Evidence {number}.", metadata={"source": f"{number}.pdf"})
        for number in range(1, 4)
    ]
    state = _generate_answer(
        {
            "question": "What is documented?",
            "language": "en",
            "intent": "disease_info",
            "documents": documents,
        }
    )
    result = _format_response(state)
    assert state["citations"] == [1, 2, 3]
    assert [source["source"] for source in result["response"]["sources"]] == [
        "1.pdf",
        "2.pdf",
        "3.pdf",
    ]


def test_invalid_grouped_citations_are_removed_from_text():
    documents = [Document(page_content="one"), Document(page_content="two")]
    answer, citations = verify_citations("Evidence [1, 2, 3].", documents)
    assert answer == "Evidence [1, 2]."
    assert citations == [1, 2]


def test_uncited_answer_becomes_safe_refusal():
    answer, citations = verify_citations("Unsupported fact.", [])
    assert answer == SAFE_REFUSAL
    assert citations == []


def test_dengue_treatment_is_routed_to_rag():
    assert route_intent("How is dengue treated at home?", "out_of_scope") == "disease_info"
    assert not is_prescription_or_diagnosis("How is dengue treated at home?")


def test_diabetes_without_relevant_context_uses_no_verified_info_message():
    answer, citations = verify_citations("No supported answer.", [])
    assert answer == SAFE_REFUSAL
    assert citations == []


def test_dengue_medicine_request_uses_prescription_refusal():
    question = "What medicine should I take for dengue?"
    assert is_prescription_or_diagnosis(question)
    assert route_intent(question, "disease_info") == "out_of_scope"
    assert PRESCRIPTION_REFUSAL != SAFE_REFUSAL


def test_format_response_includes_only_cited_sources():
    state = {
        "question": "What are dengue warning signs?",
        "answer": "Bleeding can be a warning sign [1].",
        "intent": "disease_info",
        "emergency": False,
        "citations": [1],
        "documents": [
            Document(
                page_content="Warning signs include bleeding.",
                metadata={"source": "dengue.pdf", "page_label": "12"},
            ),
            Document(
                page_content="Uncited context.",
                metadata={"source": "other.pdf", "page_label": "3"},
            ),
        ],
    }
    result = _format_response(state)
    assert result["response"]["language"] == "en"
    assert result["response"]["sources"] == [
        {
            "source": "dengue.pdf",
            "page": "12",
            "snippet": "Warning signs include bleeding.",
        }
    ]


def test_hindi_format_response_detects_language():
    result = _format_response(
        {
            "question": "डेंगू के गंभीर लक्षण क्या हैं?",
            "answer": "स्रोत के अनुसार जानकारी [1].",
            "intent": "disease_info",
            "emergency": False,
            "citations": [],
            "documents": [],
        }
    )
    assert result["response"]["language"] == "hi"


def test_hindi_ratio_allows_latin_medicine_terms():
    text = "डेंगू में paracetamol और NSAIDs से बचें।"
    assert is_language_consistent(text, "hi", "paracetamol NSAIDs dengue")
    assert not is_language_consistent("I do not have verified information.", "hi")
    assert not is_language_consistent("सैलicylates से बचें।", "hi")
    assert normalize_mixed_script_tokens("सैलicylates से बचें।") == "salicylates से बचें।"


def test_fixed_messages_are_localized():
    answer, _ = verify_citations("No citation.", [], language="hi")
    assert "सत्यापित जानकारी" in answer
    assert "अस्पताल" in emergency_response("hi")
    prescription = _generate_answer(
        {"question": "मुझे दवा बताइए", "language": "hi", "intent": "out_of_scope"}
    )
    assert "निदान" in prescription["answer"]


def test_fixed_emergency_and_disclaimer_messages_preserve_spacing():
    english_emergency = emergency_response("en")
    hindi_emergency = emergency_response("hi")
    assert "call 108" in english_emergency
    assert "call108" not in english_emergency
    assert "108 पर कॉल करें" in hindi_emergency
    assert "108पर" not in hindi_emergency
    assert "Do not self-medicate." in FIXED_MESSAGES["disclaimer"]["en"]
    assert "खुद से दवा न लें।" in FIXED_MESSAGES["disclaimer"]["hi"]


def test_medicine_answer_gets_localized_disclaimer(monkeypatch):
    monkeypatch.setattr(
        "swasthya_setu.generation.agent._llm",
        lambda: RunnableLambda(lambda _input: "paracetamol से बुखार में मदद मिलती है [1]."),
    )
    state = _verify_answer(
        {
            "question": "डेंगू में paracetamol के बारे में बताइए",
            "language": "hi",
            "intent": "disease_info",
            "answer": "paracetamol से बुखार में मदद मिलती है [1].",
            "documents": [
                Document(page_content="paracetamol is used for fever.")
            ],
        }
    )
    assert "खुद से दवा न लें" in state["answer"]


def test_existing_disclaimer_is_not_duplicated():
    state = _verify_answer(
        {
            "question": "Can I take paracetamol?",
            "language": "en",
            "intent": "disease_info",
            "answer": (
                "The guideline mentions paracetamol [1]. "
                "Do not self-medicate; ask a doctor."
            ),
            "documents": [Document(page_content="paracetamol for fever.")],
        }
    )
    assert state["answer"].count("self-medicate") == 1


def test_personal_paracetamol_question_uses_cited_guideline(monkeypatch):
    question = "Can I take paracetamol for dengue fever?"
    response = (
        "The dengue guideline says paracetamol may be used for fever and body "
        "ache [1]. Do not self-medicate; check with a doctor or health worker."
    )
    monkeypatch.setattr(
        "swasthya_setu.generation.agent._llm",
        lambda: RunnableLambda(lambda _input: response),
    )
    state = _generate_answer(
        {
            "question": question,
            "intent": "disease_info",
            "language": "en",
            "documents": [
                Document(
                    page_content="Fever and body ache are best treated with paracetamol.",
                    metadata={"source": "dengue.pdf", "page_label": "47"},
                )
            ],
        }
    )
    assert route_intent(question, "out_of_scope") == "disease_info"
    assert "paracetamol" in state["answer"]
    assert state["citations"] == [1]


def test_english_answer_is_retried_when_model_returns_hindi(monkeypatch):
    responses = iter(
        [
            "डेंगू में कुछ दर्दनिवारक दवाओं से बचें [1].",
            "Avoid salicylates and other NSAIDs in dengue [1].",
        ]
    )
    monkeypatch.setattr(
        "swasthya_setu.generation.agent._llm",
        lambda: RunnableLambda(lambda _input: next(responses)),
    )
    state = _verify_answer(
        {
            "question": "Which painkillers should be avoided in dengue?",
            "intent": "disease_info",
            "language": "en",
            "answer": next(responses),
            "citations": [1],
            "documents": [
                Document(
                    page_content="Avoid salicylates and NSAIDs.",
                    metadata={"source": "dengue.pdf", "page_label": "47"},
                )
            ],
        }
    )
    formatted = _format_response(state)
    assert is_language_consistent(state["answer"], "en")
    assert formatted["response"]["language_consistent"] is True
    assert "Avoid" in state["answer"]
