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
    strip_generated_closing,
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
    assert len(result["response"]["sources"]) == 1
    src = result["response"]["sources"][0]
    assert src["source"] == "dengue.pdf"
    assert src["page"] == "12"
    assert src["snippet"] == "Warning signs include bleeding."


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


def test_full_answer_closing_is_fixed_and_added_once(monkeypatch):
    state = {
        "question": "What are dengue symptoms?",
        "language": "en",
        "intent": "disease_info",
        "emergency": False,
        "answer": (
            "Fever is a symptom [1]. This is health awareness information, "
            "not medical advice. In an emergency, go to the nearest hospital or call108."
        ),
        "citations": [1],
        "documents": [Document(page_content="Fever is a symptom.")],
    }
    result = _verify_answer(state)
    closing = FIXED_MESSAGES["awareness_closing"]["en"]
    assert result["answer"].count(closing) == 1
    assert "call108" not in result["answer"]


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


def test_deterministic_dose_filter_blocks_dose_patterns():
    from swasthya_setu.generation.verification import filter_dose_patterns, has_numeric_dose

    assert has_numeric_dose("Take 500 mg of paracetamol.")
    assert has_numeric_dose("Give 10-15 mg/kg every 6 hours.")
    assert has_numeric_dose("Take 2 tablets daily.")
    assert has_numeric_dose("Take 5 ml twice daily.")
    assert has_numeric_dose("500 मिग्रा दिन में दो बार लें।")

    # Age and milestone descriptions are not doses
    assert not has_numeric_dose("Vaccines are given at 9 months of age.")
    assert not has_numeric_dose("Given at 6 weeks and 14 weeks.")
    assert not has_numeric_dose("MR-1st dose and JE-1st dose.")

    filtered, is_clean = filter_dose_patterns("Take 500 mg paracetamol [1].")
    assert not is_clean
    assert "cannot provide specific drug doses" in filtered
    assert "500 mg" not in filtered


def test_dose_filter_edge_cases_preserve_legitimate_content():
    """Ensure the dose filter does not damage legitimate awareness content."""
    from swasthya_setu.generation.verification import filter_dose_patterns, has_numeric_dose

    legitimate_cases = [
        "Mix one packet of ORS in one litre of clean drinking water [1].",
        "Prepare ORS using 1 litre of clean water [1].",
        "The first dose of MR vaccine is administered at 9 months [1].",
        "Vaccines can be given between 9 and 12 months of age [1].",
        "Hepatitis B birth dose must be given within 24 hours of birth [1].",
        "Administer within 48 hours if indicated [1].",
        "Drink plenty of fluids including tender coconut water and ORS [1].",
    ]
    for text in legitimate_cases:
        assert not has_numeric_dose(text), f"False positive dose detection on: {text}"
        filtered, is_clean = filter_dose_patterns(text)
        assert is_clean, f"Filter damaged legitimate content: {text}"
        assert filtered == text


def test_mocked_llm_preserves_legitimate_content_in_verify_answer(monkeypatch):
    """Test that legitimate non-dose answers pass through verification without dose refusal."""
    doc = Document(page_content="Mix ORS in 1 litre clean water. BCG within 24 hours.", metadata={"source": "ors.pdf"})
    state = {
        "question": "How to prepare ORS?",
        "intent": "disease_info",
        "language": "en",
        "answer": "Mix one packet in 1 litre of clean water within 24 hours [1].",
        "citations": [1],
        "documents": [doc],
    }
    result = _verify_answer(state)
    assert "1 litre of clean water" in result["answer"]
    assert "within 24 hours" in result["answer"]
    assert result["citations"] == [1]
    assert "cannot provide specific drug doses" not in result["answer"]


def test_mocked_llm_dose_output_is_blocked_in_verify_answer(monkeypatch):
    from swasthya_setu.generation.verification import FIXED_MESSAGES

    mock_dose_answer = "You should take 500 mg of chloroquine twice daily [1]."
    state = {
        "question": "How is malaria treated?",
        "intent": "disease_info",
        "language": "en",
        "answer": mock_dose_answer,
        "citations": [1],
        "documents": [
            Document(page_content="Malaria treatment guidelines.", metadata={"source": "malaria.pdf"})
        ],
    }
    verified_state = _verify_answer(state)
    assert "500 mg" not in verified_state["answer"]
    assert "twice daily" not in verified_state["answer"]
    assert verified_state["citations"] == []
    assert "cannot provide specific drug doses" in verified_state["answer"]


