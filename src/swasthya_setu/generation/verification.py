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
    "dose_refusal": {
        "en": "I cannot provide specific drug doses, dosing intervals, or medication schedules. Dosing requires individualized medical evaluation. Please consult a doctor, ASHA worker, or your nearest health centre.",
        "hi": "मैं दवा की विशिष्ट खुराक, समय या कार्यक्रम की सलाह नहीं दे सकता। खुराक के लिए डॉक्टर या स्वास्थ्यकर्मी द्वारा व्यक्तिगत जांच आवश्यक है। कृपया डॉक्टर, आशा कार्यकर्ता या स्वास्थ्य केंद्र से सलाह लें।",
    },
    "disclaimer": {
        "en": "Do not self-medicate. Please check with a doctor or health worker.",
        "hi": "खुद से दवा न लें। कृपया डॉक्टर या स्वास्थ्यकर्मी से सलाह लें।",
    },
    "awareness_closing": {
        "en": (
            "This is health awareness information, not medical advice. "
            "In an emergency, go to the nearest hospital or call 108."
        ),
        "hi": (
            "यह स्वास्थ्य जागरूकता की जानकारी है, चिकित्सा सलाह नहीं। "
            "आपातकाल में नजदीकी अस्पताल जाएँ या 108 पर कॉल करें।"
        ),
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

_NUMERIC_DOSE_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|µg|ml|iu|tablets?|capsules?|drops?)(?:/(?:kg|day|dose))?\b|"
    r"\b\d+\s*(?:to|-)\s*\d+\s*(?:mg|mcg|µg|ml|iu|tablets?|capsules?)\b|"
    r"\b(?:once|twice|thrice|\d+\s*times)\s+(?:daily|a\s+day|per\s+day)\b|"
    r"\bevery\s+\d+\s*(?:to\s*\d+\s*)?hours?\b|"
    r"\d+\s*(?:मिग्रा|एमजी|मिली|गोलियां|गोली|बूंद)",
    re.IGNORECASE,
)


def has_numeric_dose(text: str) -> bool:
    """Detect numeric doses, dosing intervals, tablet counts, or schedules."""
    return bool(_NUMERIC_DOSE_PATTERN.search(text))


def filter_dose_patterns(text: str, language: str = "en") -> tuple[str, bool]:
    """Deterministic post-generation safety filter blocking numeric doses.

    If blocked, returns the safe refusal message and False; otherwise returns the original text and True.
    """
    if has_numeric_dose(text):
        return localized_message("dose_refusal", language), False
    return text, True


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


def strip_generated_closing(text: str) -> str:
    """Remove model-written safety closings before adding the fixed version."""
    patterns = (
        r"(?is)\s*(?:this is health awareness information.*?call\s*108\.?)\s*$",
        r"(?is)\s*(?:यह स्वास्थ्य जागरूकता की जानकारी.*?108 पर कॉल करें।?)\s*$",
        r"(?is)\s*(?:do not self-medicate.*?(?:health worker|स्वास्थ्यकर्मी)।?)\s*$",
    )
    for pattern in patterns:
        text = re.sub(pattern, "", text).rstrip()
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
