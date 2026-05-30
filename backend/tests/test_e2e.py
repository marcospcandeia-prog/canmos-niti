import io

from app.modules.tax_engine.service import TaxEngine


class TestFullE2EFlow:
    def test_register_upload_calculate_dashboard(self, client, test_user_data):
        # 1. Register
        reg = client.post("/auth/register", json=test_user_data)
        assert reg.status_code == 201

        # 2. Login
        login = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "senha": test_user_data["senha"],
        })
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Upload document
        upload = client.post(
            "/documents/upload",
            headers=headers,
            files={"file": ("contracheque.pdf", io.BytesIO(b"Rendimento: 5000.00 IRRF 750.00"), "application/pdf")},
            data={"tipo": "infr"},
        )
        assert upload.status_code == 201
        doc_id = upload.json()["id"]

        # 4. Get document detail
        detail = client.get(f"/documents/{doc_id}", headers=headers)
        assert detail.status_code == 200
        assert detail.json()["id"] == doc_id

        # 5. Upload more documents for a complete scenario
        for i in range(2):
            client.post(
                "/documents/upload",
                headers=headers,
                files={"file": (f"doc{i}.pdf", io.BytesIO(b"content"), "application/pdf")},
            )

        # 6. List documents
        docs = client.get("/documents", headers=headers)
        assert docs.status_code == 200
        assert len(docs.json()) == 3

        # 7. Get profile
        profile = client.get("/auth/me", headers=headers)
        assert profile.status_code == 200
        assert profile.json()["email"] == test_user_data["email"]

        # 8. Dashboard
        dash = client.get("/dashboard/summary", headers=headers)
        assert dash.status_code == 200
        assert dash.json()["total_documents"] == 3

        # 9. Delete a document
        delete = client.delete(f"/documents/{doc_id}", headers=headers)
        assert delete.status_code == 204

        # 10. Verify deletion
        docs_after = client.get("/documents", headers=headers)
        assert len(docs_after.json()) == 2

    def test_tax_engine_api_flow(self, client, db, test_user, auth_headers):
        tax_events_data = [
            {"categoria": "rendimento", "subcategoria": "Salario", "valor": 50000.0},
            {"categoria": "retencao", "subcategoria": "IRRF", "valor": 7500.0},
            {"categoria": "inss", "subcategoria": "INSS", "valor": 4500.0},
        ]

        from app.shared.models.document import TaxEvent

        for event_data in tax_events_data:
            event = TaxEvent(
                user_id=test_user.id,
                document_id="e2e-test",
                categoria=event_data["categoria"],
                subcategoria=event_data["subcategoria"],
                valor=event_data["valor"],
            )
            db.add(event)
        db.commit()

        engine = TaxEngine(db)
        decl = engine.calculate(test_user.id, str(test_user.created_at.year))
        assert decl is not None
        assert decl.total_rendimentos == 50000.0
        assert decl.total_retencao == 7500.0

        validations = engine.get_validations(decl.id)
        assert isinstance(validations, list)

    def test_audit_log_exists(self, client, auth_headers):
        client.get("/dashboard", headers=auth_headers)
        audit = client.get("/audit", headers=auth_headers)
        assert audit.status_code == 200
        logs = audit.json()
        actions = [log["action"] for log in logs]
        assert "register" in actions

    def test_ai_history_flow(self, client, auth_headers):
        from unittest.mock import patch

        with patch("app.modules.ai.service.AiService._query_ollama", side_effect=Exception("offline")):
            ask = client.post("/ai/ask", headers=auth_headers, json={"pergunta": "restituicao"})
        assert ask.status_code == 200

        history = client.get("/ai/history", headers=auth_headers)
        assert history.status_code == 200
        assert len(history.json()) >= 1
