from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_docs():
    assert client.get("/docs").status_code == 200

def test_login_page():
    assert client.get("/login").status_code == 200

def test_perfil_requiere_token():
    assert client.get("/api/v1/users/me").status_code == 401