"""Deterministic disease detection and cross-disease document filtering.

Ensures that retrieval and answers for a specific disease (e.g. tuberculosis)
never incorporate or cite documents from an unrelated disease (e.g. Japanese encephalitis).
"""

from __future__ import annotations

import re
from typing import Any
from langchain_core.documents import Document

DISEASE_PATTERNS: dict[str, list[str]] = {
    "tuberculosis": [
        r"\btb\b", r"\btuberculosis\b", r"\bphthisis\b",
        r"टीबी", r"क्षय रोग", r"तपेदिक", r"राजयक्ष्मा", r"यक्ष्मा",
    ],
    "dengue": [
        r"\bdengue\b", r"\bbreakbone\b", r"डेंगू", r"हड्डी तोड़ बुखार",
    ],
    "malaria": [
        r"\bmalaria\b", r"\bplasmodium\b", r"मलेरिया",
    ],
    "chikungunya": [
        r"\bchikungunya\b", r"चिकनगुनिया",
    ],
    "japanese-encephalitis": [
        r"\bjapanese encephalitis\b", r"\bencephalitis\b", r"\bacute encephalitis\b",
        r"जापानी इंसेफेलाइटिस", r"दिमागी बुखार", r"मस्तिष्क शोथ",
    ],
    "kala-azar": [
        r"\bkala-?azar\b", r"\bleishmaniasis\b", r"\bblack fever\b",
        r"काला-?आजार", r"कालाजार",
    ],
    "lymphatic-filariasis": [
        r"\blymphatic filariasis\b", r"\bfilariasis\b", r"\belephantiasis\b",
        r"लिम्फेटिक फाइलेरियासिस", r"फाइलेरिया", r"हाथीपांव", r"फीलपांव",
    ],
    "typhoid": [
        r"\btyphoid\b", r"\benteric fever\b", r"\bsalmonella typhi\b",
        r"टाइफाइड", r"मोतीझरा", r"मियादी बुखार",
    ],
    "cholera": [
        r"\bcholera\b", r"\bvibrio cholerae\b", r"हैजा", r"कालरा",
    ],
    "diarrhoeal-disease": [
        r"\bdiarrhoe?a\b", r"\bors\b", r"\boral rehydration\b", r"\bloose motion\b",
        r"दस्त", r"ओआरएस", r"अतिसार", r"पतले दस्त",
    ],
    "hepatitis-a": [
        r"\bhepatitis a\b", r"\bhav\b", r"हेपेटाइटिस ए",
    ],
    "hepatitis-b": [
        r"\bhepatitis b\b", r"\bhbv\b", r"हेपेटाइटिस बी",
    ],
    "hepatitis-e": [
        r"\bhepatitis e\b", r"\bhev\b", r"हेपेटाइटिस ई",
    ],
    "seasonal-influenza": [
        r"\binfluenza\b", r"\bh1n1\b", r"\bflu\b", r"\bswine flu\b",
        r"इन्फ्लुएंजा", r"फ्लू", r"स्वाइन फ्लू",
    ],
    "covid-19": [
        r"\bcovid(?:-19)?\b", r"\bcoronavirus\b", r"\bsars-cov-2\b",
        r"कोविड(?:-19)?", r"कोरोना वायरस", r"कोरोना",
    ],
    "measles": [
        r"\bmeasles\b", r"\brubella\b", r"\bmr vaccine\b", r"खसरा", r"रुबेला",
    ],
    "polio": [
        r"\bpolio(?:myelitis)?\b", r"\bopv\b", r"\bipv\b", r"पोलियो",
    ],
    "diphtheria-pertussis-tetanus": [
        r"\bdiphtheria\b", r"\bpertussis\b", r"\btetanus\b", r"\bdpt\b",
        r"\bwhooping cough\b", r"\blockjaw\b",
        r"डिप्थीरिया", r"काली खांसी", r"टिटनेस", r"धनुस्तंभ",
    ],
    "rabies-animal-bites": [
        r"\brabies\b", r"\bdog bite\b", r"\banimal bite\b", r"\bhydrophobia\b",
        r"रेबीज", r"कुत्ते का काटना", r"पशु का काटना", r"जलभय",
    ],
    "snakebite": [
        r"\bsnake ?bite\b", r"\bvenomous snake\b", r"\bsnake envenomation\b",
        r"सांप का काटना", r"सर्पदंश", r"सांप",
    ],
    "leprosy": [
        r"\bleprosy\b", r"\bhansen'?s disease\b", r"कुष्ठ रोग", r"कुष्ठ", r"कोढ़",
    ],
    "hiv-aids": [
        r"\bhiv\b", r"\baids\b", r"एचआईवी", r"एड्स",
    ],
    "diabetes": [
        r"\bdiabetes\b", r"\bblood sugar\b", r"\bhyperglycemia\b",
        r"मधुमेह", r"डायबिटीज", r"शुगर",
    ],
    "hypertension": [
        r"\bhypertension\b", r"\bhigh blood pressure\b", r"\bhigh bp\b",
        r"उच्च रक्तचाप", r"हाई बीपी", r"ब्लड प्रेशर",
    ],
    "anaemia-nutrition": [
        r"\bana?emia\b", r"\biron deficiency\b", r"\bmalnutrition\b",
        r"एनीमिया", r"खून की कमी", r"कुपोषण",
    ],
    "maternal-newborn-care": [
        r"\bmaternal\b", r"\bpregnancy\b", r"\bantenatal\b", r"\bpostnatal\b",
        r"\bbreastfeeding\b", r"\bnewborn care\b",
        r"गर्भावस्था", r"प्रसव", r"नवजात देखभाल", r"स्तनपान", r"धात्री",
    ],
    "child-immunization": [
        r"\bimmuniz(?:ation|ed|ing)\b", r"\bvaccin(?:ation|e|ated|ing)\b",
        r"टीकाकरण", r"टीका", r"प्रतिरक्षण",
    ],
    "heat-illness": [
        r"\bheat stroke\b", r"\bheat exhaustion\b", r"\bsunstroke\b",
        r"लू लगना", r"गर्मी से बीमारी", r"लू",
    ],
    "mental-health-basics": [
        r"\bmental health\b", r"\bdepression\b", r"\banxiety\b",
        r"मानसिक स्वास्थ्य", r"तनाव", r"अवसाद", r"चिंता",
    ],
    "hygiene-sanitation-safe-water": [
        r"\bhandwashing\b", r"\bhand hygiene\b", r"\bsafe drinking water\b",
        r"\bsanitation\b", r"हाथ धोना", r"स्वच्छता", r"साफ पीने का पानी",
    ],
}


