import json
import urllib.request

req = urllib.request.Request(
    "https://api.github.com/repos/AlapatiAbhinavChowdhary/swasthya-setu/actions/runs?per_page=10",
    headers={"User-Agent": "Mozilla/5.0"}
)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        for run in data.get("workflow_runs", []):
            run_id = run["id"]
            head_sha = run["head_sha"][:7]
            branch = run["head_branch"]
            status = run["status"]
            conclusion = run["conclusion"]
            title = run.get("display_title", "")
            print(f"Run ID: {run_id} | SHA: {head_sha} | Branch: {branch:25} | Status: {status:11} | Conclusion: {str(conclusion):10} | {title}")

            # Also fetch jobs for the latest run
            if head_sha == "93e9297" or run == data["workflow_runs"][0]:
                jobs_url = run["jobs_url"]
                req_jobs = urllib.request.Request(jobs_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_jobs, timeout=15) as jresp:
                    jobs_data = json.loads(jresp.read().decode())
                    for job in jobs_data.get("jobs", []):
                        print(f"   -> Job '{job['name']}': status={job['status']}, conclusion={job['conclusion']}")
except Exception as e:
    print("Failed to fetch CI runs:", e)
