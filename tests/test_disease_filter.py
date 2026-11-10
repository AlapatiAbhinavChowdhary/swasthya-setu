from langchain_core.documents import Document
from swasthya_setu.generation.disease_filter import (
    clean_unexplained_abbreviations,
    detect_asked_diseases,
    filter_cross_disease_documents,
)
from swasthya_setu.generation.verification import verify_citations


def test_detect_asked_diseases_english_and_hindi():
    assert detect_asked_diseases("How is tuberculosis treated, in simple words?") == ["tuberculosis"]
    assert detect_asked_diseases("What are the warning signs of dengue?") == ["dengue"]
    assert detect_asked_diseases("मलेरिया के लक्षण क्या हैं?") == ["malaria"]
    assert detect_asked_diseases("टीबी का इलाज कैसे होता है, आसान भाषा में?") == ["tuberculosis"]
    assert detect_asked_diseases("Is there a vaccine for cholera?") in (["cholera", "child-immunization"], ["cholera"])
    # Ordinary question without disease
    assert detect_asked_diseases("Can I play football in the rain?") == []


def test_filter_cross_disease_documents_drops_unrelated_diseases():
    tb_doc = Document(
        page_content="TB is treated with special antibiotics.",
        metadata={"disease_ids": "tuberculosis", "doc_type": "fact_sheet"},
    )
    je_doc = Document(
        page_content="TBM treatment requires ATT and steroids in Japanese Encephalitis cases.",
        metadata={"disease_ids": "japanese-encephalitis", "doc_type": "guideline"},
    )
    malaria_doc = Document(
        page_content="Malaria treatment guidelines.",
        metadata={"disease_ids": "malaria", "doc_type": "guideline"},
    )

    matches = [(tb_doc, 0.85), (je_doc, 0.84), (malaria_doc, 0.80)]
    filtered = filter_cross_disease_documents(matches, ["tuberculosis"])

    # Only tb_doc must remain; je_doc and malaria_doc must be dropped
    assert len(filtered) == 1
    assert filtered[0][0].metadata["disease_ids"] == "tuberculosis"


def test_verify_citations_drops_cross_disease_citations():
    tb_doc = Document(
        page_content="Tuberculosis is curable with antibiotics.",
        metadata={"disease_ids": "tuberculosis"},
    )
    je_doc = Document(
        page_content="Encephalitis patients should be monitored closely.",
        metadata={"disease_ids": "japanese-encephalitis"},
    )
    docs = [tb_doc, je_doc]

    # Model generated an answer citing both [1] and [2] for a TB question
    raw_answer = "Tuberculosis is curable with antibiotics [1]. Encephalitis patients should be monitored [2]."
    cleaned, citations = verify_citations(
        raw_answer, docs, language="en", asked_diseases=["tuberculosis"]
    )

    # Citation [2] points to JE doc and must be dropped; only [1] is kept
    assert citations == [1]
    assert "[1]" in cleaned
    assert "[2]" not in cleaned
    assert "Encephalitis patients" not in cleaned


def test_clean_unexplained_abbreviations():
    text = "TB is managed with ATT and TBM requires special care under DOTS."
    cleaned = clean_unexplained_abbreviations(text)
    assert "anti-tubercular treatment (ATT)" in cleaned
    assert "tuberculous meningitis (TB infection of the brain)" in cleaned
    assert "Directly Observed Treatment Short-Course (DOTS)" in cleaned

