"""Batch 3 Acquisition Script for Swasthya Setu: Indian Government Documents.

Acquires verified official clinical guidelines and standard treatment workflows
from MoHFW (clinicalestablishments.mohfw.gov.in) and ICMR (icmr.gov.in)
for target diseases to achieve 3+ sources on 10+ diseases.
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
SOURCES_YAML = ROOT / "data" / "sources.yaml"
LOCKFILE = ROOT / "data" / "sources.lock.json"
REPORT_MD = ROOT / "docs" / "DOWNLOAD_REPORT.md"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# All URLs are official *.gov.in domains, discovered directly from official index pages
GOV_CANDIDATES = [
    # 1. Dengue - ICMR STW
    {
        "id": "doc-dengue-stw-icmr",
        "title": "Standard Treatment Workflows: Dengue Fever in Children",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1725952338_paediatrics_dengue_fever.pdf",
        "file": "data/raw/dengue/icmr-stw-dengue-fever.pdf",
        "disease_ids": ["dengue"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
    # 2. Hypertension - ICMR STW & MoHFW STG
    {
        "id": "doc-hypertension-stw-icmr",
        "title": "Standard Treatment Workflows: Hypertension in Adults",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1778941063_hypertensioninadults_final.pdf",
        "file": "data/raw/hypertension/icmr-stw-hypertension-adults.pdf",
        "disease_ids": ["hypertension"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
    {
        "id": "doc-hypertension-stg-mohfw",
        "title": "Standard Treatment Guidelines: Cardiovascular Diseases - Hypertension",
        "publisher": "Clinical Establishments, Ministry of Health and Family Welfare, Government of India",
        "url": "https://clinicalestablishments.mohfw.gov.in/sites/default/files/standard-treatment-guidelines/3811.pdf",
        "file": "data/raw/hypertension/mohfw-stg-cardiovascular-hypertension.pdf",
        "disease_ids": ["hypertension"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2014,
    },
    # 3. Diabetes - ICMR STWs Type 2 and Type 1
    {
        "id": "doc-diabetes-stw-type2-icmr",
        "title": "Standard Treatment Workflows: Diabetes Mellitus Type 2",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1726567245_diabetes_mellitus_type_2.pdf",
        "file": "data/raw/diabetes/icmr-stw-diabetes-type-2.pdf",
        "disease_ids": ["diabetes"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
    {
        "id": "doc-diabetes-stw-type1-icmr",
        "title": "Standard Treatment Workflows: Diabetes Mellitus Type 1",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1726567249_diabetes_mellitus_type_1.pdf",
        "file": "data/raw/diabetes/icmr-stw-diabetes-type-1.pdf",
        "disease_ids": ["diabetes"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
    # 4. Anaemia & Nutrition - ICMR STWs
    {
        "id": "doc-anaemia-stw-malnutrition-icmr",
        "title": "Standard Treatment Workflows: Severe Acute Malnutrition in Children",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1725952337_paediatrics_severe_acute_malnutrition.pdf",
        "file": "data/raw/anaemia-nutrition/icmr-stw-severe-acute-malnutrition.pdf",
        "disease_ids": ["anaemia-nutrition"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
    {
        "id": "doc-anaemia-stw-haemolytic-icmr",
        "title": "Standard Treatment Workflows: Haemolytic Anaemia",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1726568316_haemolytic_anaemia_all.pdf",
        "file": "data/raw/anaemia-nutrition/icmr-stw-haemolytic-anaemia.pdf",
        "disease_ids": ["anaemia-nutrition"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
    # 5. Maternal & Newborn Care - ICMR STWs
    {
        "id": "doc-maternal-stw-pregnancy-icmr",
        "title": "Standard Treatment Workflows: Antenatal Management of Normal Pregnancy",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1771568619_ante-natalmanagementofnormalpregnancy-7.pdf",
        "file": "data/raw/maternal-newborn-care/icmr-stw-antenatal-management-pregnancy.pdf",
        "disease_ids": ["maternal-newborn-care"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
    {
        "id": "doc-newborn-stw-thermal-icmr",
        "title": "Standard Treatment Workflows: Thermal Care of the Newborn",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1726568617_thermal_care_newborn.pdf",
        "file": "data/raw/maternal-newborn-care/icmr-stw-thermal-care-newborn.pdf",
        "disease_ids": ["maternal-newborn-care"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
    # 6. Seasonal Influenza / Respiratory - ICMR STWs
    {
        "id": "doc-influenza-stw-ari-icmr",
        "title": "Standard Treatment Workflows: Acute Respiratory Infections in Adults",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1725963734_pulmonology_acute_respiratory_infections.pdf",
        "file": "data/raw/seasonal-influenza/icmr-stw-acute-respiratory-infections.pdf",
        "disease_ids": ["seasonal-influenza"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
    {
        "id": "doc-influenza-stw-pneumonia-icmr",
        "title": "Standard Treatment Workflows: Severe Pneumonia in Children",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1725952336_paediatrics_severe_pneumonia.pdf",
        "file": "data/raw/seasonal-influenza/icmr-stw-severe-pneumonia.pdf",
        "disease_ids": ["seasonal-influenza"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
    # 7. Diarrhoeal Disease - ICMR STW & MoHFW STG
    {
        "id": "doc-diarrhoea-stw-icmr",
        "title": "Standard Treatment Workflows: Acute Diarrhea in Children",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1725952338_paediatrics_diarrhea.pdf",
        "file": "data/raw/diarrhoeal-disease/icmr-stw-acute-diarrhea.pdf",
        "disease_ids": ["diarrhoeal-disease"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
    {
        "id": "doc-diarrhoea-stg-mohfw",
        "title": "Standard Treatment Guidelines: Gastroenterological Diseases - Acute Diarrhoeal Diseases",
        "publisher": "Clinical Establishments, Ministry of Health and Family Welfare, Government of India",
        "url": "https://clinicalestablishments.mohfw.gov.in/sites/default/files/standard-treatment-guidelines/9721.pdf",
        "file": "data/raw/diarrhoeal-disease/mohfw-stg-gastroenterological-diarrhoea.pdf",
        "disease_ids": ["diarrhoeal-disease"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2014,
    },
    # 8. Rabies - MoHFW STG
    {
        "id": "doc-rabies-stg-mohfw",
        "title": "National Guidelines on Rabies Prophylaxis",
        "publisher": "Clinical Establishments, Ministry of Health and Family Welfare, Government of India",
        "url": "https://clinicalestablishments.mohfw.gov.in/sites/default/files/standard-treatment-guidelines/238.pdf",
        "file": "data/raw/rabies-animal-bites/mohfw-stg-rabies-prophylaxis.pdf",
        "disease_ids": ["rabies-animal-bites"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2014,
    },
    # 9. Chikungunya - MoHFW STG
    {
        "id": "doc-chikungunya-stg-mohfw",
        "title": "Standard Treatment Guidelines: Chikungunya Fever",
        "publisher": "Clinical Establishments, Ministry of Health and Family Welfare, Government of India",
        "url": "https://clinicalestablishments.mohfw.gov.in/sites/default/files/standard-treatment-guidelines/155.pdf",
        "file": "data/raw/chikungunya/mohfw-stg-chikungunya-fever.pdf",
        "disease_ids": ["chikungunya"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2014,
    },
    # 10. Japanese Encephalitis - MoHFW STG
    {
        "id": "doc-je-stg-mohfw",
        "title": "Standard Treatment Guidelines: Case Management of Acute Encephalitis Syndrome / Japanese Encephalitis",
        "publisher": "Clinical Establishments, Ministry of Health and Family Welfare, Government of India",
        "url": "https://clinicalestablishments.mohfw.gov.in/sites/default/files/standard-treatment-guidelines/5041.pdf",
        "file": "data/raw/japanese-encephalitis/mohfw-stg-japanese-encephalitis.pdf",
        "disease_ids": ["japanese-encephalitis"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2014,
    },
    # 11. Lymphatic Filariasis - MoHFW STG
    {
        "id": "doc-filariasis-stg-mohfw",
        "title": "Standard Treatment Guidelines: Filariasis Control in India and Its Elimination",
        "publisher": "Clinical Establishments, Ministry of Health and Family Welfare, Government of India",
        "url": "https://clinicalestablishments.mohfw.gov.in/sites/default/files/standard-treatment-guidelines/5021.pdf",
        "file": "data/raw/lymphatic-filariasis/mohfw-stg-filariasis-control.pdf",
        "disease_ids": ["lymphatic-filariasis"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2014,
    },
    # 12. Kala-Azar - MoHFW STG
    {
        "id": "doc-kala-azar-stg-mohfw",
        "title": "Standard Treatment Guidelines: Road Map for Kala-Azar Elimination",
        "publisher": "Clinical Establishments, Ministry of Health and Family Welfare, Government of India",
        "url": "https://clinicalestablishments.mohfw.gov.in/sites/default/files/standard-treatment-guidelines/7051.pdf",
        "file": "data/raw/kala-azar/mohfw-stg-kala-azar-elimination.pdf",
        "disease_ids": ["kala-azar"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2014,
    },
    # 13. Hepatitis (A, B, E) - MoHFW STG
    {
        "id": "doc-hepatitis-stg-mohfw",
        "title": "National Guidelines for Diagnosis & Management of Viral Hepatitis",
        "publisher": "Clinical Establishments, Ministry of Health and Family Welfare, Government of India",
        "url": "https://clinicalestablishments.mohfw.gov.in/sites/default/files/standard-treatment-guidelines/3591.pdf",
        "file": "data/raw/hepatitis-b/mohfw-stg-viral-hepatitis.pdf",
        "disease_ids": ["hepatitis-a", "hepatitis-b", "hepatitis-e"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2018,
    },
    # 14. Mental Health - MoHFW STG
    {
        "id": "doc-mental-health-stg-mohfw",
        "title": "Standard Treatment Guidelines: Management of Common Mental Disorders",
        "publisher": "Clinical Establishments, Ministry of Health and Family Welfare, Government of India",
        "url": "https://clinicalestablishments.mohfw.gov.in/sites/default/files/standard-treatment-guidelines/606.pdf",
        "file": "data/raw/mental-health-basics/mohfw-stg-common-mental-disorders.pdf",
        "disease_ids": ["mental-health-basics"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2014,
    },
]


def fetch_pdf(url: str) -> tuple[bytes | None, str, str | None]:
    """Fetch PDF with urllib and curl fallback."""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if data.startswith(b"%PDF"):
                    return data, f"urllib (attempt {attempt + 1})", None
        except Exception as e:
            if attempt == 2:
                urllib_err = str(e)
            time.sleep(1 + attempt)

    try:
        res = subprocess.run(
            [
                "curl.exe",
                "-L",
                "-4",
                "--fail",
                "--silent",
                "--show-error",
                "--connect-timeout",
                "15",
                "--max-time",
                "60",
                "-A",
                USER_AGENT,
                url,
            ],
            capture_output=True,
            timeout=70,
        )
        if res.stdout.startswith(b"%PDF"):
            return res.stdout, "curl.exe -L -4", None
        curl_err = res.stderr.decode("utf-8", errors="replace").strip()
    except Exception as e:
        curl_err = str(e)

    return None, "unreachable", f"urllib: {urllib_err}; curl: {curl_err}"


def main():
    logger.info("Starting Batch 3: Indian Government Documents Acquisition...")

    # Load existing manifest and lock
    existing_manifest = yaml.safe_load(SOURCES_YAML.read_text(encoding="utf-8")) or {}
    manifest_sources = {s["id"]: s for s in existing_manifest.get("sources", [])}
    seen_hashes: dict[str, str] = {}
    for s in manifest_sources.values():
        if s.get("file") and (ROOT / s["file"]).exists():
            h = hashlib.sha256((ROOT / s["file"]).read_bytes()).hexdigest()
            seen_hashes[h] = s["id"]

    existing_lock = []
    if LOCKFILE.exists():
        existing_lock = json.loads(LOCKFILE.read_text(encoding="utf-8"))
    lock_by_url = {item["url"]: item for item in existing_lock}

    downloaded = 0
    skipped = 0
    failed = 0

    for item in GOV_CANDIDATES:
        source_id = item["id"]
        url = item["url"]
        target = ROOT / item["file"]
        target.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Processing %s: %s", source_id, url)

        # Idempotent skip if exists and valid
        if target.exists():
            data = target.read_bytes()
            if data.startswith(b"%PDF"):
                doc_hash = hashlib.sha256(data).hexdigest()
                item["doc_id"] = doc_hash
                item["status"] = "local_file"
                manifest_sources[source_id] = item
                seen_hashes[doc_hash] = source_id
                lock_by_url[url] = {
                    "url": url,
                    "file": str(target.relative_to(ROOT)),
                    "date": date.today().isoformat(),
                    "status": "skipped",
                    "hash": doc_hash,
                    "bytes": len(data),
                }
                skipped += 1
                logger.info("  Skipped (already on disk): %s", source_id)
                continue

        # Fetch using ladder
        data, step_used, err = fetch_pdf(url)
        if data:
            doc_hash = hashlib.sha256(data).hexdigest()
            target.write_bytes(data)
            item["doc_id"] = doc_hash
            item["status"] = "downloaded"
            manifest_sources[source_id] = item
            seen_hashes[doc_hash] = source_id
            lock_by_url[url] = {
                "url": url,
                "file": str(target.relative_to(ROOT)),
                "date": date.today().isoformat(),
                "status": "downloaded",
                "hash": doc_hash,
                "bytes": len(data),
                "fallback": step_used,
            }
            downloaded += 1
            logger.info("  Downloaded %s (%d bytes via %s)", source_id, len(data), step_used)
        else:
            lock_by_url[url] = {
                "url": url,
                "file": str(target.relative_to(ROOT)),
                "date": date.today().isoformat(),
                "status": "unreachable",
                "error": err,
            }
            failed += 1
            logger.warning("  Unreachable %s: %s", source_id, err)

    # Save sources.yaml
    manifest_sources_list = sorted(manifest_sources.values(), key=lambda s: s["id"])
    SOURCES_YAML.write_text(
        yaml.dump({"sources": manifest_sources_list}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    logger.info("Saved %d sources to %s", len(manifest_sources_list), SOURCES_YAML)

    # Save sources.lock.json
    lock_list = sorted(lock_by_url.values(), key=lambda s: s["url"])
    LOCKFILE.write_text(json.dumps(lock_list, indent=2), encoding="utf-8")
    logger.info("Saved %d lock entries to %s", len(lock_list), LOCKFILE)

    # Regenerate download report
    generate_download_report(lock_list)
    logger.info("Batch 3 Complete: %d downloaded, %d skipped, %d failed", downloaded, skipped, failed)


def generate_download_report(lock_entries: list[dict]):
    lines = [
        "# Source download report",
        "",
        "Generated from `data/sources.lock.json` and official acquisition runs.",
        "",
        "| Source URL | Status | Bytes | Fallback Step | Reason / Details |",
        "|---|---|---:|---|---|",
    ]
    for e in lock_entries:
        url = e.get("url", "")
        status = e.get("status", "")
        bytes_val = e.get("bytes", 0)
        fallback = e.get("fallback", "-")
        reason = e.get("error", "Verified official file")
        lines.append(f"| {url} | {status} | {bytes_val} | {fallback} | {reason} |")

    lines.append("")
    lines.append("## Unreachable sources log")
    unreachable = [e for e in lock_entries if e.get("status") == "unreachable"]
    if unreachable:
        for u in unreachable:
            lines.append(f"- **{u.get('url')}**: `{u.get('error')}`")
    else:
        lines.append("- No unreachable sources logged.")
    lines.append("")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Updated download report at %s", REPORT_MD)


if __name__ == "__main__":
    main()
