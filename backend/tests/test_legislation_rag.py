from unittest.mock import patch

from app.modules.ai.legislation_rag import (
    IRPF_LEGISLATION,
    index_legislation,
    search_legislation,
    check_legislation_available,
)


class TestLegislationRAG:
    def test_legislation_data_exists(self):
        assert len(IRPF_LEGISLATION) >= 10
        for item in IRPF_LEGISLATION:
            assert "id" in item
            assert "titulo" in item
            assert "texto" in item
            assert "tags" in item
            assert isinstance(item["tags"], list)
            assert len(item["tags"]) > 0

    def test_legislation_ids_unique(self):
        ids = [item["id"] for item in IRPF_LEGISLATION]
        assert len(ids) == len(set(ids))

    @patch("app.modules.ai.legislation_rag.get_embeddings_client")
    @patch("app.modules.ai.legislation_rag.get_qdrant_client")
    def test_index_legislation_no_client(self, mock_client, mock_embeddings):
        mock_client.return_value = None
        result = index_legislation()
        assert result is False

    @patch("app.modules.ai.legislation_rag.get_embeddings_client")
    @patch("app.modules.ai.legislation_rag.get_qdrant_client")
    def test_search_legislation_no_client(self, mock_client, mock_embeddings):
        mock_client.return_value = None
        result = search_legislation("deducao medica")
        assert result == []

    @patch("app.modules.ai.legislation_rag.get_qdrant_client")
    def test_check_legislation_no_client(self, mock_client):
        mock_client.return_value = None
        result = check_legislation_available()
        assert result is False

    def test_legislation_content_relevant(self):
        keywords_found = set()
        expected_keywords = [
            "isencao", "dedução", "rendimento", "dependente",
            "restituição", "alíquota", "declaração",
        ]
        for item in IRPF_LEGISLATION:
            for tag in item["tags"]:
                for kw in expected_keywords:
                    if kw in tag.lower() or kw in item["texto"].lower():
                        keywords_found.add(kw)
        assert len(keywords_found) >= 5
