import sys

from swasthya_setu.generation.agent import run_agent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

question = " ".join(sys.argv[1:])
result = run_agent(question)

print(f"\n=== INTENT ===\n{result.get('intent', 'emergency')}")
print("\n=== ANSWER ===")
print(result["answer"])
print("\n=== SOURCES ===")
for number in result.get("citations", []):
    document = result.get("documents", [])[number - 1]
    print(
        f"[{number}] {document.metadata.get('source')} "
        f"(page {document.metadata.get('page_label')})"
    )