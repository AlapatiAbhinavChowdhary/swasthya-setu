"""Deterministic safety checks that must run before any model call."""

import re
from swasthya_setu.generation.triage_normalizer import normalize_triage_text, has_fuzzy_emergency

EMERGENCY_RESPONSES = {
    "en": (
        "This may be an emergency. Go to the nearest hospital immediately or call 108 or 112. "
        "Do not wait for an online answer."
    ),
    "hi": (
        "यह आपातकाल हो सकता है। तुरंत नजदीकी अस्पताल जाएँ या 108 या 112 पर कॉल करें। "
        "ऑनलाइन जवाब के लिए इंतजार न करें।"
    ),
    "or": (
        "ଏହା ଏକ ଜରୁରୀକାଳୀନ ପରିସ୍ଥିତି ହୋଇପାରେ। ତୁରନ୍ତ ନିକଟତମ ଡାକ୍ତରଖାନାକୁ ଯାଆନ୍ତୁ କିମ୍ବା ୧୦୮ ବା ୧୧୨ କୁ କଲ୍ କରନ୍ତୁ। "
        "ଅନଲାଇନ୍ ଉତ୍ତର ପାଇଁ ଅପେକ୍ଷା କରନ୍ତୁ ନାହିଁ।"
    ),
}

EMERGENCY_RESPONSE = EMERGENCY_RESPONSES["en"]


def emergency_response(language: str) -> str:
    """Return the emergency message in the user's language."""
    return EMERGENCY_RESPONSES.get(language, EMERGENCY_RESPONSES["en"])


_EDUCATIONAL_QUERY_PREFIX = re.compile(
    r"^(?:what\s+(?:are|is|causes|does)|how\s+(?:to\s+prevent|do\s+doctors|is|are|do|much|many|long)|can\s+|why\s+(?:should|does|is|are|do|would|not)?\s+|is\s+it\s+normal|"
    r"does\s+|do\s+|will\s+|would\s+|"
    r"educational\s+(?:info|information)\s+on|overview\s+of|tell\s+me\s+about|information\s+on\s+how|signs\s+and\s+symptoms\s+of|definition\s+of)\b|"
    r"^(?:क्या\s+होता\s+है|लक्षण\s+क्या\s+हैं|कारण\s+क्या\s+हैं|बचाव\s+कैसे\s+करें|जानकारी\s+दें|सांस फूलने के आम कारण)\b|"
    r".*(?:के क्या कारण|क्या लक्षण|क्या दिशा-निर्देश|क्या होते हैं|kya hote hain|kya lakshan hain)\??$",
    re.IGNORECASE,
)

_ACUTE_EMERGENCY_OVERRIDE = re.compile(
    r"\b("
    r"not\s+breathing|cannot\s+breathe|can't\s+breathe|stopped\s+breathing|"
    r"unconscious|unresponsive|convulsing|seizure|fits|"
    r"cyanosis|turning\s+blue|neela\s+pad|"
    r"drank\s+(?:phenyl|poison|cleaner|chemical|acid|pesticide)|swallowed\s+(?:poison|phenyl|cleaner|acid)|"
    r"(?:bitten|bit)\s+by\s+(?:a\s+)?snake|snake\s*bite\s+on|"
    r"vomiting\s+blood|coughing\s+(?:up\s+)?(?:\w+\s+){0,4}blood|khoon\s+ki\s+ulti|"
    r"behosh|saans\s+nahi\s+aa\s+rahi|keetnashak|zehar"
    r")\b|"
    r"(?:सांस\s+नहीं\s+ले\s+रहा|नीला\s+पड़\s+गया|नीला\s+पड़\s+रहा|बेहोश|दौरा\s+पड़|खून\s+की\s+उल्टी|कीटनाशक|जहर\s+पी|सांप\s+ने\s+काट)",
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
    r"soaked\s+\d+\s+pads|"
    r"vomit(?:t?ing|t?ed)?\s+(?:\w+\s+){0,4}blood|blood\s+in\s+vomit|haematemesis|"
    r"coughing\s+(?:up\s+)?(?:\w+\s+){0,6}blood|fresh\s+blood|"
    r"difficulty\s+breathing|cannot\s+breathe|can't\s+breathe|stopped\s+breathing|not\s+breathing|breathlessness|gasping\s+for\s+(?:air|breath)|struggling\s+to\s+breathe|"
    r"fell\s+in\s+(?:\w+\s+){0,3}water|bucket\s+of\s+water|drowning|drowned|"
    r"unconscious(?:ness)?|unresponsive|passed\s+out|collapsed|not\s+waking\s+up|loss\s+of\s+consciousness|cold\s+to\s+touch|"
    r"convulsions?|convulsing|seizures?|status\s+epilepticus|continuous\s+fits?|having\s+(?:\w+\s+){0,2}fits?|"
    r"(?:severe|crushing|radiating)\s+(?:chest\s+pain|chest\s+pressure)|"
    r"chest\s+(?:pressure|pain)\s+(?:sweating|and\s+sweating|with\s+sweat)|"
    r"chest\s+pain\s+(?:radiating|with\s+(?:sweat|nausea|shortness))|"
    r"face\s+droop(?:ing)?|slurred\s+speech|cannot\s+speak\s+or\s+move|sudden\s+weakness|sudden\s+paralysis|numbness\s+on\s+one\s+side|"
    r"(?:sudden\s+severe|severe\s+sudden)\s+head\s*ache|stiff\s+neck\s+(?:and|with)\s+vomiting|worst\s+pain\s+in\s+life|"
    r"(?:baby|infant|newborn|child)\s+(?:has\s+stopped\s+breathing|is\s+(?:unresponsive|unconscious|very\s+lethargic|cold\s+to\s+touch)|lips\s+are\s+turning\s+blue|turning\s+blue|cyanosis|not\s+breathing\s+properly|convulsing)|"
    r"lips\s+turning\s+blue|"
    r"(?:severe|unbearable|excruciating)\s+(?:\w+\s+)?(?:abdominal|belly|stomach)\s+pain|"
    r"(?:swallowed|drank|ingested|consumed)\s+(?:\w+\s+){0,4}(?:poison|cleaner|chemical|acid|phenyl|toilet\s+cleaner|pesticide)|"
    r"poison\s+pesticide|foaming\s+at\s+(?:the\s+)?mouth|(?:venomous\s+|poisonous\s+)?(?:snake|cobra|krait|viper)\s*(?:bite|bit|bitten)(?!\s+(?:antivenom|first\s+aid|management|prevention|guideline))|"
    r"(?:heavy\s+bleeding|severe\s+bleeding|hemorrhage|haemorrhage)\s+after\s+delivery"
    r")\b",
    re.IGNORECASE,
)

