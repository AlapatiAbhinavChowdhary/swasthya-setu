import json
import urllib.request

COMMITS = ["1fe5926", "4431520"]

def check_runs():
    url = "https://api.github.com/repos/AlapatiAbhinavChowdhary/swasthya-setu/actions/runs?per_page=20"
    req = urllib.request.Request(url, headers={"User-Agent": "Python/3.12", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error fetching runs: {e}")
        return

    runs = data.get("workflow_runs", [])
    print(f"Found {len(runs)} total workflow runs in API response.\n")
    
    target_runs = [r for r in runs if any(r["head_sha"].startswith(c) for c in COMMITS)]
    if not target_runs:
        print("No target runs found matching commits:", COMMITS)
        print("Recent runs in repo:")
        for r in runs[:5]:
            print(f"  Run ID: {r['id']}, SHA: {r['head_sha'][:7]}, Status: {r['status']}, Conclusion: {r['conclusion']}, Branch: {r.get('head_branch')}")
        return

    for r in target_runs:
        run_id = r["id"]
        head_sha = r["head_sha"][:7]
        branch = r.get("head_branch")
        status = r["status"]
        conclusion = r["conclusion"]
        created = r["created_at"]
        print(f"=== Workflow Run ID: {run_id} ===")
        print(f"  Commit: {head_sha} ({branch})")
        print(f"  Status: {status} | Conclusion: {conclusion}")
        print(f"  Created At: {created}")
        print(f"  HTML URL: {r.get('html_url')}")
        
        # Now fetch individual jobs for this run
        jobs_url = r.get("jobs_url")
        if jobs_url:
            jreq = urllib.request.Request(jobs_url, headers={"User-Agent": "Python/3.12", "Accept": "application/vnd.github+json"})
            try:
                with urllib.request.urlopen(jreq, timeout=15) as jresp:
                    jdata = json.loads(jresp.read().decode())
                    jobs = jdata.get("jobs", [])
                    print(f"  Jobs ({len(jobs)}):")
                    for job in jobs:
                        print(f"    - Job ID: {job['id']} | Name: {job['name']} | Status: {job['status']} | Conclusion: {job['conclusion']}")
            except Exception as je:
                print(f"  Failed to fetch jobs: {je}")
        print()

if __name__ == "__main__":
    check_runs()

