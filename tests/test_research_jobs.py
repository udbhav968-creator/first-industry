import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_research_job_success():
    """Milestone 6.3: POST /research-jobs with valid stack returns 202 and job_id."""
    payload = {
        "stack": [
            {"name": "react", "version": "17.0.2"},
            {"name": "node", "version": "14.17.0"}
        ]
    }
    response = client.post("/research-jobs", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "report_id" in data
    assert len(data["stack"]) == 2

def test_create_research_job_invalid_empty_stack():
    """Milestone 6.3 validation test: Empty stack rejected with 422."""
    payload = {"stack": []}
    response = client.post("/research-jobs", json=payload)
    assert response.status_code == 422

def test_get_research_job_by_id():
    """Milestone 6.4: GET /research-jobs/{id} returns job metadata."""
    payload = {
        "stack": [{"name": "express", "version": "4.17.1"}]
    }
    create_res = client.post("/research-jobs", json=payload)
    job_id = create_res.json()["job_id"]

    get_res = client.get(f"/research-jobs/{job_id}")
    assert get_res.status_code == 200
    assert get_res.json()["job_id"] == job_id
    assert get_res.json()["status"] == "queued"

def test_get_nonexistent_job_returns_404():
    """Milestone 4.6 error contract: 404 for nonexistent job id."""
    response = client.get("/research-jobs/job-does-not-exist")
    assert response.status_code == 404

def test_get_report_details():
    """Milestone 4.5: GET /reports/{id} returns findings, upgrade paths, and sources."""
    payload = {
        "stack": [{"name": "fastapi", "version": "0.100.0"}]
    }
    create_res = client.post("/research-jobs", json=payload)
    report_id = create_res.json()["report_id"]

    report_res = client.get(f"/reports/{report_id}")
    assert report_res.status_code == 200
    report_data = report_res.json()

    assert "findings" in report_data
    assert "upgrade_paths" in report_data
    assert "sources" in report_data
    assert "severity_distribution" in report_data
    assert len(report_data["findings"]) == 1
    assert report_data["findings"][0]["component"] == "fastapi"
