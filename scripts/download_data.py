"""Download and validate official PDF sources listed in data/sources.yaml."""

from __future__ import annotations

import hashlib
import json
import logging
import time
import urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import yaml

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sources.yaml"
LOCKFILE = ROOT / "data" / "sources.lock.json"
MAX_BYTES = 60 * 1024 * 1024
USER_AGENT = "SwasthyaSetuSourceDownloader/1.0"


def _robots_allowed(url: str) -> bool:
    parsed = urlparse(url)
    robots = RobotFileParser(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    try:
        robots.read()
    except OSError:
        logger.warning("Could not read robots.txt for %s; skipping", parsed.netloc)
        return False
    return robots.can_fetch(USER_AGENT, url)


def _download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        content_length = int(response.headers.get("Content-Length", "0") or 0)
        if content_length > MAX_BYTES:
            raise RuntimeError("content exceeds 60 MB limit")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise RuntimeError("content exceeds 60 MB limit")
    if not data.startswith(b"%PDF"):
        raise RuntimeError("response is not a PDF")
    return data


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    lock: list[dict[str, object]] = []
    for source in manifest.get("sources", []):
        source_id = source["id"]
        disease_id = source["disease_ids"][0]
        target = ROOT / "data" / "raw" / disease_id / f"{source_id}.pdf"
        entry: dict[str, object] = {
            "url": source["url"],
            "file": str(target.relative_to(ROOT)),
            "date": date.today().isoformat(),
        }
        try:
            if target.exists():
                data = target.read_bytes()
                if data.startswith(b"%PDF"):
                    entry.update({"status": "skipped", "hash": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
                    lock.append(entry)
                    continue
            if not _robots_allowed(source["url"]):
                raise RuntimeError("robots.txt disallows or is unavailable")
            for attempt in range(3):
                try:
                    data = _download(source["url"])
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(2**attempt)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            entry.update({"status": "downloaded", "hash": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        except Exception as exc:
            logger.warning("Failed %s: %s", source_id, exc)
            entry.update({"status": "failed", "error": str(exc)})
        lock.append(entry)
    LOCKFILE.write_text(json.dumps(lock, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
