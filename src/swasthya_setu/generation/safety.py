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
    "or": (
        "ଏହା ଏକ ଜରୁରୀକାଳୀନ ପରିସ୍ଥିତି ହୋଇପାରେ। ତୁରନ୍ତ ନିକଟତମ ଡାକ୍ତରଖାନାକୁ ଯାଆନ୍ତୁ କିମ୍ବା ୧୦୮ କୁ କଲ୍ କରନ୍ତୁ। "
        "ଅନଲାଇନ୍ ଉତ୍ତର ପାଇଁ ଅପେକ୍ଷା କରନ୍ତୁ ନାହିଁ।"
    ),
}

EMERGENCY_RESPONSE = EMERGENCY_RESPONSES["en"]


def emergency_response(language: str) -> str:
    """Return the emergency message in the user's language."""
    return EMERGENCY_RESPONSES.get(language, EMERGENCY_RESPONSES["en"])


_EDUCATIONAL_QUERY_PREFIX = re.compile(
    r"^(?:what\s+(?:are|is|causes|does)|how\s+(?:to\s+prevent|do\s+doctors|is|are|do)|can\s+|why\s+does|is\s+it\s+normal|"
    r"overview\s+of|tell\s+me\s+about|information\s+on\s+how|signs\s+and\s+symptoms\s+of|definition\s+of)\b|"
    r"^(?:क्या\s+होता\s+है|लक्षण\s+क्या\s+हैं|कारण\s+क्या\s+हैं|बचाव\s+कैसे\s+करें|जानकारी\s+दें|सांस फूलने के आम कारण)\b|"
    r".*(?:के क्या कारण|क्या लक्षण|क्या दिशा-निर्देश|क्या होते हैं|kya hote hain|kya lakshan hain)\??$",
    re.IGNORECASE,
)

_PAST_OR_RESOLVED_HISTORY = re.compile(
    r"\b(?:years?|months?)\s+ago\b|\b(?:fine now|resolved|recovered|past history|cured)\b",
    re.IGNORECASE,
)

_EMERGENCY_PATTERNS_EN = re.compile(
    r"\b("
    r"(?:heavy|severe|uncontrolled|profuse|continuous)\s+bleeding|"
    r"bleeding\s+(?:won't|does\s*not|cannot|isn't)\s+stop|"
    r"vomiting\s+(?:\w+\s+)?blood|blood\s+in\s+vomit|haematemesis|"
    r"coughing\s+(?:up\s+)?(?:\w+\s+){0,3}blood|"
    r"difficulty\s+breathing|cannot\s+breathe|can't\s+breathe|stopped\s+breathing|breathlessness|gasping\s+for\s+(?:air|breath)|struggling\s+to\s+breathe|"
    r"unconscious(?:ness)?|unresponsive|passed\s+out|collapsed|not\s+waking\s+up|loss\s+of\s+consciousness|"
    r"convulsions?|seizures?|status\s+epilepticus|continuous\s+fits?|"
    r"(?:severe|crushing|radiating)\s+(?:chest\s+pain|chest\s+pressure)|"
    r"chest\s+pain\s+(?:radiating|with\s+(?:sweat|nausea|shortness))|"
    r"face\s+droop(?:ing)?|slurred\s+speech|cannot\s+speak\s+or\s+move|"
    r"(?:baby|infant|newborn|child)\s+(?:has\s+stopped\s+breathing|is\s+(?:unresponsive|unconscious|very\s+lethargic|cold\s+to\s+touch)|lips\s+are\s+turning\s+blue|turning\s+blue|cyanosis|not\s+breathing\s+properly)|"
    r"(?:severe|unbearable|excruciating)\s+(?:\w+\s+)?(?:abdominal|belly|stomach)\s+pain|"
    r"swallowed\s+poison|poison\s+pesticide|foaming\s+at\s+(?:the\s+)?mouth|(?:venomous\s+)?snake\s*(?:bite|bit|bitten)"
    r")\b",
    re.IGNORECASE,
)

