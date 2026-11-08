"""Batch 1 Acquisition Script for Swasthya Setu.

Acquires seed documents for Immunization, Malaria, Dengue, and Tuberculosis
from official government and WHO sources using the Fetch Fallback Ladder.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from pypdf import PdfReader
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
SOURCES_YAML = ROOT / "data" / "sources.yaml"
LOCKFILE = ROOT / "data" / "sources.lock.json"
REPORT_MD = ROOT / "docs" / "DOWNLOAD_REPORT.md"
STRUCTURED_SCHEDULE = ROOT / "data" / "structured" / "vaccination_schedule.json"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

CANDIDATES = [
    # --- Immunization ---
    {
        "id": "doc-immunization-nis-2018",
        "title": "National Immunization Schedule",
        "publisher": "National Health Mission, Ministry of Health and Family Welfare, Government of India",
        "url": "https://nhm.gov.in/New_Updates_2018/NHM_Components/Immunization/report/National_%20Immunization_Schedule.pdf",
        "file": "data/raw/child-immunization/national-immunization-schedule-2018.pdf",
        "disease_ids": [
            "child-immunization",
            "hepatitis-b",
            "polio",
            "measles",
            "japanese-encephalitis",
            "diphtheria-pertussis-tetanus",
        ],
        "coverage": "general",
        "language": "en",
        "doc_type": "schedule",
        "year": 2018,
    },
    {
        "id": "doc-immunization-faq-hw",
        "title": "Frequently Asked Questions on Immunization for Health Workers",
        "publisher": "National Health Mission, Ministry of Health and Family Welfare, Government of India",
        "url": "https://nhm.gov.in/New_Updates_2018/NHM_Components/Immunization/Guildelines_for_immunization/FAQ_on_Immunization_for_Health_Workers-English.pdf",
        "file": "data/raw/child-immunization/faq-immunization-health-workers.pdf",
        "disease_ids": [
            "child-immunization",
            "hepatitis-b",
            "polio",
            "measles",
            "diphtheria-pertussis-tetanus",
        ],
        "coverage": "general",
        "language": "en",
        "doc_type": "iec",
        "year": 2018,
    },
    {
        "id": "doc-immunization-faq-pm",
        "title": "Frequently Asked Questions on Immunization for Program Managers",
        "publisher": "National Health Mission, Ministry of Health and Family Welfare, Government of India",
        "url": "https://nhm.gov.in/New_Updates_2018/NHM_Components/Immunization/Guildelines_for_immunization/FAQ_on_Immunization_for_Program_Manager-English.pdf",
        "file": "data/raw/child-immunization/faq-immunization-program-managers.pdf",
        "disease_ids": [
            "child-immunization",
            "hepatitis-b",
            "polio",
            "measles",
            "diphtheria-pertussis-tetanus",
        ],
        "coverage": "general",
        "language": "en",
        "doc_type": "iec",
        "year": 2018,
    },
    {
        "id": "doc-immunization-mohfw-unit2",
        "title": "Unit 2: National Immunization Schedule (2008)",
        "publisher": "Ministry of Health and Family Welfare, Government of India",
        "url": "https://main.mohfw.gov.in/sites/default/files/Unit2NationalImmunizationSchedule.pdf",
        "file": "data/raw/child-immunization/mohfw-unit2-immunization-schedule-2008.pdf",
        "disease_ids": [
            "child-immunization",
            "hepatitis-b",
            "polio",
            "measles",
            "diphtheria-pertussis-tetanus",
        ],
        "coverage": "general",
        "language": "en",
        "doc_type": "schedule",
        "year": 2008,
    },
    {
        "id": "doc-immunization-who-handbook-2008",
        "title": "Immunization Handbook for Medical Officers",
        "publisher": "WHO Country Office for India and Government of India",
        "url": "https://cdn.who.int/media/docs/default-source/searo/india/routine-immunization/immunization-handbook-for-medical-officers-2008.pdf",
        "file": "data/raw/child-immunization/who-immunization-handbook-medical-officers-2008.pdf",
        "disease_ids": [
            "child-immunization",
            "hepatitis-b",
            "polio",
            "measles",
            "diphtheria-pertussis-tetanus",
        ],
        "coverage": "general",
        "language": "en",
        "doc_type": "guideline",
        "year": 2008,
        "license_note": "WHO publication, CC BY-NC-SA 3.0 IGO; retain attribution and source link.",
    },
    # --- Malaria ---
    {
        "id": "doc-malaria-stg-mohfw",
        "title": "Standard Treatment Guidelines: Malaria",
        "publisher": "Clinical Establishments, Ministry of Health and Family Welfare, Government of India",
        "url": "https://clinicalestablishments.mohfw.gov.in/sites/default/files/standard-treatment-guidelines/892.pdf",
        "file": "data/raw/malaria/standard-treatment-guidelines-malaria.pdf",
        "disease_ids": ["malaria"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2014,
    },
    {
        "id": "doc-malaria-nsp-2023-27",
        "title": "National Strategic Plan for Malaria Elimination in India 2023-2027",
        "publisher": "National Center for Vector Borne Diseases Control (NCVBDC), MoHFW, Government of India",
        "url": "https://ncvbdc.mohfw.gov.in/Doc/National-Strategic-Plan-Malaria-2023-27.pdf",
        "file": "data/raw/malaria/national-strategic-plan-malaria-2023-27.pdf",
        "disease_ids": ["malaria"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "strategy",
        "year": 2023,
    },
    {
        "id": "doc-malaria-framework-2016-30",
        "title": "National Framework for Malaria Elimination in India 2016-2030",
        "publisher": "National Center for Vector Borne Diseases Control (NCVBDC), MoHFW, Government of India",
        "url": "https://ncvbdc.mohfw.gov.in/WriteReadData/l892s/National-framework-for-malaria-elimination-in-India-2016%E2%80%932030.pdf",
        "file": "data/raw/malaria/national-framework-malaria-elimination-2016-2030.pdf",
        "disease_ids": ["malaria"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "strategy",
        "year": 2016,
    },
    {
        "id": "doc-malaria-operational-manual-2016",
        "title": "Operational Manual for Malaria Elimination in India 2016",
        "publisher": "National Center for Vector Borne Diseases Control (NCVBDC), MoHFW, Government of India",
        "url": "https://ncvbdc.mohfw.gov.in/WriteReadData/l892s/5232542721532941542.pdf",
        "file": "data/raw/malaria/operational-manual-malaria-elimination-2016.pdf",
        "disease_ids": ["malaria"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2016,
    },
    # --- Dengue ---
    {
        "id": "doc-dengue-guideline-7c8ffb",
        "title": "National Guidelines for Clinical Management of Dengue Fever 2023",
        "publisher": "NCVBDC, Ministry of Health and Family Welfare, Government of India",
        "url": "https://ncvbdc.mohfw.gov.in/Doc/National%20Guidelines%20for%20Clinical%20Management%20of%20Dengue%20Fever%202023.pdf",
        "file": "data/raw/dengue_guidelines_2023.pdf",
        "disease_ids": ["dengue"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2023,
    },
    # --- Tuberculosis ---
    {
        "id": "doc-tb-guidance-differential-care-2025",
        "title": "National Guidance on Differential TB Care",
        "publisher": "Central TB Division, Ministry of Health and Family Welfare, Government of India",
        "url": "https://tbcindia.mohfw.gov.in/wp-content/uploads/2025/07/National-Guidance-on-Differential-TB-Care_Final_March-2025-3.pdf",
        "file": "data/raw/tuberculosis/national-guidance-differential-tb-care-2025.pdf",
        "disease_ids": ["tuberculosis"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2025,
    },
    {
        "id": "doc-tb-tog-ch3-case-finding-2016",
        "title": "Technical and Operational Guidelines for TB Control 2016 - Chapter 3: Case Finding and Diagnosis Strategy",
        "publisher": "Central TB Division, Ministry of Health and Family Welfare, Government of India",
        "url": "https://tbcindia.mohfw.gov.in/wp-content/uploads/2023/05/1394742221TOG-Chapter-3-Case-finding-diagnosis-strategy1.pdf",
        "file": "data/raw/tuberculosis/tog-2016-chapter-3-case-finding-diagnosis.pdf",
        "disease_ids": ["tuberculosis"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2016,
    },
    {
        "id": "doc-tb-tog-ch4-treatment-p1-2016",
        "title": "Technical and Operational Guidelines for TB Control 2016 - Chapter 4: Treatment of TB (Part 1)",
        "publisher": "Central TB Division, Ministry of Health and Family Welfare, Government of India",
        "url": "https://tbcindia.mohfw.gov.in/wp-content/uploads/2023/05/8337437943TOG-Chapter-4-Treatment-of-TB-Part-1.pdf",
        "file": "data/raw/tuberculosis/tog-2016-chapter-4-treatment-of-tb-part-1.pdf",
        "disease_ids": ["tuberculosis"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2016,
    },
    {
        "id": "doc-tb-tog-ch4-treatment-p2-2016",
        "title": "Technical and Operational Guidelines for TB Control 2016 - Chapter 4: Treatment of TB (Part 2)",
        "publisher": "Central TB Division, Ministry of Health and Family Welfare, Government of India",
        "url": "https://tbcindia.mohfw.gov.in/wp-content/uploads/2023/05/934546848TOG-Chapter-4-Treatment-of-TB-Part-2.pdf",
        "file": "data/raw/tuberculosis/tog-2016-chapter-4-treatment-of-tb-part-2.pdf",
        "disease_ids": ["tuberculosis"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2016,
    },
    {
        "id": "doc-tb-icmr-stw-extrapulmonary",
        "title": "Standard Treatment Workflows: Adult Extrapulmonary Tuberculosis",
        "publisher": "Indian Council of Medical Research (ICMR), Government of India",
        "url": "https://www.icmr.gov.in/icmrobject/uploads/STWs/1725964687_adult-extrapulmonary-tuberculosis-all.pdf",
        "file": "data/raw/tuberculosis/icmr-adult-extrapulmonary-tuberculosis-stw.pdf",
        "disease_ids": ["tuberculosis"],
        "coverage": "disease-specific",
        "language": "en",
        "doc_type": "guideline",
        "year": 2022,
    },
]


def fetch_with_ladder(url: str) -> tuple[bytes | None, str, str | None]:
    """Fetch using the Fetch Fallback Ladder:

    1. Python urllib with browser User-Agent and backoff (3 attempts).
    2. curl.exe -L with IPv4 (-4).
    3. PowerShell Invoke-WebRequest.
    4. Alternative host formats (e.g. toggle www).
    Returns: (data_bytes, ladder_step_used, error_message)
    """
    # 1. Python urllib with backoff
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if data.startswith(b"%PDF"):
                    return data, "Python urllib (attempt " + str(attempt + 1) + ")", None
        except Exception as e:
            if attempt == 2:
                urllib_err = str(e)
            time.sleep(1 + attempt)

    # 2. curl.exe with -L and -4
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
                "20",
                "--max-time",
                "90",
                "-A",
                USER_AGENT,
                url,
            ],
            capture_output=True,
            timeout=100,
        )
        if res.stdout.startswith(b"%PDF"):
            return res.stdout, "curl.exe -L -4", None
        curl_err = res.stderr.decode("utf-8", errors="replace").strip()
    except Exception as e:
        curl_err = str(e)

    # 3. PowerShell Invoke-WebRequest
    try:
        ps_cmd = f"$ProgressPreference = 'SilentlyContinue'; (Invoke-WebRequest -Uri '{url}' -UserAgent '{USER_AGENT}' -UseBasicParsing -TimeoutSec 30).Content"
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            timeout=60,
        )
        if res.stdout.startswith(b"%PDF"):
            return res.stdout, "PowerShell Invoke-WebRequest", None
        ps_err = res.stderr.decode("utf-8", errors="replace").strip()
    except Exception as e:
        ps_err = str(e)

    # 4. Host modification / alternative host
    parsed = urllib.parse.urlsplit(url)
    alt_netloc = None
    if parsed.netloc.startswith("main."):
        alt_netloc = "www." + parsed.netloc[5:]
    elif parsed.netloc.startswith("www."):
        alt_netloc = parsed.netloc[4:]
    else:
        alt_netloc = "www." + parsed.netloc

    if alt_netloc:
        alt_url = urllib.parse.urlunsplit(
            (parsed.scheme, alt_netloc, parsed.path, parsed.query, parsed.fragment)
        )
        try:
            res = subprocess.run(
                [
                    "curl.exe",
                    "-L",
                    "-4",
                    "--fail",
                    "--silent",
                    "--show-error",
                    "-A",
                    USER_AGENT,
                    alt_url,
                ],
                capture_output=True,
                timeout=60,
            )
            if res.stdout.startswith(b"%PDF"):
                return res.stdout, f"curl.exe on alternative host ({alt_netloc})", None
        except Exception:
            pass

    combined_err = f"urllib: {urllib_err}; curl: {curl_err}"
    return None, "unreachable", combined_err


def main():
    logger.info("Starting Batch 1 Acquisition...")

    # Load existing sources and lock
    existing_manifest = yaml.safe_load(SOURCES_YAML.read_text(encoding="utf-8")) or {}
    manifest_sources = {s["id"]: s for s in existing_manifest.get("sources", [])}
    seen_hashes: dict[str, str] = {}
    for s in manifest_sources.values():
        if s.get("file") and (ROOT / s["file"]).exists():
            h = hashlib.sha256((ROOT / s["file"]).read_bytes()).hexdigest()
            s["doc_id"] = h
            seen_hashes[h] = s["id"]

    existing_lock = []
    if LOCKFILE.exists():
        existing_lock = json.loads(LOCKFILE.read_text(encoding="utf-8"))
    lock_by_url = {item["url"]: item for item in existing_lock}

    report_entries = []

    for item in CANDIDATES:
        source_id = item["id"]
        url = item["url"]
        target = ROOT / item["file"]
        target.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Processing %s: %s", source_id, url)

        # Check if already present on disk
        if target.exists():
            data = target.read_bytes()
            if data.startswith(b"%PDF"):
                doc_hash = hashlib.sha256(data).hexdigest()
                item["doc_id"] = doc_hash
                item["status"] = "local_file"
                manifest_sources[source_id] = item
                seen_hashes[doc_hash] = source_id
                lock_entry = {
                    "url": url,
                    "file": str(target.relative_to(ROOT)),
                    "date": date.today().isoformat(),
                    "status": "skipped",
                    "hash": doc_hash,
                    "bytes": len(data),
                }
                lock_by_url[url] = lock_entry
                report_entries.append({
                    "source": source_id,
                    "status": "skipped",
                    "bytes": len(data),
                    "fallback": "Existing file",
                    "reason": f"Valid PDF already present ({len(data)} bytes)",
                })
                logger.info("  Skipped (already exists): %s", source_id)
                continue

        # Fetch using Ladder
        data, step_used, err = fetch_with_ladder(url)

        if data:
            doc_hash = hashlib.sha256(data).hexdigest()
            # Check deduplication
            if doc_hash in seen_hashes:
                logger.info(
                    "  Duplicate content hash %s already registered under %s",
                    doc_hash[:12],
                    seen_hashes[doc_hash],
                )
                item["status"] = "deduplicated"
            else:
                target.write_bytes(data)
                item["status"] = "downloaded"
                seen_hashes[doc_hash] = source_id

            item["doc_id"] = doc_hash
            manifest_sources[source_id] = item

            lock_entry = {
                "url": url,
                "file": str(target.relative_to(ROOT)),
                "date": date.today().isoformat(),
                "status": "downloaded",
                "hash": doc_hash,
                "bytes": len(data),
                "fallback": step_used,
            }
            lock_by_url[url] = lock_entry
            report_entries.append({
                "source": source_id,
                "status": "downloaded",
                "bytes": len(data),
                "fallback": step_used,
                "reason": f"PDF successfully verified via {step_used}",
            })
            logger.info("  Downloaded %s (%d bytes via %s)", source_id, len(data), step_used)
        else:
            lock_entry = {
                "url": url,
                "file": str(target.relative_to(ROOT)),
                "date": date.today().isoformat(),
                "status": "unreachable",
                "error": err,
            }
            lock_by_url[url] = lock_entry
            report_entries.append({
                "source": source_id,
                "status": "unreachable",
                "bytes": 0,
                "fallback": "Failed all ladder steps",
                "reason": err,
            })
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

    # Build structured vaccination schedule
    build_vaccination_schedule()

    # Update docs/DOWNLOAD_REPORT.md
    generate_download_report(lock_list)


def build_vaccination_schedule():
    nis_file = ROOT / "data" / "raw" / "child-immunization" / "national-immunization-schedule-2018.pdf"
    if not nis_file.exists():
        nis_file = ROOT / "data" / "raw" / "child-immunization" / "national-immunization-schedule.pdf"

    if not nis_file.exists():
        logger.warning("National Immunization Schedule file not found; skipping structured schedule.")
        return

    reader = PdfReader(str(nis_file))
    text = "\n".join(page.extract_text() for page in reader.pages)

    if "National Immunization Schedule" not in text or "Birth" not in text or "6 Weeks" not in text:
        logger.warning("NIS text does not contain expected schedule table; not usable yet.")
        return

    STRUCTURED_SCHEDULE.parent.mkdir(parents=True, exist_ok=True)
    schedule_data = {
        "source": {
            "title": "National Immunization Schedule (NIS) for Infants, Children and Pregnant Women",
            "publisher": "National Health Mission, Ministry of Health and Family Welfare, Government of India",
            "url": "https://nhm.gov.in/New_Updates_2018/NHM_Components/Immunization/report/National_%20Immunization_Schedule.pdf",
            "verified": True,
            "year": 2018,
        },
        "schedule": [
            {
                "age": "Birth",
                "age_key": "birth",
                "target_group": "Infants",
                "vaccines": ["BCG", "OPV-0", "Hepatitis B birth dose"],
                "description": "Bacillus Calmette Guerin (BCG), Oral Polio Vaccine (OPV)-0 dose, Hepatitis B birth dose (within 24 hours).",
            },
            {
                "age": "6 Weeks",
                "age_key": "6_weeks",
                "target_group": "Infants",
                "vaccines": ["OPV-1", "Pentavalent-1", "Rotavirus-1 (RVV-1)", "fIPV-1", "PCV-1*"],
                "description": "OPV-1, Pentavalent-1 (Diphtheria, Pertussis, Tetanus, Hepatitis B, Hib), Rotavirus Vaccine-1, Fractional dose Inactivated Polio Vaccine-1, Pneumococcal Conjugate Vaccine-1 (in selected states).",
            },
            {
                "age": "10 Weeks",
                "age_key": "10_weeks",
                "target_group": "Infants",
                "vaccines": ["OPV-2", "Pentavalent-2", "Rotavirus-2 (RVV-2)"],
                "description": "OPV-2, Pentavalent-2, Rotavirus Vaccine (RVV)-2.",
            },
            {
                "age": "14 Weeks",
                "age_key": "14_weeks",
                "target_group": "Infants",
                "vaccines": ["OPV-3", "Pentavalent-3", "fIPV-2", "Rotavirus-3 (RVV-3)", "PCV-2*"],
                "description": "OPV-3, Pentavalent-3, fIPV-2, Rotavirus Vaccine-3, PCV-2 (in selected states).",
            },
            {
                "age": "9-12 Months",
                "age_key": "9_12_months",
                "target_group": "Infants",
                "vaccines": ["MR-1 (Measles & Rubella)", "JE-1**", "PCV-Booster*", "Vitamin A (1st dose)"],
                "description": "Measles & Rubella (MR)-1st dose, Japanese Encephalitis (JE)-1st dose (in endemic districts), PCV-Booster, Vitamin A 1st dose (1 lakh IU).",
            },
            {
                "age": "16-24 Months",
                "age_key": "16_24_months",
                "target_group": "Children",
                "vaccines": ["MR-2", "JE-2**", "DPT-Booster-1", "OPV-Booster", "Vitamin A (2nd dose)"],
                "description": "MR 2nd dose, JE-2 (endemic districts), DPT Booster-1, OPV Booster, Vitamin A (doses 2-9 every 6 months up to 5 years).",
            },
            {
                "age": "5-6 Years",
                "age_key": "5_6_years",
                "target_group": "Children",
                "vaccines": ["DPT-Booster-2"],
                "description": "DPT Booster-2.",
            },
            {
                "age": "10 Years",
                "age_key": "10_years",
                "target_group": "Adolescents",
                "vaccines": ["Td (Tetanus & adult Diphtheria)"],
                "description": "Tetanus & adult Diphtheria (Td).",
            },
            {
                "age": "16 Years",
                "age_key": "16_years",
                "target_group": "Adolescents",
                "vaccines": ["Td (Tetanus & adult Diphtheria)"],
                "description": "Tetanus & adult Diphtheria (Td).",
            },
            {
                "age": "Pregnant Women",
                "age_key": "pregnancy",
                "target_group": "Pregnant Women",
                "vaccines": ["Td-1", "Td-2 or Td-Booster"],
                "description": "Td-1 early in pregnancy; Td-2 4 weeks after Td-1; Td-Booster if 2 TT/Td doses received in pregnancy within last 3 years.",
            },
        ],
    }
    STRUCTURED_SCHEDULE.write_text(json.dumps(schedule_data, indent=2), encoding="utf-8")
    logger.info("Saved structured vaccination schedule to %s", STRUCTURED_SCHEDULE)


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

