from unittest.mock import patch, MagicMock

from app.modules.ai.rag_service import (
    _chunk_text,
    ensure_collection,
    index_document,
    search_similar,
    delete_document_vectors,
)


class TestChunkText:
    def test_chunk_small_text(self):
        text = "palavra1 palavra2 palavra3"
        chunks = _chunk_text(text, chunk_size=10, overlap=2)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_large_text(self):
        words = [f"palavra{i}" for i in range(100)]
        text = " ".join(words)
        chunks = _chunk_text(text, chunk_size=50, overlap=10)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk.split()) <= 50

    def test_chunk_empty_text(self):
        chunks = _chunk_text("")
        assert chunks == []

    def test_chunk_overlap(self):
        words = [f"w{i}" for i in range(20)]
        text = " ".join(words)
        chunks = _chunk_text(text, chunk_size=10, overlap=3)
        assert len(chunks) >= 2

    def test_chunk_preserves_order(self):
        words = [f"w{i}" for i in range(30)]
        text = " ".join(words)
        chunks = _chunk_text(text, chunk_size=15, overlap=5)
        assert "w0" in chunks[0]
        assert "w29" in chunks[-1]


class TestRagService:
    @patch("app.modules.ai.rag_service.get_qdrant_client")
    def test_index_document_no_client(self, mock_client):
        mock_client.return_value = None
        result = index_document(1, 1, "texto teste")
        assert result is False

    @patch("app.modules.ai.rag_service.get_embeddings_client")
    @patch("app.modules.ai.rag_service.get_qdrant_client")
    def test_index_document_no_embeddings(self, mock_client, mock_embeddings):
        mock_client.return_value = MagicMock()
        mock_embeddings.return_value = None
        result = index_document(1, 1, "texto teste")
        assert result is False

    @patch("app.modules.ai.rag_service.get_qdrant_client")
    def test_search_similar_no_client(self, mock_client):
        mock_client.return_value = None
        result = search_similar("teste", 1)
        assert result == []

    @patch("app.modules.ai.rag_service.get_embeddings_client")
    @patch("app.modules.ai.rag_service.get_qdrant_client")
    def test_search_similar_no_embeddings(self, mock_client, mock_embeddings):
        mock_client.return_value = MagicMock()
        mock_embeddings.return_value = None
        result = search_similar("teste", 1)
        assert result == []

    @patch("app.modules.ai.rag_service.get_qdrant_client")
    def test_delete_document_vectors_no_client(self, mock_client):
        mock_client.return_value = None
        result = delete_document_vectors(1)
        assert result is False

    @patch("app.modules.ai.rag_service.get_qdrant_client")
    def test_ensure_collection_no_client(self, mock_client):
        mock_client.return_value = None
        result = ensure_collection()
        assert result is False
