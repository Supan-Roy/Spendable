from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint returns HTML when frontend is built or JSON metadata otherwise."""
    response = client.get("/")
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    if "text/html" in content_type:
        assert "<!html" in response.text.lower() or "<!doctype html>" in response.text.lower() or "<html" in response.text.lower()
    else:
        data = response.json()
        assert data["project"] == "Spendable"
        assert "health_check" in data



def test_health_endpoint():
    """Verify health check endpoint returns 200 and expected metadata structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert data["app_name"] == "Spendable API"
    assert "database" in data
    assert "services" in data