_EMERGENCY_PATTERNS_HI = re.compile(
    r"("
    r"खून की उल्टी|खून की उल्टियां|उल्टी में खून|बहुत ज्यादा खून|खून (?:का\s+)?बहना (?:बिल्कुल\s+)?(?:बंद नहीं|रुक नहीं)|खून बह रहा है रुक नहीं|रक्तस्राव नहीं रुक रहा|अधिक रक्तस्राव|भारी रक्तस्राव|"
    r"सांस लेने में (?:बहुत\s+)?(?:दिक्कत|तकलीफ|परेशानी|तड़प)|सांस फूल रही|सांस रुक गई|सांस नहीं (?:आ रही|ले रहा)|दम घुट रहा|नीला पड़ रहा|"
    r"बेहोशी|बेहोश|होश खो दिया|चेतना नहीं है|जाग नहीं रहा|मूर्छित|नाड़ी नहीं मिल रही|पल्स नहीं|"
    r"दौरे(?: पड़ रहे)?|दौरा पड़ गया|मिर्गी का दौरा|झटके (?:आ रहे|आने लगे|पड़ रहे)|जबड़ा भिंच गया|आंखें उलट|"
    r"(?:सीने|छाती) में (?:बहुत\s+)?(?:तेज दर्द|असहनीय दर्द|दबाव|तेज चुभन)|सीने में .* पसीना|"
    r"चेहरा टेढ़ा हो गया|बोल नहीं पा रहा|अंग काम नहीं कर रहा|लकवा का दौरा|आधा शरीर सुन्न|आवाज बंद हो गई|"
    r"गर्दन अकड़|गर्दन में अकड़न|"
    r"(?:बच्चा|शिशु|नवजात)\s+(?:सांस नहीं ले (?:रहा|पा रहा)|नीला पड़ (?:गया|रहा)|होश में नहीं है|बहुत गंभीर बीमार)|"
    r"पेट में (?:[\w\u0900-\u097f]+\s+)*(?:असहनीय|भयंकर|तेज)\s*दर्द|पेट में (?:बहुत|असहनीय|भयंकर)\s+(?:तेज\s+)?दर्द|"
    r"जहर पी लिया|कीटनाशक (?:दवा\s+)?(?:निगल|पी|खा)\s*(?:ली|लिया|गया|है)|मुंह से झाग निकल|सांप ने (?:[\w\u0900-\u097f]+\s+){0,3}(?:काट|डस)\s*लिया|डस लिया|डस गया|प्रसव के (?:तुरंत\s+)?बाद .* (?:रक्तस्राव|खून)"
    r")",
)

