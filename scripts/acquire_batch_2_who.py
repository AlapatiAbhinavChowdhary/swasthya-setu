"""Batch 2 Acquisition Script for Swasthya Setu: WHO Fact Sheets.

Acquires verified WHO fact sheets from who.int discovered from the official
fact sheet index for all target diseases.
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
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
SOURCES_YAML = ROOT / "data" / "sources.yaml"
LOCKFILE = ROOT / "data" / "sources.lock.json"
REPORT_MD = ROOT / "docs" / "DOWNLOAD_REPORT.md"
DISCOVERED_FILE = ROOT / "logs" / "who_fact_sheets_discovered.json"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Verified mapping from who.int news-room/fact-sheets index
DISEASE_WHO_MAPPING: dict[str, list[str]] = {
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
    "diphtheria-pertussis-tetanus": ["diphtheria", "tetanus"],
    "rabies-animal-bites": ["rabies", "animal-bites"],
    "snakebite": ["snakebite-envenoming"],
    "leprosy": ["leprosy"],
    "hiv-aids": ["hiv-aids"],
    "diabetes": ["diabetes"],
    "hypertension": ["hypertension"],
    "anaemia-nutrition": ["anaemia", "malnutrition"],
    "maternal-newborn-care": ["maternal-mortality", "newborn-mortality"],
    "child-immunization": ["immunization-coverage"],
    "heat-illness": ["climate-change-heat-and-health"],
    "mental-health-basics": ["mental-health-strengthening-our-response"],
    "hygiene-sanitation-safe-water": ["sanitation", "drinking-water"],
}


def fetch_html(url: str) -> tuple[bytes | None, str, str | None]:
    """Fetch HTML using urllib then curl.exe with timeouts."""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if b"<html" in data.lower() or b"<!doctype html" in data.lower():
                    if len(data) > 1000:
                        return data, f"urllib (attempt {attempt + 1})", None
        except Exception as e:
            if attempt == 2:
                urllib_err = str(e)
            time.sleep(1 + attempt)

    # curl fallback
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
        if b"<html" in res.stdout.lower() or b"<!doctype html" in res.stdout.lower():
            if len(res.stdout) > 1000:
                return res.stdout, "curl.exe -L -4", None
        curl_err = res.stderr.decode("utf-8", errors="replace").strip()
    except Exception as e:
        curl_err = str(e)

    return None, "unreachable", f"urllib: {urllib_err}; curl: {curl_err}"


def main():
    logger.info("Starting Batch 2: WHO Fact Sheets Acquisition...")

    discovered = json.loads(DISCOVERED_FILE.read_text(encoding="utf-8"))

    # Load existing sources and lock
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

    downloaded_count = 0
    skipped_count = 0
    failed_count = 0

    for disease_id, slugs in DISEASE_WHO_MAPPING.items():
        for slug in slugs:
            if slug not in discovered:
                logger.warning("Slug %s not in discovered index!", slug)
                continue

            info = discovered[slug]
            url = info["url"]
            title = info["title"] or f"WHO Fact Sheet: {slug}"
            source_id = f"doc-who-factsheet-{slug.replace('(', '').replace(')', '')}"
            target_file = ROOT / "data" / "raw" / disease_id / f"who-{slug.replace('(', '').replace(')', '')}.html"
            target_file.parent.mkdir(parents=True, exist_ok=True)

            logger.info("Processing [%s] %s: %s", disease_id, source_id, url)

            # Check if file already exists
            if target_file.exists():
                data = target_file.read_bytes()
                if len(data) > 1000:
                    doc_hash = hashlib.sha256(data).hexdigest()
                    seen_hashes[doc_hash] = source_id
                    manifest_sources[source_id] = {
                        "id": source_id,
                        "title": f"WHO Fact Sheet: {title}",
                        "publisher": "World Health Organization (WHO)",
                        "url": url,
                        "file": str(target_file.relative_to(ROOT)),
                        "disease_ids": [disease_id],
                        "coverage": "disease-specific",
                        "language": "en",
                        "doc_type": "fact_sheet",
                        "license_note": "WHO content, CC BY-NC-SA 3.0 IGO; retain attribution and link.",
                        "doc_id": doc_hash,
                        "status": "local_file",
                    }
                    lock_by_url[url] = {
                        "url": url,
                        "file": str(target_file.relative_to(ROOT)),
                        "date": date.today().isoformat(),
                        "status": "skipped",
                        "hash": doc_hash,
                        "bytes": len(data),
                    }
                    skipped_count += 1
                    logger.info("  Skipped (already on disk): %s", source_id)
                    continue

            # Fetch HTML
            data, step_used, err = fetch_html(url)

            if data:
                doc_hash = hashlib.sha256(data).hexdigest()
                target_file.write_bytes(data)
                manifest_sources[source_id] = {
                    "id": source_id,
                    "title": f"WHO Fact Sheet: {title}",
                    "publisher": "World Health Organization (WHO)",
                    "url": url,
                    "file": str(target_file.relative_to(ROOT)),
                    "disease_ids": [disease_id],
                    "coverage": "disease-specific",
                    "language": "en",
                    "doc_type": "fact_sheet",
                    "license_note": "WHO content, CC BY-NC-SA 3.0 IGO; retain attribution and link.",
                    "doc_id": doc_hash,
                    "status": "downloaded",
                }
                seen_hashes[doc_hash] = source_id
                lock_by_url[url] = {
                    "url": url,
                    "file": str(target_file.relative_to(ROOT)),
                    "date": date.today().isoformat(),
                    "status": "downloaded",
                    "hash": doc_hash,
                    "bytes": len(data),
                    "fallback": step_used,
                }
                downloaded_count += 1
                logger.info("  Downloaded %s (%d bytes via %s)", source_id, len(data), step_used)
            else:
                lock_by_url[url] = {
                    "url": url,
                    "file": str(target_file.relative_to(ROOT)),
                    "date": date.today().isoformat(),
                    "status": "unreachable",
                    "error": err,
                }
                failed_count += 1
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

    # Regenerate DOWNLOAD_REPORT.md
    generate_download_report(lock_list)

    logger.info("Batch 2 WHO Complete: %d downloaded, %d skipped, %d failed",
                downloaded_count, skipped_count, failed_count)


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

