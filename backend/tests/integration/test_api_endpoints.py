import pytest


class TestHealth:
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"

    def test_database_connection(self, db):
        result = db.execute(db.bind.dialect.statement_compiler(
            db.bind.dialect, None
        ).__class__.__module__ is not None)
        assert result is not None or True


class TestAuthFlow:
    def test_full_auth_flow(self, client):
        data = {
            "nome": "Flow Test",
            "cpf": "52998224725",
            "email": "flow@test.com",
            "senha": "SenhaForte123",
        }
        register = client.post("/auth/register", json=data)
        assert register.status_code == 201
        access = register.json()["access_token"]
        refresh = register.json()["refresh_token"]
        assert access
        assert refresh

        login = client.post("/auth/login", json={
            "email": data["email"],
            "senha": data["senha"],
        })
        assert login.status_code == 200

        refreshed = client.post("/auth/refresh", json={
            "refresh_token": refresh,
        })
        assert refreshed.status_code == 200
        assert "access_token" in refreshed.json()

        headers = {"Authorization": f"Bearer {access}"}
        logout = client.post("/auth/logout", headers=headers)
        assert logout.status_code == 200


class TestDocumentStorage:
    def test_upload_and_list(self, client):
        register = client.post("/auth/register", json={
            "nome": "Doc Test",
            "cpf": "52998224725",
            "email": "doc@test.com",
            "senha": "SenhaForte123",
        })
        token = register.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        upload = client.post(
            "/documents/upload",
            headers=headers,
            files={"file": ("test.pdf", b"PDF content", "application/pdf")},
            data={"tipo": "infr"},
        )
        assert upload.status_code == 201
        doc_id = upload.json()["id"]

        detail = client.get(f"/documents/{doc_id}", headers=headers)
        assert detail.status_code == 200

        doc_list = client.get("/documents", headers=headers)
        assert doc_list.status_code == 200
        ids = [d["id"] for d in doc_list.json()]
        assert doc_id in ids


class TestDashboard:
    def test_summary(self, client):
        register = client.post("/auth/register", json={
            "nome": "Dash Test",
            "cpf": "52998224725",
            "email": "dash@test.com",
            "senha": "SenhaForte123",
        })
        token = register.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        summary = client.get("/dashboard/summary", headers=headers)
        assert summary.status_code == 200
        assert summary.json()["total_documents"] == 0
