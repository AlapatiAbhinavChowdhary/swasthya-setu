"""Download and validate official PDF sources listed in data/sources.yaml."""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
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
ALLOWED_HTML_HOSTS = (".gov.in", ".nic.in", "who.int", ".who.int")


def _robots_allowed(url: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    robots = RobotFileParser(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    try:
        robots.read()
    except OSError:
        return True, "robots.txt unavailable (continued)"
    return robots.can_fetch(USER_AGENT, url), "robots.txt"


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


def _download_with_curl(url: str) -> bytes:
    result = subprocess.run(
        [
            "curl.exe", "-4", "-L", "--fail", "--silent", "--show-error",
            "--connect-timeout", "20", "--max-time", "90",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            url,
        ],
        capture_output=True,
        check=True,
        timeout=120,
    )
    data = result.stdout
    if len(data) > MAX_BYTES:
        raise RuntimeError("content exceeds 60 MB limit")
    if not data.startswith(b"%PDF"):
        raise RuntimeError("curl response is not a PDF")
    return data


def _download_html(url: str) -> bytes:
    host = urlparse(url).hostname or ""
    if not any(host == suffix.lstrip(".") or host.endswith(suffix) for suffix in ALLOWED_HTML_HOSTS):
        raise RuntimeError(f"HTML host is not an allowed official domain: {host}")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise RuntimeError("content exceeds 60 MB limit")
    if b"<html" not in data.lower() and b"<!doctype" not in data.lower():
        raise RuntimeError("response is not HTML")
    return data


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--retry-unreachable", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    lock: list[dict[str, object]] = []
    for source in manifest.get("sources", []):
        source_id = source["id"]
        disease_id = source["disease_ids"][0]
        extension = "html" if source.get("type") == "html" else "pdf"
        target = ROOT / source["file"] if source.get("file") else (
            ROOT / "data" / "raw" / disease_id / f"{source_id}.{extension}"
        )
        entry: dict[str, object] = {
            "url": source["url"],
            "file": str(target.relative_to(ROOT)),
            "date": date.today().isoformat(),
        }
        try:
            if target.exists():
                data = target.read_bytes()
                valid = data.startswith(b"%PDF") if extension == "pdf" else b"<html" in data.lower()
                if valid:
                    entry.update({"status": "skipped", "hash": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
                    lock.append(entry)
                    continue
            robots_ok, robots_source = _robots_allowed(source["url"])
            if not robots_ok and not args.retry_unreachable:
                raise RuntimeError(f"robots check failed: {robots_source}")
            worked_with = "python"
            for attempt in range(3):
                try:
                    data = _download_html(source["url"]) if extension == "html" else _download(source["url"])
                    break
                except Exception:
                    if attempt == 2:
                        if extension == "html":
                            data = _download_html(source["url"])
                        else:
                            data = _download_with_curl(source["url"])
                        worked_with = "curl"
                        break
                    time.sleep(2**attempt)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            entry.update({
                "status": "downloaded",
                "hash": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "fallback": worked_with,
                "robots": robots_source,
                "type": extension,
            })
        except Exception as exc:
            logger.warning("Failed %s: %s", source_id, exc)
            entry.update({"status": "unreachable", "error": str(exc)})
        lock.append(entry)
    LOCKFILE.write_text(json.dumps(lock, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
