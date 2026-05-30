import io


class TestDocumentUpload:
    def test_upload_success(self, client, auth_headers):
        file_content = b"test document content"
        response = client.post(
            "/documents/upload",
            headers=auth_headers,
            files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")},
            data={"tipo": "infr"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nome_original"] == "test.pdf"
        assert data["status"] in ("pending", "processing", "completed")

    def test_upload_without_auth(self, client):
        file_content = b"test"
        response = client.post(
            "/documents/upload",
            files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")},
        )
        assert response.status_code == 401


class TestDocumentList:
    def test_list_documents_empty(self, client, auth_headers):
        response = client.get("/documents", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_documents_with_data(self, client, auth_headers):
        client.post(
            "/documents/upload",
            headers=auth_headers,
            files={"file": ("doc1.pdf", io.BytesIO(b"content1"), "application/pdf")},
        )
        client.post(
            "/documents/upload",
            headers=auth_headers,
            files={"file": ("doc2.pdf", io.BytesIO(b"content2"), "application/pdf")},
        )
        response = client.get("/documents", headers=auth_headers)
        assert response.status_code == 200
        docs = response.json()
        assert len(docs) == 2


class TestDocumentDetail:
    def test_get_detail_nonexistent(self, client, auth_headers):
        response = client.get("/documents/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    def test_get_detail_success(self, client, auth_headers):
        upload_resp = client.post(
            "/documents/upload",
            headers=auth_headers,
            files={"file": ("test.pdf", io.BytesIO(b"content"), "application/pdf")},
        )
        doc_id = upload_resp.json()["id"]

        response = client.get(f"/documents/{doc_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == doc_id
        assert "ocr_result" in data
        assert "tax_events" in data


class TestDocumentDelete:
    def test_delete_success(self, client, auth_headers):
        upload_resp = client.post(
            "/documents/upload",
            headers=auth_headers,
            files={"file": ("doc.pdf", io.BytesIO(b"content"), "application/pdf")},
        )
        doc_id = upload_resp.json()["id"]

        response = client.delete(f"/documents/{doc_id}", headers=auth_headers)
        assert response.status_code == 204

        get_resp = client.get(f"/documents/{doc_id}", headers=auth_headers)
        assert get_resp.status_code == 404

    def test_delete_nonexistent(self, client, auth_headers):
        response = client.delete("/documents/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_other_user_document(self, client, test_user_data):
        client.post("/auth/register", json=test_user_data)
        login1 = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "senha": test_user_data["senha"],
        })
        h1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}

        upload_resp = client.post(
            "/documents/upload", headers=h1,
            files={"file": ("doc.pdf", io.BytesIO(b"content"), "application/pdf")},
        )
        doc_id = upload_resp.json()["id"]

        outro = {"nome": "Outro", "cpf": "99571750255", "email": "outro@email.com", "senha": "senha456"}
        client.post("/auth/register", json=outro)
        login2 = client.post("/auth/login", json={"email": outro["email"], "senha": outro["senha"]})
        h2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

        response = client.delete(f"/documents/{doc_id}", headers=h2)
        assert response.status_code == 404

    def test_delete_without_auth(self, client):
        response = client.delete("/documents/some-id")
        assert response.status_code == 401


class TestDocumentIsolation:
    def test_user_cannot_access_other_document(self, client, test_user_data):
        client.post("/auth/register", json=test_user_data)
        login1 = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "senha": test_user_data["senha"],
        })
        headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}

        upload_resp = client.post(
            "/documents/upload",
            headers=headers1,
            files={"file": ("doc.pdf", io.BytesIO(b"content"), "application/pdf")},
        )
        doc_id = upload_resp.json()["id"]

        outro_user = {
            "nome": "Outro User",
            "cpf": "99571750255",
            "email": "outro@email.com",
            "senha": "senha456",
        }
        client.post("/auth/register", json=outro_user)
        login2 = client.post("/auth/login", json={
            "email": outro_user["email"],
            "senha": outro_user["senha"],
        })
        headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

        response = client.get(f"/documents/{doc_id}", headers=headers2)
        assert response.status_code == 404
