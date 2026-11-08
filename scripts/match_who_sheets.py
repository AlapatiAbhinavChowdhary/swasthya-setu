import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
diseases = yaml.safe_load((ROOT / "data" / "diseases.yaml").read_text(encoding="utf-8"))["diseases"]
discovered = json.loads((ROOT / "logs" / "who_fact_sheets_discovered.json").read_text(encoding="utf-8"))

# Exact mappings derived from verified WHO fact sheet slugs
mapping = {
    "dengue": ["dengue-and-severe-dengue"],
    "malaria": ["malaria"],
    "chikungunya": ["chikungunya"],
    "japanese-encephalitis": ["japanese-encephalitis"],
    "kala-azar": ["leishmaniasis"],
    "lymphatic-filariasis": ["lymphatic-filariasis"],
    "tuberculosis": ["tuberculosis"],
    "typhoid": ["typhoid"],
    "cholera": ["cholera"],
    "diarrhoeal-disease": ["diarrhoeal-disease"],
    "hepatitis-a": ["hepatitis-a"],
    "hepatitis-b": ["hepatitis-b"],
    "hepatitis-e": ["hepatitis-e"],
    "seasonal-influenza": ["influenza-(seasonal)"],
    "covid-19": ["coronavirus-disease-(covid-19)"],
    "measles": ["measles"],
    "polio": ["poliomyelitis"],
    "diphtheria-pertussis-tetanus": ["diphtheria", "pertussis", "tetanus"],
    "rabies-animal-bites": ["rabies", "animal-bites"],
    "snakebite": ["snakebite-envenoming"],
    "leprosy": ["leprosy"],
    "hiv-aids": ["hiv-aids"],
    "diabetes": ["diabetes"],
    "hypertension": ["hypertension"],
    "anaemia-nutrition": ["anaemia", "malnutrition"],
    "maternal-newborn-care": ["maternal-mortality", "newborn-mortality"],
    "child-immunization": ["immunization-coverage"],
    "heat-illness": ["heatwaves-and-health", "climate-change-heat-and-health"],
    "mental-health-basics": ["mental-health-strengthening-our-response"],
    "hygiene-sanitation-safe-water": ["sanitation", "drinking-water"],
}

print("=== VERIFYING SLUGS IN DISCOVERED WHO INDEX ===")
verified_plan = {}
for d_id, slugs in mapping.items():
    verified_plan[d_id] = []
    for s in slugs:
        if s in discovered:
            verified_plan[d_id].append((s, discovered[s]["url"], discovered[s]["title"]))
            print(f"[OK] {d_id} -> {s} ('{discovered[s]['title']}')")
        else:
            # Search partial
            found = False
            for k in discovered:
                if s.replace("-", "") in k.replace("-", "") or k.startswith(s.split("-")[0]):
                    if d_id in k or any(w in k for w in d_id.split("-") if len(w)>4):
                        print(f" [Alt match] {d_id} ({s}) -> {k} ('{discovered[k]['title']}')")
            if not found:
                print(f"[MISSING] {d_id} -> slug {s} not in discovered index")

(ROOT / "logs" / "who_verified_plan.json").write_text(json.dumps(verified_plan, indent=2), encoding="utf-8")

