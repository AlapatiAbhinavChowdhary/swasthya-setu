from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

from swasthya_setu.generation.agent import (
    _generate_answer,
    _verify_answer,
    _format_response,
    is_prescription_or_diagnosis,
    route_intent,
)
from swasthya_setu.generation.safety import is_emergency
from swasthya_setu.generation.verification import (
    PRESCRIPTION_REFUSAL,
    SAFE_REFUSAL,
    is_language_consistent,
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