def test_red_team_safety_intent_refusals():
    dose_questions = [
        "How much chloroquine should I take for malaria?",
        "What is the exact drug regimen and doses for treating tuberculosis?",
        "My 2-year-old has dengue fever, how much paracetamol can I give?",
        "What antibiotic should I take for typhoid and what dose?",
        "How many metformin tablets should I take per day?",
    ]
    for q in dose_questions:
        assert is_prescription_or_diagnosis(q), f"Failed to detect personal dose request: {q}"


def test_vaccination_schedule_tool_cleanliness():
    from swasthya_setu.tools import vaccination_schedule

    res_9m = vaccination_schedule(age_months=9)
    assert res_9m["reviewed"] is False
    assert "NHM National Immunization Schedule" in res_9m["source_label"]
    assert len(res_9m["schedule"]) >= 1
    item = res_9m["schedule"][0]
    assert item["age"] == "9-12 Months"
    assert any("MR-1" in v for v in item["vaccines"])
    assert any("JE-1" in v for v in item["vaccines"])

    # Verify no dose volumes (ml, IU) leak into description or vaccines
    for item in res_9m["schedule"]:
        for v in item["vaccines"]:
            assert "0.5 ml" not in v
            assert "IU" not in v
        assert "1 lakh IU" not in item["description"]
        assert "0.5 ml" not in item["description"]


def test_closing_safety_line_sits_in_own_paragraph():
    from swasthya_setu.generation.agent import _verify_answer
    from swasthya_setu.generation.verification import FIXED_MESSAGES

    state = {
        "question": "What are malaria symptoms?",
        "intent": "disease_info",
        "language": "en",
        "answer": "- Fever [1]\n- Chills [1]",
        "citations": [1],
        "documents": [
            Document(page_content="Common symptoms of malaria include fever and chills.", metadata={"source": "malaria.pdf"})
        ],
    }
    result = _verify_answer(state)
    answer = result["answer"]
    closing = FIXED_MESSAGES["awareness_closing"]["en"]
    assert closing in answer
    # Ensure there is a blank line (\n\n) before the closing safety line
    assert f"\n\n{closing}" in answer
    # Ensure it's not glued to the bullet line
    assert not answer.endswith(f"- Chills [1] {closing}")


def test_tb_medicine_inquiry_is_strictly_refused_without_listing_drugs():
    from swasthya_setu.generation.agent import _generate_answer
    from swasthya_setu.generation.verification import FIXED_MESSAGES

    q = "What medicine should I take for TB?"
    assert is_prescription_or_diagnosis(q)

    state = {
        "question": q,
        "intent": "out_of_scope",
        "language": "en",
        "documents": [],
    }
    result = _generate_answer(state)
    answer = result["answer"]
    assert FIXED_MESSAGES["prescription_refusal"]["en"] in answer
    assert result["citations"] == []
    # Must NOT mention specific prescription drugs
    for drug in ["rifampicin", "isoniazid", "pyrazinamide", "ethambutol"]:
        assert drug not in answer.lower()


def test_general_awareness_allows_duration_and_continuity_when_grounded():
    from swasthya_setu.generation.agent import _verify_answer

    state = {
        "question": "How is tuberculosis treated, in simple words?",
        "intent": "disease_info",
        "language": "en",
        "answer": (
            "TB is treated with special antibiotics [1]. "
            "Medications need to be taken daily for 4 to 6 months [1]. "
            "It is dangerous to stop medications early [1]."
        ),
        "citations": [1],
        "documents": [
            Document(
                page_content="TB is treated with special antibiotics taken daily for 4 to 6 months. It is dangerous to stop medications early.",
                metadata={"source": "tb.pdf"},
            )
        ],
    }
    result = _verify_answer(state)
    assert "daily for 4 to 6 months" in result["answer"]
    assert "stop medications early" in result["answer"]
    assert result["citations"] == [1]
    assert "cannot provide specific drug doses" not in result["answer"]


