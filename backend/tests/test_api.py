def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_login_and_me(client, token):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "admin@example.com"
    assert resp.json()["role"] == "admin"


def test_requires_auth(client):
    assert client.get("/api/v1/documents").status_code == 401


def test_rbac_register_requires_admin(client, token):
    resp = client.post("/api/v1/auth/register",
                       headers={"Authorization": f"Bearer {token}"},
                       json={"email": "auditor@example.com", "password": "Password123!",
                             "full_name": "Aud Itor", "role": "auditor"})
    assert resp.status_code == 200


def test_dashboard_empty_ok(client, token):
    resp = client.get("/api/v1/dashboard/executive", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["page"] == "executive"