def detect_asked_diseases(text: str) -> list[str]:
    """Identify diseases explicitly referenced in the user's query."""
    text_lower = text.lower()
    matched = []
    for disease_id, patterns in DISEASE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_lower, re.IGNORECASE):
                matched.append(disease_id)
                break
    return matched


def filter_cross_disease_documents(
    matches: list[tuple[Document, float]], asked_diseases: list[str]
) -> list[tuple[Document, float]]:
    """Drop documents tagged strictly with other diseases when a specific disease is asked."""
    if not asked_diseases:
        return matches

    asked_set = set(asked_diseases)
    filtered: list[tuple[Document, float]] = []

    for doc, score in matches:
        raw_ids = doc.metadata.get("disease_ids", "")
        doc_diseases = {d.strip() for d in raw_ids.split(",") if d.strip()}

        # Keep document if it matches any of the asked diseases
        if doc_diseases.intersection(asked_set):
            # Prioritize plain-language fact sheets when asked about general disease info
            adjusted_score = score
            if doc.metadata.get("doc_type") == "fact_sheet":
                adjusted_score += 0.02
            filtered.append((doc, adjusted_score))
        elif not doc_diseases:
            # General document without disease tags
            filtered.append((doc, score))
        # If doc_diseases is non-empty and has NO intersection with asked_set,
        # it belongs to another disease (e.g. Japanese Encephalitis when asked about TB)
        # and is strictly dropped.

    return filtered


def clean_unexplained_abbreviations(text: str) -> str:
    """Expand or clarify medical abbreviations in plain-language explanations."""
    replacements = [
        (r"\bATT\b(?!\s*\([^)]*anti)", "anti-tubercular treatment (ATT)"),
        (r"\bTBM\b(?!\s*\([^)]*brain)", "tuberculous meningitis (TB infection of the brain)"),
        (r"\bDOTS\b(?!\s*\([^)]*Directly)", "Directly Observed Treatment Short-Course (DOTS)"),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text

