"""Post-generation checks for grounded responses."""

import re

from langchain_core.documents import Document

SAFE_REFUSAL = (
    "I do not have verified information on that. "
    "Please ask a doctor, ASHA worker or health centre."
)

PRESCRIPTION_REFUSAL = (
    "I cannot diagnose you or recommend medicines or doses. "
    "Please ask a doctor, ASHA worker or health centre."
)


def verify_citations(text: str, documents: list[Document]) -> tuple[str, list[int]]:
    """Keep only citations that refer to retrieved documents.

    An answer without a valid citation is replaced with the standard refusal so
    the model cannot turn a retrieval miss into an unsupported medical claim.
    """
    valid_numbers = set(range(1, len(documents) + 1))
    cited_numbers: list[int] = []

    def replace(match: re.Match[str]) -> str:
        number = int(match.group(1))
        if number in valid_numbers:
            cited_numbers.append(number)
            return match.group(0)
        return ""

    cleaned = re.sub(r"\[(\d+)\]", replace, text).strip()
    if not cited_numbers:
        return SAFE_REFUSAL, []
    return cleaned, sorted(set(cited_numbers))
