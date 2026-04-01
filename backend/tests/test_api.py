from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}

def test_get_job_status_not_found():
    response = client.get("/api/job/invalid_id")
    assert response.status_code == 404
    
def test_generate_requires_api_key():
    # Attempting to post without required form fields should yield 422
    response = client.post("/api/generate")
    assert response.status_code == 422
