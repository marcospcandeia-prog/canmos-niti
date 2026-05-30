from unittest.mock import patch


class TestAiAsk:
    def test_ask_without_auth(self, client):
        response = client.post("/ai/ask", json={"pergunta": "Qual minha restituição?"})
        assert response.status_code == 401

    def test_ask_fallback_response(self, client, auth_headers):
        with patch("app.modules.ai.service.AiService._query_ollama", side_effect=Exception("Ollama offline")):
            response = client.post(
                "/ai/ask",
                headers=auth_headers,
                json={"pergunta": "restituicao"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "resposta" in data
        assert "restituição" in data["resposta"].lower()

    def test_ask_with_context(self, client, auth_headers):
        with patch("app.modules.ai.service.AiService._query_ollama", side_effect=Exception("Ollama offline")):
            response = client.post(
                "/ai/ask",
                headers=auth_headers,
                json={
                    "pergunta": "Meus documentos estão corretos?",
                    "contexto": {"fonte_extra": "teste"},
                },
            )
        assert response.status_code == 200

    def test_ask_generic_fallback(self, client, auth_headers):
        with patch("app.modules.ai.service.AiService._query_ollama", side_effect=Exception("Ollama offline")):
            response = client.post(
                "/ai/ask",
                headers=auth_headers,
                json={"pergunta": "algo completamente aleatório sem match"},
            )
        assert response.status_code == 200
        assert "contador" in response.json()["resposta"]


class TestAiHistory:
    def test_history_empty(self, client, auth_headers):
        response = client.get("/ai/history", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_history_with_data(self, client, auth_headers):
        with patch("app.modules.ai.service.AiService._query_ollama", side_effect=Exception("Ollama offline")):
            client.post("/ai/ask", headers=auth_headers, json={"pergunta": "restituicao"})

        response = client.get("/ai/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["pergunta"] == "restituicao"

    def test_history_without_auth(self, client):
        response = client.get("/ai/history")
        assert response.status_code == 401

    def test_history_respects_limit(self, client, auth_headers):
        with patch("app.modules.ai.service.AiService._query_ollama", side_effect=Exception("Ollama offline")):
            client.post("/ai/ask", headers=auth_headers, json={"pergunta": "q1"})
            client.post("/ai/ask", headers=auth_headers, json={"pergunta": "q2"})

        response = client.get("/ai/history?limit=1", headers=auth_headers)
        data = response.json()
        assert len(data) == 1
