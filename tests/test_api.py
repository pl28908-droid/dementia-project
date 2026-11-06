from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_landing_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "SMARAN" in response.text
