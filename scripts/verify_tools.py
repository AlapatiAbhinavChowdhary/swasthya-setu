from swasthya_setu.tools import outbreak_alerts, find_hospital
from swasthya_setu.generation.agent import run_agent

print("=" * 80)
print("OUTBREAK ALERTS (EN)")
print("=" * 80)
alerts_en = outbreak_alerts(disease="dengue", language="en")
print("Disclaimer:", alerts_en["disclaimer"])
print("Is demo:", alerts_en["is_demo"])
print("Count:", alerts_en["count"])
for a in alerts_en["alerts"]:
    print(f"  [{a['label']}] {a['disease']} in {a['district']}, {a['state']} ({a['date']})")
    print(f"  Advisory: {a['advisory']}")

print("\n" + "=" * 80)
print("OUTBREAK ALERTS (HI)")
print("=" * 80)
alerts_hi = outbreak_alerts(disease="dengue", language="hi")
print("Disclaimer:", alerts_hi["disclaimer"])
for a in alerts_hi["alerts"]:
    print(f"  [{a['label']}] {a['disease']} in {a['district']}, {a['state']} ({a['date']})")
    print(f"  Advisory (HI): {a['advisory_hi']}")

print("\n" + "=" * 80)
print("FIND HOSPITAL (EN)")
print("=" * 80)
hosp_en = find_hospital(district="delhi", language="en")
print("Disclaimer:", hosp_en["disclaimer"])
print("Is sample:", hosp_en["is_sample"])
print("Count:", hosp_en["count"])
for f in hosp_en["facilities"][:3]:
    print(f"  [{f['label']}] {f['name']} ({f['type']}) | Phone: {f['phone']}")

print("\n" + "=" * 80)
print("FIND HOSPITAL (HI)")
print("=" * 80)
hosp_hi = find_hospital(district="delhi", language="hi")
print("Disclaimer:", hosp_hi["disclaimer"])

print("\n" + "=" * 80)
print("AGENT DIRECT INVOCATION FOR TOOLS")
print("=" * 80)
agent_alerts = run_agent("Are there any dengue alerts in Delhi?", session_id="test-agent-alerts")
print("Intent:", agent_alerts["response"]["intent"])
print("Answer:\n", agent_alerts["response"]["answer"])

print("\n" + "=" * 80)
agent_hosp = run_agent("Find hospitals in Delhi", session_id="test-agent-hosp")
print("Intent:", agent_hosp["response"]["intent"])
print("Answer:\n", agent_hosp["response"]["answer"])
