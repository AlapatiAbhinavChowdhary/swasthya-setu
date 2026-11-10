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
            "In an emergency, go to the nearest hospital or call 108 or 112."
        ),
        "hi": (
            "यह स्वास्थ्य जागरूकता की जानकारी है, चिकित्सा सलाह नहीं। "
            "आपातकाल में नजदीकी अस्पताल जाएँ या 108 या 112 पर कॉल करें।"
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
    r"\b\d+(?:\.\d+)?(?:\s*(?:to|-)\s*\d+(?:\.\d+)?)?\s*(?:ml|milliliters?|millilitres?)\s*(?:/|per)\s*kg\b|"
    r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|µg|iu|tablets?|capsules?|vials?|ampoules?)(?:/(?:kg|day|dose))?\b|"
    r"\b\d+\s*(?:to|-)\s*\d+\s*(?:mg|mcg|µg|iu|tablets?|capsules?|vials?|ampoules?)\b|"
    r"\b\d+(?:\.\d+)?\s*(?:vials?|ampoules?|bottles?|units?)\s*(?:of\s+)?(?:antivenom|asv|anti-snake\s*venom)\b|"
    r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|tablets?|ml)\s*(?:of\s+)?zinc\b|"
    r"\b(?:once|twice|thrice|\d+\s*times)\s+(?:daily|a\s+day|per\s+day)\b|"
    r"\bevery\s+\d+\s*(?:to\s*\d+\s*)?hours?\b|"
    r"\d+\s*(?:मिली|एमएल|मिलीलीटर)\s*(?:/|प्रति)\s*(?:किग्रा|किलो|kg)|"
    r"\d+\s*(?:शीशी|शीशियां|वायल|वायल्स|vials?)\s*(?:एंटीवेनम|एएसवी)|"
    r"\d+\s*(?:मिग्रा|एमजी|गोलियां|गोली)\s*(?:जिंक)?|"
    r"\b\d+(?:\.\d+)?\s*(?:drops?)\b|"
    r"\b\d+(?:\.\d+)?\s*(?:to|-)\s*\d+\s*(?:drops?)\b|"
    r"\b\d+(?:\.\d+)?\s*(?:ml|milliliters?|millilitres?)\b(?!\s*(?:\([^)]*\)\s*)?(?:of\s+)?(?:clean\s+|drinking\s+|safe\s+|boiled\s+|potable\s+|fresh\s+|prepared\s+|cool(?:ed)?\s+|lukewarm\s+)*(?:water|ors|solution|liquid|fluid|fluids|drink))\b|"
    r"\d+\s*(?:मिली|एमएल|मिलीलीटर)(?![\s\w\u0900-\u097f]*(?:पानी|जल|ओआरएस|घोल|तरल))",
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


_PRESCRIPTION_LEAK_DRUGS = re.compile(
    r"\b("
    r"paracetamol|crocin|calpol|ibuprofen|combiflam|aspirin|disprin|"
    r"azithromycin|amoxicillin|ciprofloxacin|doxycycline|metronidazole|"
    r"chloroquine|artesunate|artemether|lumefantrine|"
    r"cetirizine|allegra|montelukast|cough\s+syrup|antibiotic"
    r")\b",
    re.IGNORECASE,
)

_PRESCRIPTION_LEAK_ADVICE = re.compile(
    r"\b("
    r"you\s+should\s+take|i\s+recommend(?:\s+taking)?|take\s+(?:the\s+following|\d+|this)\s+(?:medicine|tablet|drug)|"
    r"you\s+can\s+take|you\s+may\s+take|start\s+taking|"
    r"give\s+(?:the\s+child|him|her)\s+\w+|"
    r"aapko\s+.*leni\s+chahiye|aap\s+.*len|आप\s+.*लें|आपको\s+.*लेनी\s+चाहिए"
    r")\b",
    re.IGNORECASE,
)


