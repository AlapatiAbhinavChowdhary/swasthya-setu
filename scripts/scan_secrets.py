import re
import subprocess
import sys
from pathlib import Path

# Patterns for Google API keys / Gemini tokens
PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    re.compile(r"\bAQ\.[0-9A-Za-z_-]+\b"),
]

def scan_text(text: str) -> int:
    matches = 0
    for p in PATTERNS:
        matches += len(p.findall(text))
    return matches

print("=== Working Tree Secret Scan ===")
working_tree_matches = {}

for p in Path(".").rglob("*"):
    if not p.is_file():
        continue
    # Skip ignored dirs and local ignored .env
    parts = p.parts
    if any(d in parts for d in [".git", "node_modules", ".venv", "vectorstore", "logs", "dist", ".cache", "__pycache__"]):
        continue
    if p.name == ".env":
        continue
    if p.suffix in [".png", ".jpg", ".pdf", ".db", ".sqlite", ".sqlite3", ".pkl"]:
        continue
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")
        count = scan_text(content)
        if count > 0:
            working_tree_matches[str(p)] = count
    except Exception:
        pass

print(f"Working tree scan complete. Non-ignored files with matches: {len(working_tree_matches)}")
for fn, count in working_tree_matches.items():
    print(f"  {fn}: {count} match(es)")

print("\n=== Git History Secret Scan (All Branches) ===")
commit_matches = {}

try:
    log_proc = subprocess.run(
        ["git", "log", "--all", "--pretty=format:%H", "-p", "--", ":(exclude)*.png", ":(exclude)*.pdf"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    current_commit = None

    for line in log_proc.stdout.splitlines():
        if re.match(r"^[0-9a-f]{40}$", line):
            current_commit = line[:8]
        elif line.startswith("+") and not line.startswith("+++"):
            count = scan_text(line[1:])
            if count > 0 and current_commit:
                commit_matches[current_commit] = commit_matches.get(current_commit, 0) + count

    print(f"Git history scan complete. Commits with matches: {len(commit_matches)}")
    for c, count in commit_matches.items():
        print(f"  commit {c}: {count} match(es)")

except Exception as exc:
    print(f"Git history scan error: {exc}")

if working_tree_matches or commit_matches:
    print("\n[FAILED] Secret patterns found!")
    sys.exit(1)
else:
    print("\n[PASSED] Zero secrets found in working tree or git history.")
    sys.exit(0)
