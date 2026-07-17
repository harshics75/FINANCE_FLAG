import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["APP_ENV"] = "development"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def token(client):
    resp = client.post("/api/v1/auth/login",
                       data={"username": "admin@example.com", "password": "ChangeMe123!"})
    return resp.json()["access_token"]