def check_post_generation_prescription_leak(
    question: str, answer: str, language: str = "en"
) -> tuple[str, bool]:
    """Post-generation safety net:

    If the user's question asks what to take/give, and the generated answer
    names a specific drug with a quantity or frequency, or says 'you should take / I recommend',
    replace the answer with the prescription refusal before returning to the user.
    Legitimate awareness answers (e.g. dengue avoid aspirin, TB 6 months duration) are kept.
    """
    from swasthya_setu.generation.triage_normalizer import normalize_triage_text

    norm_q = normalize_triage_text(question)

    # Check if question asks what to take/give for personal treatment
    asks_what_to_take = bool(
        re.search(
            r"\b(what\s+(?:medicine|tablet|drug|syrup)?\s*(?:should|can)\s*i\s*(?:take|give)|"
            r"which\s+(?:medicine|tablet|drug|syrup)\s*(?:should|can)\s*i\s*(?:take|give)|"
            r"kya\s*(?:dawai|tablet|medicine)\s*(?:lu|loon|khaun|du|doon)|"
            r"konsi\s*(?:dawai|tablet|goli|medicine)\s*(?:lu|khaun|du|deni)|"
            r"kaunsi\s*(?:dawai|tablet|goli|medicine)\s*(?:lu|khaun|du|deni)|"
            r"कौन\s*सी\s*(?:दवा|गोली|सिरप)\s*(?:लूँ|लूं|खानी|दूँ|दू)|"
            r"क्या\s*(?:दवा|गोली)\s*(?:लूँ|लूं|खानी|दूँ|दू))\b",
            norm_q,
            re.IGNORECASE,
        )
    )

    if not asks_what_to_take:
        return answer, True

    has_advice = bool(_PRESCRIPTION_LEAK_ADVICE.search(answer))
    has_drug_with_freq = bool(
        _PRESCRIPTION_LEAK_DRUGS.search(answer)
        and (
            has_numeric_dose(answer)
            or re.search(
                r"\b(?:once|twice|thrice|\d+\s*times)\s+(?:daily|a\s+day)|every\s+\d+\s*hours|\bदिन\s*में\s*(?:एक|दो|तीन|\d+)\s*बार\b",
                answer,
                re.IGNORECASE,
            )
        )
    )

    if has_advice or has_drug_with_freq:
        return localized_message("prescription_refusal", language), False

    return answer, True


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
        r"(?is)\s*(?:this is health awareness information.*?(?:call\s*(?:108|112)(?:\s*(?:or|and)\s*(?:108|112))?)\.?)\s*$",
        r"(?is)\s*(?:यह स्वास्थ्य जागरूकता की जानकारी.*?(?:108|112)(?:\s*(?:या|और)\s*(?:108|112))?\s*पर कॉल करें।?)\s*$",
        r"(?is)\s*(?:do not self-medicate.*?(?:health worker|स्वास्थ्यकर्मी)।?)\s*$",
    )
    for pattern in patterns:
        text = re.sub(pattern, "", text).rstrip()
    return text


_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "are", "have", "been",
    "will", "can", "also", "under", "treatment", "disease", "health", "used",
    "which", "such", "than", "they", "were", "what", "when", "where", "who", "your",
    "should", "take", "give", "people", "child", "more", "most", "about",
    "का", "के", "की", "में", "से", "है", "हैं", "पर", "और", "को", "या", "भी", "किया", "जाता"
}


def is_chunk_supporting_sentence(sentence: str, doc: Document) -> bool:
    """Check if document chunk provides lexical support for the sentence's key claims."""
    if len(doc.page_content.strip()) < 30:
        return True

    doc_text = doc.page_content.lower()

    # Acronyms (e.g. RNTCP, NTEP, DOTS) in the sentence must exist in the cited doc
    acronyms = re.findall(r"\b[A-Z]{2,}\b", sentence)
    for ac in acronyms:
        if ac in {"WHO", "TB", "HIV", "ORS", "IV", "MR", "JE", "OPV", "IPV", "DPT"}:
            continue
        if ac.lower() not in doc_text:
            return False

    # Check multi-word proper title (e.g. "Revised National Tuberculosis Control Program")
    title_phrases = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,}\b", sentence)
    for phrase in title_phrases:
        if phrase.lower() not in doc_text:
            return False

    # Check Latin words if present
    latin_words = [w for w in re.findall(r"\b[a-z]{3,}\b", sentence.lower()) if w not in _STOPWORDS]
    if latin_words and len(latin_words) >= 4:
        matches = sum(1 for w in latin_words if w in doc_text)
        if matches == 0:
            return False

    # For English sentences without non-Latin scripts, check English content word overlap
    is_non_latin = any(ord(c) >= 0x0900 for c in sentence)
    if not is_non_latin:
        words = re.findall(r"\b[a-z0-9\-]{3,}\b", sentence.lower())
        content_words = [w for w in words if w not in _STOPWORDS]
        if len(content_words) >= 4:
            matches = sum(1 for w in content_words if w in doc_text)
            if matches / len(content_words) < 0.20:
                return False

    return True


