import swasthya_setu.generation.agent as agent_module
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from swasthya_setu.generation.agent import _generate_answer

en_mock_answer = (
    "To prepare ORS:\n"
    "* Wash your hands with soap and clean water [1].\n"
    "* Pour the entire contents of 1 packet of ORS into 1 litre (1000 ml) of clean drinking water [1].\n"
    "* Stir well until the powder is completely dissolved [1].\n"
    "* Do not boil the prepared solution and use it within 24 hours [1]."
)
agent_module._llm = lambda: RunnableLambda(lambda _input: en_mock_answer)
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
print("=== ENGLISH ORS PREPARATION ANSWER ===")
print("Question: How is ORS prepared?")
print(en_state["answer"])
print(f"Citations: {en_state.get('citations')}")

hi_mock_answer = (
    "ओआरएस घोल तैयार करने का तरीका:\n"
    "* सबसे पहले साबुन और साफ पानी से हाथ धोएं [1]।\n"
    "* ओआरएस का पूरा पैकेट 1 लीटर (1000 मिली) साफ पीने के पानी में डालें [1]।\n"
    "* चम्मच से अच्छी तरह हिलाकर पूरी तरह घोल लें [1]।\n"
    "* तैयार घोल को 24 घंटे के भीतर इस्तेमाल करें [1]।"
)
agent_module._llm = lambda: RunnableLambda(lambda _input: hi_mock_answer)
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
print("\n=== HINDI ORS PREPARATION ANSWER ===")
print("Question: ओआरएस का घोल कैसे तैयार किया जाता है?")
print(hi_state["answer"])
print(f"Citations: {hi_state.get('citations')}")
