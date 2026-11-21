import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_research_job():
    payload = {
        "stack": [
            {"name": "react", "version": "17.0.2"},
            {"name": "node", "version": "18.15.0"}
        ]
    }
    response = client.post("/research-jobs", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "report_id" in data
    assert len(data["stack"]) == 2

def test_create_research_job_empty_payload():
    response = client.post("/research-jobs", json={"stack": []})
    assert response.status_code == 422

def test_get_research_job():
    payload = {"stack": [{"name": "node", "version": "18.15.0"}]}
    create_res = client.post("/research-jobs", json=payload)
    job_id = create_res.json()["job_id"]

    res = client.get(f"/research-jobs/{job_id}")
    assert res.status_code == 200
    assert res.json()["job_id"] == job_id
    assert res.json()["status"] == "queued"

def test_get_nonexistent_job():
    res = client.get("/research-jobs/missing-id")
    assert res.status_code == 404

def test_get_report():
    payload = {"stack": [{"name": "fastapi", "version": "0.100.0"}]}
    create_res = client.post("/research-jobs", json=payload)
    report_id = create_res.json()["report_id"]

    res = client.get(f"/reports/{report_id}")
    assert res.status_code == 200
    data = res.json()
    assert "findings" in data
    assert "upgrade_paths" in data
    assert "sources" in data
    assert len(data["findings"]) == 1
