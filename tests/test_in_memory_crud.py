import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from fastapi.testclient import TestClient
from main import app
from database import db

client = TestClient(app)

def test_list_components_seeded():
    res = client.get("/api/components")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) >= 3

def test_crud_lifecycle_in_memory():
    # 1. POST (Create)
    new_comp = {
        "name": "fastapi",
        "version": "0.100.0",
        "category": "backend"
    }
    create_res = client.post("/api/components", json=new_comp)
    assert create_res.status_code == 201
    created_item = create_res.json()
    comp_id = created_item["id"]
    assert created_item["name"] == "fastapi"
    assert created_item["version"] == "0.100.0"
    assert created_item["category"] == "backend"

    # 2. GET by ID
    get_res = client.get(f"/api/components/{comp_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == comp_id

    # 3. PUT (Update)
    update_payload = {
        "name": "fastapi",
        "version": "0.109.1",
        "category": "api-framework"
    }
    put_res = client.put(f"/api/components/{comp_id}", json=update_payload)
    assert put_res.status_code == 200
    updated_item = put_res.json()
    assert updated_item["version"] == "0.109.1"
    assert updated_item["category"] == "api-framework"

    # 4. GET verify updated state
    verify_res = client.get(f"/api/components/{comp_id}")
    assert verify_res.status_code == 200
    assert verify_res.json()["version"] == "0.109.1"

    # 5. DELETE
    del_res = client.delete(f"/api/components/{comp_id}")
    assert del_res.status_code == 200
    assert del_res.json()["id"] == comp_id

    # 6. Verify 404 after deletion
    gone_res = client.get(f"/api/components/{comp_id}")
    assert gone_res.status_code == 404

def test_update_nonexistent_component():
    res = client.put("/api/components/nonexistent-id-12345", json={"name": "test", "version": "1.0"})
    assert res.status_code == 404

def test_delete_nonexistent_component():
    res = client.delete("/api/components/nonexistent-id-12345")
    assert res.status_code == 404

def test_analyze_in_memory_database():
    res = client.post("/api/components/analyze")
    assert res.status_code == 200
    data = res.json()
    assert "findings" in data
    assert "severity_distribution" in data
    assert "upgrade_paths" in data
    assert "sources" in data
