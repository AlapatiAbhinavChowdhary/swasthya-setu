"""Deterministic safety checks that must run before any model call."""

import re

EMERGENCY_RESPONSES = {
    "en": (
    "This may be an emergency. Go to the nearest hospital immediately or call 108. "
    "Do not wait for an online answer."
    ),
    "hi": (
        "यह आपातकाल हो सकता है। तुरंत नजदीकी अस्पताल जाएँ या 108 पर कॉल करें। "
        "ऑनलाइन जवाब के लिए इंतजार न करें।"
    ),
}


def emergency_response(language: str) -> str:
    """Return the emergency message in the user's language."""
    return EMERGENCY_RESPONSES.get(language, EMERGENCY_RESPONSES["en"])


EMERGENCY_RESPONSE = EMERGENCY_RESPONSES["en"]

_EMERGENCY_PATTERNS = (
    re.compile(
        r"\b("
        r"heavy bleeding|vomiting blood|blood in vomit|difficulty breathing|"
        r"cannot breathe|can't breathe|unconscious|not responding|convulsion|"
        r"seizure|very sick child|child is very ill|severe chest pain"
        r")\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(खून की उल्टी|उल्टी में खून|बहुत ज्यादा खून|सांस लेने में (?:दिक्कत|तकलीफ)|बेहोश|दौरे|"
        r"बच्चा बहुत बीमार|सीने में तेज दर्द)",
    ),
    re.compile(
        r"(ରକ୍ତ ବାନ୍ତି|ଶ୍ୱାସ ନେବାରେ କଷ୍ଟ|ବେହୋସ|ଖିଚୁଣି)",
    ),
)


def is_emergency(message: str) -> bool:
    """Return whether a message contains a high-confidence emergency signal."""
    return any(pattern.search(message) for pattern in _EMERGENCY_PATTERNS)