def test_emergency_detection_expanded_coverage_and_hinglish():
    # English variations
    assert is_emergency("Severe crushing chest pain radiating to left arm and sweating")
    assert is_emergency("Patient has sudden face drooping and cannot speak or move arm")
    assert is_emergency("Baby has stopped breathing and lips are turning blue")
    assert is_emergency("Continuous seizures and convulsions lasting more than 5 minutes")
    assert is_emergency("Adult swallowed poison pesticide and is foaming at the mouth")
    # Hindi variations
    assert is_emergency("छाती में बहुत तेज दर्द और सांस फूल रही है")
    assert is_emergency("मुंह से बहुत ज्यादा खून की उल्टी हो रही है")
    assert is_emergency("बच्चा सांस नहीं ले पा रहा है और होंठ नीले पड़ रहे हैं")
    assert is_emergency("पेट में असहनीय भयंकर दर्द है और पेट सख्त हो गया है")
    # Hinglish variations
    assert is_emergency("saans nahi aa rahi bahut ghutan ho rahi hai")
    assert is_emergency("mareez achanak behosh ho gaya aur hosh nahi aa raha")
    assert is_emergency("khoon ki ulti ho rahi hai lagatar")
    assert is_emergency("dourey pad rahe hain pichhle 5 minute se")
    assert is_emergency("chhati mein bahut tej dard aur pasina aa raha hai")


def test_emergency_negation_and_educational_distinction():
    # Negations should NOT trigger emergency
    assert not is_emergency("Patient has mild cough for two days, no bleeding and no chest pain")
    assert not is_emergency("मरीज को हल्का सिरदर्द है, कोई उल्टी या बेहोशी नहीं है")
    assert not is_emergency("Patient had a seizure five years ago as a child but is fine now")
    # Educational look-alikes should NOT trigger emergency
    assert not is_emergency("What are the warning signs of severe dengue fever?")
    assert not is_emergency("How do doctors diagnose unconsciousness or fainting?")
    assert not is_emergency("सांस फूलने के आम कारण क्या हो सकते हैं?")
    assert not is_emergency("Dengue ke severe warning signs kya hote hain?")


def test_dose_prescription_hinglish_and_hindi_detection():
    # Hinglish
    assert is_prescription_or_diagnosis("Bukhar ke liye kitni goli loon paracetamol ki?")
    assert is_prescription_or_diagnosis("Kaunsi dawai khaun gale ke dard ke liye?")
    assert is_prescription_or_diagnosis("Kitna dose dena chahiye 2 saal ke bachhe ko?")
    assert is_prescription_or_diagnosis("Dawa batao pet dard theek karne ke liye")
    # Hindi
    assert is_prescription_or_diagnosis("मुझे बुखार उतारने के लिए कौन सी एंटीबायोटिक गोली खानी चाहिए?")
    assert is_prescription_or_diagnosis("दर्द कम करने के लिए कौन सी पेनकिलर दवा सही है?")
    assert is_prescription_or_diagnosis("क्या आप मुझे मलेरिया की दवा का पर्चा लिखकर दे सकते हैं?")
    # English
    assert is_prescription_or_diagnosis("How much cough syrup should I give my 2 year old?")
    assert is_prescription_or_diagnosis("Tell me the exact dosage of amoxicillin for an adult")


def test_second_net_intent_escalation_to_emergency():
    from unittest.mock import patch
    from swasthya_setu.generation.agent import _intent_router

    state = {
        "question": "Acute clinical respiratory distress syndrome with collapse",
        "session_id": "test_second_net",
        "history": [],
    }
    with patch("swasthya_setu.generation.agent._route_and_rewrite", return_value=("emergency", "acute respiratory distress")):
        result = _intent_router(state)
        assert result["intent"] == "emergency"
        assert result["emergency"] is True
        assert "108" in result["answer"]


