"""Post-generation checks for grounded responses."""

import re

from langchain_core.documents import Document

FIXED_MESSAGES = {
    "safe_refusal": {
        "en": "I do not have verified information on that. Please ask a doctor, ASHA worker or health centre.",
        "hi": "मेरे पास इसकी सत्यापित जानकारी नहीं है। कृपया डॉक्टर, आशा कार्यकर्ता या स्वास्थ्य केंद्र से पूछें।",
    },
    "prescription_refusal": {
        "en": "I cannot diagnose you or recommend medicines or doses. Please ask a doctor, ASHA worker or health centre.",
        "hi": "मैं आपका निदान नहीं कर सकता और दवा या खुराक की सलाह नहीं दे सकता। कृपया डॉक्टर, आशा कार्यकर्ता या स्वास्थ्य केंद्र से पूछें।",
    },
    "disclaimer": {
        "en": "Do not self-medicate. Please check with a doctor or health worker.",
        "hi": "खुद से दवा न लें। कृपया डॉक्टर या स्वास्थ्यकर्मी से सलाह लें।",
    },
}

SAFE_REFUSAL = FIXED_MESSAGES["safe_refusal"]["en"]
PRESCRIPTION_REFUSAL = FIXED_MESSAGES["prescription_refusal"]["en"]

_DEVANAGARI_RANGE = re.compile(r"[\u0900-\u097f]")
_ODIA_RANGE = re.compile(r"[\u0b00-\u0b7f]")
_LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z-]*")
_MIXED_SCRIPT_TOKEN = re.compile(r"\S*[\u0900-\u097f]\S*[A-Za-z]\S*|\S*[A-Za-z]\S*[\u0900-\u097f]\S*")
_MIXED_MEDICAL_TOKENS = {
    "सैलicylates": "salicylates",
}


def localized_message(message: str, language: str) -> str:
    """Return a fixed safety message in the requested language."""
    return FIXED_MESSAGES.get(message, FIXED_MESSAGES["safe_refusal"]).get(
        language, FIXED_MESSAGES[message]["en"]
    )


def is_language_consistent(
    text: str, language: str, context: str = ""
) -> bool:
    """Check script ratio while allowing cited Latin medical terms."""
    if _MIXED_SCRIPT_TOKEN.search(text):
        return False
    devanagari = len(_DEVANAGARI_RANGE.findall(text))
    odia = len(_ODIA_RANGE.findall(text))
    latin_text = text
    if context:
        context_terms = {
            term.lower() for term in _LATIN_WORD.findall(context) if len(term) > 1
        }
        latin_text = _LATIN_WORD.sub(
            lambda match: "" if match.group(0).lower() in context_terms else match.group(0),
            text,
        )
    latin = len(re.findall(r"[A-Za-z]", latin_text))
    if language == "hi":
        letters = devanagari + latin
        return bool(devanagari) and (not letters or devanagari / letters >= 0.35)
    if language == "or":
        letters = odia + latin
        return bool(odia) and (not letters or odia / letters >= 0.35)
    return devanagari == 0 and odia == 0


def normalize_mixed_script_tokens(text: str) -> str:
    """Replace known model-created mixed-script medical spellings."""
    for mixed, normalized in _MIXED_MEDICAL_TOKENS.items():
        text = re.sub(re.escape(mixed), normalized, text, flags=re.IGNORECASE)
    return text


def verify_citations(
    text: str, documents: list[Document], language: str = "en"
) -> tuple[str, list[int]]:
    """Keep only citations that refer to retrieved documents.

    An answer without a valid citation is replaced with the standard refusal so
    the model cannot turn a retrieval miss into an unsupported medical claim.
    """
    valid_numbers = set(range(1, len(documents) + 1))
    cited_numbers: list[int] = []

    def replace(match: re.Match[str]) -> str:
        numbers = [int(value) for value in re.findall(r"\d+", match.group(1))]
        valid = [number for number in numbers if number in valid_numbers]
        cited_numbers.extend(valid)
        return f"[{', '.join(str(number) for number in valid)}]" if valid else ""

    cleaned = re.sub(r"\[((?:\d+\s*,\s*)*\d+)\]", replace, text).strip()
    if not cited_numbers:
        return localized_message("safe_refusal", language), []
    return cleaned, sorted(set(cited_numbers))
