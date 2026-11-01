"""Deterministic safety checks that must run before any model call."""

import re

EMERGENCY_RESPONSE = (
    "This may be an emergency. Go to the nearest hospital immediately or call 108. "
    "Do not wait for an online answer."
)

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
        r"(खून की उल्टी|बहुत ज्यादा खून|सांस लेने में दिक्कत|बेहोश|दौरे|"
        r"बच्चा बहुत बीमार|सीने में तेज दर्द)",
    ),
    re.compile(
        r"(ରକ୍ତ ବାନ୍ତି|ଶ୍ୱାସ ନେବାରେ କଷ୍ଟ|ବେହୋସ|ଖିଚୁଣି)",
    ),
)


def is_emergency(message: str) -> bool:
    """Return whether a message contains a high-confidence emergency signal."""
    return any(pattern.search(message) for pattern in _EMERGENCY_PATTERNS)