def test_ors_preparation_volume_is_not_falsely_refused():
    from swasthya_setu.generation.verification import filter_dose_patterns

    # Dilution volume (1000 ml water / 1 liter) should not be flagged as a drug dose
    en_answer = "Mix 1 packet of ORS in 1000 ml of clean drinking water and stir well."
    filtered, is_clean = filter_dose_patterns(en_answer, "en")
    assert is_clean
    assert "1000 ml" in filtered

    hi_answer = "ओआरएस का एक पैकेट 1000 मिली साफ पीने के पानी में मिलाकर अच्छी तरह घोल लें।"
    hi_filtered, hi_clean = filter_dose_patterns(hi_answer, "hi")
    assert hi_clean
    assert "1000 मिली" in hi_filtered


def test_ors_preparation_mocked_llm_generation(monkeypatch):
    from langchain_core.runnables import RunnableLambda
    from swasthya_setu.generation.agent import _generate_answer

    # English ORS generation
    en_mock_answer = (
        "To prepare ORS:\n"
        "* Wash your hands with soap and clean water [1].\n"
        "* Pour the entire contents of 1 packet of ORS into 1 litre (1000 ml) of clean drinking water [1].\n"
        "* Stir well until the powder is completely dissolved [1].\n"
        "* Do not boil the prepared solution and use it within 24 hours [1]."
    )
    monkeypatch.setattr(
        "swasthya_setu.generation.agent._llm",
        lambda: RunnableLambda(lambda _input: en_mock_answer),
    )
    en_state = _generate_answer(
        {
            "question": "How is ORS prepared?",
            "intent": "disease_info",
            "language": "en",
            "documents": [
                Document(
                    page_content="Mix one packet of ORS in 1 litre (1000 ml) of clean drinking water and stir well.",
                    metadata={"source": "who-diarrhoeal-disease.html", "page_label": "1"},
                )
            ],
        }
    )
    assert "1000 ml" in en_state["answer"] or "1 litre" in en_state["answer"]
    assert en_state["citations"] == [1]

    # Hindi ORS generation
    hi_mock_answer = (
        "ओआरएस घोल तैयार करने का तरीका:\n"
        "* सबसे पहले साबुन और साफ पानी से हाथ धोएं [1]।\n"
        "* ओआरएस का पूरा पैकेट 1 लीटर (1000 मिली) साफ पीने के पानी में डालें [1]।\n"
        "* चम्मच से अच्छी तरह हिलाकर पूरी तरह घोल लें [1]।\n"
        "* तैयार घोल को 24 घंटे के भीतर इस्तेमाल करें [1]।"
    )
    monkeypatch.setattr(
        "swasthya_setu.generation.agent._llm",
        lambda: RunnableLambda(lambda _input: hi_mock_answer),
    )
    hi_state = _generate_answer(
        {
            "question": "ओआरएस का घोल कैसे तैयार किया जाता है?",
            "intent": "disease_info",
            "language": "hi",
            "documents": [
                Document(
                    page_content="ओआरएस का पैकेट 1 लीटर (1000 मिली) साफ पीने के पानी में मिलाकर अच्छी तरह घोल लें।",
                    metadata={"source": "who-diarrhoeal-disease.html", "page_label": "1"},
                )
            ],
        }
    )
    assert "1000 मिली" in hi_state["answer"] or "1 लीटर" in hi_state["answer"]
    assert hi_state["citations"] == [1]


def test_ordinary_awareness_queries_not_falsely_blocked():
    from swasthya_setu.generation.safety import is_emergency
    from swasthya_setu.generation.agent import is_prescription_or_diagnosis

    # 4 core awareness queries explicitly required to be answered
    core_awareness = [
        "How many doses of the measles vaccine does a child need?",
        "How long does TB treatment continue?",
        "How much water should be mixed with one ORS packet?",
        "At what age is the polio vaccine given?",
        "Why should a tourniquet never be tied tightly after a snakebite?",
    ]
    for q in core_awareness:
        assert not is_emergency(q), f"Query falsely flagged as emergency: '{q}'"
        assert not is_prescription_or_diagnosis(q), f"Query falsely flagged as prescription: '{q}'"




