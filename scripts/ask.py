import sys

from swasthya_setu.config import check_llm_configured

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

is_configured, missing_var = check_llm_configured()
if not is_configured:
    sys.exit(f"Error: Required LLM setting '{missing_var}' is missing or set to a placeholder.")

from swasthya_setu.generation.agent import run_agent

question = " ".join(sys.argv[1:])
if not question.strip():
    sys.exit("Error: No question provided.")

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