_EMERGENCY_PATTERNS_HI = re.compile(
    r"("
    r"खून की उल्टी|उल्टी में खून|बहुत ज्यादा खून|खून (?:का\s+)?बहना (?:बिल्कुल\s+)?(?:बंद नहीं|रुक नहीं)|रक्तस्राव नहीं रुक रहा|"
    r"सांस लेने में (?:बहुत\s+)?(?:दिक्कत|तकलीफ|परेशानी)|सांस फूल रही|सांस रुक गई|सांस नहीं आ रही|दम घुट रहा|"
    r"बेहोशी|बेहोश|होश खो दिया|चेतना नहीं है|जाग नहीं रहा|मूर्छित|"
    r"दौरे(?: पड़ रहे)?|दौरा पड़ गया|मिर्गी का दौरा|झटके आ रहे|"
    r"(?:सीने|छाती) में (?:बहुत\s+)?(?:तेज दर्द|असहनीय दर्द|दबाव)|"
    r"चेहरा टेढ़ा हो गया|बोल नहीं पा रहा|अंग काम नहीं कर रहा|लकवा का दौरा|"
    r"(?:बच्चा|शिशु|नवजात)\s+(?:सांस नहीं ले (?:रहा|पा रहा)|नीला पड़ गया|होश में नहीं है|बहुत गंभीर बीमार)|"
    r"पेट में (?:[\w\u0900-\u097f]+\s+)*(?:असहनीय|भयंकर|तेज)\s*दर्द|पेट में (?:बहुत|असहनीय|भयंकर)\s+(?:तेज\s+)?दर्द|"
    r"जहर पी लिया|कीटनाशक (?:निगल|पी) लिया|मुंह से झाग निकल|सांप ने काट लिया"
    r")",
)

_EMERGENCY_PATTERNS_HINGLISH = re.compile(
    r"\b("
    r"khoon ki ulti|ulti me(?:in)? khoon|khoon nikal raha|bleeding (?:nahi|ruk nahi|ruk)\s*rahi|bahut zyada khoon|"
    r"saans nahi aa rahi|saans lene me(?:in)? dikkat|saans phool rahi|dam ghut raha|saans ruk gayi|"
    r"behosh ho gaya|behoshi|hosh nahi hai|uth nahi raha|collapse ho gaya|"
    r"dourey? pad rahe|daura pad gaya|daure aa rahe|jhatke aa rahe|fits aa rahe|"
    r"(?:seene|chhati)\s*me(?:in)?\s+(?:bahut\s+)?(?:tej\s+|tez\s+)?dard|chest pain ho raha hai|"
    r"bachha saans nahi le raha|bachha behosh ho gaya|baby saans nahi le raha|bachha bahut bimar hai|"
    r"pet me(?:in)? (?:bahut\s+)?tez dard|zehar pee liya|poison pee liya|saanp ne kaat liya|zehar kha liya"
    r")\b",
    re.IGNORECASE,
)

_EMERGENCY_PATTERNS_ODIA = re.compile(
    r"(ରକ୍ତ ବାନ୍ତି|ଶ୍ୱାସ ନେବାରେ କଷ୍ଟ|ବେହୋସ|ଖିଚୁଣି|ଛାତିରେ ଭୀଷଣ ଯନ୍ତ୍ରଣା)",
)


def is_emergency(message: str) -> bool:
    """Return whether a message contains a high-confidence acute emergency signal."""
    msg = message.strip()
    if not msg:
        return False

    if _PAST_OR_RESOLVED_HISTORY.search(msg):
        return False

    is_educational = bool(_EDUCATIONAL_QUERY_PREFIX.search(msg))

    matched_patterns = []
    for pat in (_EMERGENCY_PATTERNS_EN, _EMERGENCY_PATTERNS_HI, _EMERGENCY_PATTERNS_HINGLISH, _EMERGENCY_PATTERNS_ODIA):
        m = pat.search(msg)
        if m:
            matched_patterns.append(m)

    if not matched_patterns:
        return False

    # Check if all matches are negated: e.g. "no bleeding and no chest pain" or "कोई उल्टी या बेहोशी नहीं है"
    has_unnegated_match = False
    for m in matched_patterns:
        start = m.start()
        end = m.end()
        prefix_window = msg[max(0, start - 25):start].lower()
        suffix_window = msg[end:min(len(msg), end + 25)].lower()
        is_negated = bool(
            re.search(r"\b(?:no|not|without|denies|neither|nor|nahin|nahi|नहीं|ना|कोई)\s*$", prefix_window)
            or re.search(r"^\s*[ी|े|ा|ों]*\s*(?:नहीं|ना|nahi|nahin)(?:\s|$)", suffix_window)
        )
        if not is_negated:
            has_unnegated_match = True
            break

    if not has_unnegated_match:
        return False

    # If it is framed as a purely educational question without first-person acute symptoms:
    # e.g. "What are the warning signs of dengue?" -> educational
    if is_educational:
        first_person_signals = re.compile(
            r"\b(?:my|i am|he is|she is|patient|baby|child|father|mother|right now|immediately|मेरा|मेरी|मेरे|मरीज|मरीज़|बच्चा)\b",
            re.IGNORECASE,
        )
        if not first_person_signals.search(msg):
            return False

    return True
