"""Triage normalization and fuzzy lexicon matching for safety-critical queries.

Provides Unicode normalization, character repeat collapsing, typo mapping,
and fuzzy matching for English, Hindi, and Hinglish emergency & prescription queries.
"""

from __future__ import annotations

import re
import unicodedata
from rapidfuzz.distance import Levenshtein

# Common typos and SMS spellings mapped to canonical forms
_TYPO_MAP: dict[str, str] = {
    # English typos
    "unconsious": "unconscious",
    "unconcious": "unconscious",
    "unconshus": "unconscious",
    "unconciouss": "unconscious",
    "inconscious": "unconscious",
    "unresponcive": "unresponsive",
    "blud": "blood",
    "bloood": "blood",
    "bleding": "bleeding",
    "bled": "bleeding",
    "bleading": "bleeding",
    "brething": "breathing",
    "breathe": "breathing",
    "breth": "breathing",
    "breathlessnes": "breathlessness",
    "breathless": "breathlessness",
    "sizure": "seizure",
    "seisure": "seizure",
    "conwulsion": "convulsion",
    "convulshun": "convulsion",
    "hart": "heart",
    "hearth": "heart",
    "poisn": "poison",
    "posion": "poison",
    "posining": "poisoning",
    "posened": "poisoned",
    "drowing": "drowning",
    "drownd": "drowning",
    "hedache": "headache",
    "head ache": "headache",
    "swetting": "sweating",
    "diziness": "dizziness",
    "vomitted": "vomited",
    "sholder": "shoulder",
    "crushng": "crushing",
    "plz": "please",
    # Hinglish & Hindi transliteration typos and SMS shorthand
    "nhi": "nahi",
    "ni": "nahi",
    "rha": "raha",
    "rhi": "rahi",
    "rhe": "rahe",
    "pd": "pad",
    "gya": "gaya",
    "gyi": "gayi",
    "gye": "gaye",
    "keetnashk": "keetnashak",
    "kitnashk": "keetnashak",
    "kitnashak": "keetnashak",
    "keetanashak": "keetnashak",
    "behoshh": "behosh",
    "behos": "behosh",
    "sans": "saans",
    "saas": "saans",
    "chaati": "chhati",
    "sine": "seena",
    "drd": "dard",
    "nila": "neela",
    "jahar": "zehar",
    "zehr": "zehar",
    "saap": "saanp",
    "sarp": "saanp",
    "dawaii": "dawai",
    "dawae": "dawai",
    "goliya": "goliyan",
    "ktna": "kitna",
    "ktni": "kitni",
    "btao": "batao",
    "btado": "batao",
    "serap": "syrup",
    "seerup": "syrup",
    "bachhe": "bache",
    "bachha": "bacha",
    "chota": "chhota",
    "choti": "chhoti",
    "bukhr": "bukhar",
}

# Regex to collapse 3+ repeated characters down to 2: e.g. "heeeelp" -> "help", "saaaans" -> "saans"
_REPEAT_PATTERN = re.compile(r"(.)\1{2,}")


def normalize_triage_text(text: str) -> str:
    """Normalize text by lowering, NFC normalizing, collapsing repeated chars and mapping typos."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text).lower()
    # Collapse 3+ repeats: e.g. "heeeelp" -> "help", "saaaans" -> "saans"
    text = _REPEAT_PATTERN.sub(r"\1\1", text)
    # Collapse spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Split into tokens and replace known typos
    tokens = text.split(" ")
    replaced = []
    for t in tokens:
        clean_t = re.sub(r"[^\w\u0900-\u097f]", "", t)
        if clean_t in _TYPO_MAP:
            replaced.append(_TYPO_MAP[clean_t])
        else:
            replaced.append(t)
    return " ".join(replaced)


# Lexicon of critical emergency words for fuzzy matching
# Token-level Levenshtein check: len >= 5 allows dist <= 1; len >= 8 allows dist <= 2
_EMERGENCY_FUZZY_TARGETS = {
    "unconscious",
    "unresponsive",
    "convulsion",
    "convulsions",
    "convulsing",
    "breathlessness",
    "suffocating",
    "cyanosis",
    "pesticide",
    "poisoning",
    "paralysis",
    "haematemesis",
    "keetnashak",
    "behoshi",
    "behosh",
}


def fuzzy_match_emergency_token(token: str) -> bool:
    """Return True if token fuzzy matches an emergency keyword."""
    clean = re.sub(r"[^\w]", "", token.lower())
    n = len(clean)
    if n < 5:
        return False
    for target in _EMERGENCY_FUZZY_TARGETS:
        dist = Levenshtein.distance(clean, target)
        if n >= 8 and len(target) >= 8:
            if dist <= 2:
                return True
        elif dist <= 1:
            return True
    return False


def has_fuzzy_emergency(text: str) -> bool:
    """Check if any token in normalized text fuzzy-matches emergency keywords."""
    norm = normalize_triage_text(text)
    for token in norm.split():
        if fuzzy_match_emergency_token(token):
            return True
    return False
