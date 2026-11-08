"""Fetch WHO Fact Sheet Index and find exact links for target diseases."""

import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Load diseases
diseases = yaml.safe_load((ROOT / "data" / "diseases.yaml").read_text(encoding="utf-8"))["diseases"]

print(f"Loaded {len(diseases)} target diseases.")

req = urllib.request.Request(
    "https://www.who.int/news-room/fact-sheets",
    headers={"User-Agent": USER_AGENT}
)

with urllib.request.urlopen(req, timeout=30) as resp:
    raw_html = resp.read().decode("utf-8", errors="replace")

link_pattern = re.compile(
    r'<a[^>]+href=["\'](/news-room/fact-sheets/detail/([^"\']+))["\'][^>]*>(.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)

links = {}
for m in link_pattern.finditer(raw_html):
    href, slug, inner_text = m.group(1), m.group(2).strip("/"), m.group(3)
    clean_title = html.unescape(re.sub(r"<[^>]+>", "", inner_text)).strip()
    full_url = urllib.parse.urljoin("https://www.who.int", href)
    if slug and slug not in links:
        links[slug] = {"url": full_url, "title": clean_title}

print(f"Discovered {len(links)} WHO fact sheet links from index page.")

out_file = ROOT / "logs" / "who_fact_sheets_discovered.json"
out_file.parent.mkdir(parents=True, exist_ok=True)
out_file.write_text(json.dumps(links, indent=2), encoding="utf-8")
print(f"Saved discovered links to {out_file}")

# Print count and first 20
print(f"Total discovered: {len(links)}")
