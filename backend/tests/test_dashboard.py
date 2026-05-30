import io


class TestDashboardSummary:
    def test_summary_empty(self, client, auth_headers):
        response = client.get("/dashboard/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_documents"] == 0
        assert data["total_tax_events"] == 0
        assert data["restituicao_estimada"] == 0.0
        assert data["alertas"] == 0

    def test_summary_after_upload(self, client, auth_headers):
        client.post(
            "/documents/upload",
            headers=auth_headers,
            files={"file": ("rendimento.pdf", io.BytesIO(b"salario 5000"), "application/pdf")},
        )
        response = client.get("/dashboard/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_documents"] == 1
        assert data["documents_by_status"] != {}

    def test_summary_isolation(self, client, auth_headers):
        client.post(
            "/documents/upload",
            headers=auth_headers,
            files={"file": ("doc.pdf", io.BytesIO(b"content"), "application/pdf")},
        )
        outro_user = {
            "nome": "Isolado",
            "cpf": "27904714361",
            "email": "isolado@email.com",
            "senha": "senha456",
        }
        client.post("/auth/register", json=outro_user)
        login = client.post("/auth/login", json={
            "email": "isolado@email.com",
            "senha": "senha456",
        })
        headers2 = {"Authorization": f"Bearer {login.json()['access_token']}"}

        response = client.get("/dashboard/summary", headers=headers2)
        assert response.json()["total_documents"] == 0
