import json
import urllib.request
import urllib.error
import sys

BASE_URL = "http://127.0.0.1:8000"

def do_req(method, endpoint, body=None):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    if body is not None:
        req.data = json.dumps(body).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            try:
                data = json.loads(content)
            except Exception:
                data = content[:200]
            return resp.status, data
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            data = json.loads(content)
        except Exception:
            data = content[:200]
        return e.code, data

tests = [
    # 1. Health
    ("1. Liveness Health Check", "GET", "/health", None, 200),
    # 2. Create Job Multi-Stack
    ("2. Create Research Job (Multi-Component)", "POST", "/research-jobs", {
        "stack": [
            {"name": "react", "version": "17.0.2"},
            {"name": "node", "version": "18.15.0"},
            {"name": "postgres", "version": "12.0"}
        ]
    }, 202),
    # 3. Create Job Single Stack
    ("3. Create Research Job (Single Component)", "POST", "/research-jobs", {
        "stack": [{"name": "fastapi", "version": "0.100.0"}]
    }, 202),
    # 4. Validation: Empty stack
    ("4. Validation Failure: Empty Stack Array", "POST", "/research-jobs", {"stack": []}, 422),
    # 5. Validation: Bad type
    ("5. Validation Failure: Invalid Payload Type", "POST", "/research-jobs", {"stack": "invalid"}, 422),
    # 6. List Jobs
    ("6. List Jobs with Pagination (page 1, limit 2)", "GET", "/research-jobs?page=1&limit=2", None, 200),
    # 7. List Jobs Filtered
    ("7. List Jobs Filtered by Status (queued)", "GET", "/research-jobs?status=queued", None, 200),
    # 8. Missing Job
    ("8. Get Nonexistent Job ID (404 expected)", "GET", "/research-jobs/missing-job-xyz", None, 404),
    # 9. Missing Report
    ("9. Get Nonexistent Report ID (404 expected)", "GET", "/reports/missing-rep-xyz", None, 404),
    # 10. OpenAPI Schema
    ("10. OpenAPI 3.1 Contract JSON", "GET", "/openapi.json", None, 200),
    # 11. Swagger UI
    ("11. Interactive Swagger UI (/docs)", "GET", "/docs", None, 200),
    # 12. ReDoc UI
    ("12. Interactive ReDoc UI (/redoc)", "GET", "/redoc", None, 200),
]

print("=================================================================")
print("          FASTAPI BACKEND COMPLETE ENDPOINT TEST SUITE           ")
print("=================================================================")

passed = 0
failed = 0
created_job_id = None
created_report_id = None

for name, method, path, body, expected_status in tests:
    status, res = do_req(method, path, body)
    if status == expected_status:
        print(f"✅ PASS | {method:<4} {path:<38} -> HTTP {status}")
        passed += 1
        if "Multi-Component" in name and isinstance(res, dict):
            created_job_id = res.get("job_id")
            created_report_id = res.get("report_id")
    else:
        print(f"❌ FAIL | {method:<4} {path:<38} -> Got HTTP {status}, expected {expected_status}")
        failed += 1

# Test Dynamic Job Retrieval
if created_job_id:
    status, res = do_req("GET", f"/research-jobs/{created_job_id}")
    if status == 200 and res.get("job_id") == created_job_id:
        print(f"✅ PASS | GET  /research-jobs/{{job_id}}                 -> HTTP 200 (Job ID: {created_job_id})")
        passed += 1
    else:
        print(f"❌ FAIL | GET  /research-jobs/{{job_id}}                 -> Got HTTP {status}")
        failed += 1

# Test Dynamic Report Retrieval
if created_report_id:
    status, res = do_req("GET", f"/reports/{created_report_id}")
    if status == 200 and "findings" in res and "upgrade_paths" in res:
        print(f"✅ PASS | GET  /reports/{{report_id}}                     -> HTTP 200 (Report ID: {created_report_id})")
        print(f"         ├─ Total Findings: {len(res.get('findings', []))}")
        print(f"         ├─ Upgrade Paths:  {len(res.get('upgrade_paths', []))}")
        print(f"         ├─ Severity:       {res.get('severity_distribution')}")
        print(f"         └─ Sources:        {len(res.get('sources', []))} reference URLs")
        passed += 1
    else:
        print(f"❌ FAIL | GET  /reports/{{report_id}}                     -> Got HTTP {status}")
        failed += 1

print("=================================================================")
print(f"Test Summary: {passed} passed, {failed} failed out of {passed + failed} checks.")
print("=================================================================")
sys.exit(0 if failed == 0 else 1)