_EMERGENCY_PATTERNS_HINGLISH = re.compile(
    r"\b("
    r"khoon ki ulti|ulti me(?:in)? khoon|khoon nikal raha|bleeding (?:nahi|ruk nahi|ruk)\s*rahi|bahut zyada khoon|khoon behna ruk nahi rha|heavy bleeding|"
    r"saans (?:nahi|nhi) (?:aa|le) (?:raha|rha|rahi|rhi)|saans lene me(?:in)? (?:bhut\s+|bahut\s+)?dikkat|saans phool rahi|dam ghut raha|saans ruk gayi|saans band|saans bilkul atak|bol (?:b\s+|bhi\s+)?ni pa rhe|blue ho gya|neela pd gya|"
    r"behosh ho gaya|behoshi|behosh pde|behosh|hosh nahi hai|uth (?:hi\s+)?nahi raha|collapse ho gaya|body cold ho gyi|naadi nahi|nadi nahi|"
    r"dourey? pad rahe|daura pad gaya|daure aa rahe|jhatke aa rahe|fits (?:padne|aa|pad) rahe|fits padne lge|"
    r"(?:seene|chhati|chest)\s*me(?:in)?\s+(?:bahut\s+|severe\s+)?(?:tej\s+|tez\s+|severe\s+)?dard|chest me severe dard|chest pain ho raha hai|"
    r"face (?:ek taraf )?tedha|hath kaam ni kr|haath kaam nahi|"
    r"bachha saans nahi le raha|bachha behosh ho gaya|baby saans nahi le raha|bachha bahut bimar hai|"
    r"pet me(?:in)? (?:bahut\s+)?tez dard|zehar pee liya|poison pee liya|cleaner phenyl|floor cleaner|phenyl pee liya|saanp ne kaat liya|keetnashak pee liya|jahar fail rha|heavy bleeding ho rhi|"
    r"delivery k baad .* (?:blood|khoon)|doob gya"
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

    norm = normalize_triage_text(msg)
    if not norm:
        return False

    if _PAST_OR_RESOLVED_HISTORY.search(norm):
        return False

    is_educational = bool(_EDUCATIONAL_QUERY_PREFIX.search(norm))
    has_acute_override = bool(_ACUTE_EMERGENCY_OVERRIDE.search(norm))

    matched_patterns = []
    for pat in (_EMERGENCY_PATTERNS_EN, _EMERGENCY_PATTERNS_HI, _EMERGENCY_PATTERNS_HINGLISH, _EMERGENCY_PATTERNS_ODIA):
        m = pat.search(norm)
        if m:
            matched_patterns.append(m)

    if not matched_patterns and not has_fuzzy_emergency(norm):
        return False

    # Check if all matches are negated: e.g. "no bleeding and no chest pain" or "कोई उल्टी या बेहोशी नहीं है"
    has_unnegated_match = False
    if matched_patterns:
        for m in matched_patterns:
            start = m.start()
            end = m.end()
            prefix_window = norm[max(0, start - 25):start].lower()
            suffix_window = norm[end:min(len(norm), end + 25)].lower()
            is_negated = bool(
                re.search(r"\b(?:no|not|without|denies|neither|nor|nahin|nahi|नहीं|ना|कोई)\s*$", prefix_window)
                or re.search(r"^\s*[ी|े|ा|ों]*\s*(?:नहीं|ना|nahi|nahin)(?:\s|$)", suffix_window)
            )
            if not is_negated:
                has_unnegated_match = True
                break
    else:
        # Fuzzy match path
        has_unnegated_match = True

    if not has_unnegated_match:
        return False

    # Guard for educational questions mentioning paralysis in polio/vaccines without acute stroke signals
    if re.search(r"\b(?:polio|vaccin|immuniz)\b", norm, re.IGNORECASE) and not has_acute_override:
        acute_stroke_signal = re.compile(
            r"\b(?:sudden|slurred|droop|stroke|right\s+now|attack|tedha|suun|sunn|paralysis\s+right\s+now)\b",
            re.IGNORECASE,
        )
        if not acute_stroke_signal.search(norm):
            return False

    # Guard for non-emergency sentences asking about definition or causes of behoshi/fainting
    if re.search(r"\b(?:causes?|meaning|definition|what\s+is|reason|karan|arth|kya\s+hai)\b", norm, re.IGNORECASE) and not has_acute_override:
        first_person_signals = re.compile(
            r"\b(?:my|i am|he is|she is|patient|baby|child|father|mother|mera|meri|mere|bache|bacha|papa|maa|मेरा|मेरी|मेरे|मरीज|मरीज़|बच्चा)\b",
            re.IGNORECASE,
        )
        if not first_person_signals.search(norm) and not re.search(r"\b(?:right\s+now|turant|immediately|abhi)\b", norm, re.IGNORECASE):
            return False

    # If it is framed as a purely educational question without acute symptoms:
    # e.g. "What are the warning signs of dengue?" -> educational
    if is_educational and not has_acute_override:
        first_person_signals = re.compile(
            r"\b(?:my|i am|he is|she is|patient|baby|child|father|mother|someone|person|right now|immediately|mera|meri|mere|bache|bacha|papa|maa|bhai|bhaiya|uncle|मेरा|मेरी|मेरे|मरीज|मरीज़|बच्चा)\b",
            re.IGNORECASE,
        )
        if not first_person_signals.search(norm):
            return False

    return True