def verify_citations(
    text: str,
    documents: list[Document],
    language: str = "en",
    asked_diseases: list[str] | None = None,
) -> tuple[str, list[int]]:
    """Keep only citations that refer to and are supported by retrieved documents.

    An answer without a valid citation is replaced with the standard refusal so
    the model cannot turn a retrieval miss into an unsupported medical claim.
    If asked_diseases is specified, cross-disease documents from other diseases
    are strictly rejected.
    """
    valid_numbers = set(range(1, len(documents) + 1))
    if asked_diseases:
        asked_set = set(asked_diseases)
        disease_allowed_numbers = set()
        for idx, doc in enumerate(documents, start=1):
            raw_ids = doc.metadata.get("disease_ids", "")
            doc_diseases = {d.strip() for d in raw_ids.split(",") if d.strip()}
            if not doc_diseases or doc_diseases.intersection(asked_set):
                disease_allowed_numbers.add(idx)
        valid_numbers = valid_numbers.intersection(disease_allowed_numbers)
    cited_numbers: list[int] = []

    lines = text.split("\n")
    cleaned_lines: list[str] = []

    for line in lines:
        if not line.strip():
            cleaned_lines.append(line)
            continue

        # Split line into sentences preserving bullet prefixes
        prefix = ""
        bullet_match = re.match(r"^(\s*[-*•]\s+)", line)
        content_line = line
        if bullet_match:
            prefix = bullet_match.group(1)
            content_line = line[len(prefix):]

        sentences = re.split(r"(?<=[.!?।])\s+", content_line)
        kept_sentences: list[str] = []

        for sent in sentences:
            if not sent.strip():
                continue
            had_citation = bool(re.search(r"\[((?:\d+\s*,\s*)*\d+)\]", sent))

            def replace_cite(match: re.Match[str]) -> str:
                raw_nums = [int(v) for v in re.findall(r"\d+", match.group(1))]
                clean_sentence = re.sub(r"\[(?:\d+\s*,\s*)*\d+\]", "", sent).strip()

                supported = []
                for num in raw_nums:
                    if num in valid_numbers:
                        if is_chunk_supporting_sentence(clean_sentence, documents[num - 1]):
                            supported.append(num)
                            cited_numbers.append(num)

                return f"[{', '.join(str(n) for n in supported)}]" if supported else ""

            new_sent = re.sub(r"\[((?:\d+\s*,\s*)*\d+)\]", replace_cite, sent)
            has_cite_now = bool(re.search(r"\[((?:\d+\s*,\s*)*\d+)\]", new_sent))

            # If the sentence had a citation but ALL citations were dropped/unsupported,
            # drop this unsupported sentence
            if had_citation and not has_cite_now:
                continue

            new_sent = re.sub(r"[ \t]{2,}", " ", new_sent).strip()
            if new_sent:
                kept_sentences.append(new_sent)

        if kept_sentences:
            full_line = (prefix + " ".join(kept_sentences)).strip()
            if full_line and full_line != prefix.strip():
                cleaned_lines.append(full_line)

    cleaned = "\n".join(cleaned_lines).strip()
    if not cited_numbers:
        return localized_message("safe_refusal", language), []
    return cleaned, sorted(set(cited_numbers))
