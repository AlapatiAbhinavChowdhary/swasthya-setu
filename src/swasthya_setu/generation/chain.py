from functools import cache

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from swasthya_setu.config import settings
from swasthya_setu.generation.prompts import SYSTEM_PROMPT
from swasthya_setu.retrieval.vectorstore import load_index

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)


@cache
def _store():
    return load_index()


def format_context(docs: list[Document]) -> str:
    """Number each chunk so the model can cite it as [1], [2], ..."""
    parts = []
    for i, d in enumerate(docs, start=1):
        src = d.metadata.get("source", "unknown")
        page = d.metadata.get("page_label", "?")
        parts.append(f"[{i}] (source: {src}, page {page})\n{d.page_content}")
    return "\n\n".join(parts)


def answer(question: str, k: int = 4) -> tuple[str, list[Document]]:
    """Retrieve the top-k chunks, then ask Gemini to answer from them."""
    docs = _store().similarity_search(question, k=k)
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
       
    )
    chain = prompt | llm | StrOutputParser()
    text = chain.invoke({"context": format_context(docs), "question": question})
    return text, docs