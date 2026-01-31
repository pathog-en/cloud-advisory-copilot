from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()


def test_rules_returns_list():
    r = client.get("/rules")
    assert r.status_code == 200
    data = r.json()
    assert "count" in data and "rules" in data
    assert isinstance(data["rules"], list)


def test_assess_post_works():
    payload = {
        "workload_type": "web_api",
        "environment": "prod",
        "traffic_profile": "spiky",
        "availability_target": "high",
        "rto_minutes": 15,
        "rpo_minutes": 5,
        "data_sensitivity": "confidential",
        "budget_priority": "balanced",
        "team_experience": "mixed",
        "constraints": ["no k8s"],
        "notes": "test",
        "provider_hints": {"trace": True},
    }

    r = client.post("/assess", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "scores" in body
    assert "recommendations" in body
    assert body["meta"]["trace_enabled"] is True
    assert body.get("trace") is not None
