import hashlib
import pytest
from unittest.mock import MagicMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
def mock_minio():
    """Mock MinIO service for all document tests"""
    with patch('app.modules.documents.service.get_minio_service') as mock_get:
        minio_mock = MagicMock()
        minio_mock.calculate_file_hash.side_effect = lambda f: hashlib.sha256(f.read()).hexdigest()
        minio_mock.generate_storage_path.return_value = "users/1/documents/test.pdf"
        minio_mock.upload_file.return_value = None
        minio_mock.delete_file.return_value = None
        minio_mock.get_presigned_url.return_value = "https://minio.test/url"
        mock_get.return_value = minio_mock
        yield mock_get


@pytest.mark.asyncio
async def test_upload_unauthorized(client: AsyncClient):
    response = await client.post(
        "/documents/upload",
        files={"file": ("test.pdf", b"content", "application/pdf")}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_success(auth_client: AsyncClient):
    file_content = b"fake pdf content for testing"
    response = await auth_client.post(
        "/documents/upload",
        files={"file": ("nota-fiscal.pdf", file_content, "application/pdf")}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nome_original"] == "nota-fiscal.pdf"
    assert data["mime_type"] == "application/pdf"
    assert data["status"] == "uploaded"
    assert "id" in data
    assert data["user_id"] is not None


@pytest.mark.asyncio
async def test_upload_invalid_mime_type(auth_client: AsyncClient):
    response = await auth_client.post(
        "/documents/upload",
        files={"file": ("script.exe", b"bad", "application/x-msdownload")}
    )
    assert response.status_code == 400
    assert "não suportado" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_empty_file(auth_client: AsyncClient):
    response = await auth_client.post(
        "/documents/upload",
        files={"file": ("vazio.pdf", b"", "application/pdf")}
    )
    assert response.status_code == 400
    assert "vazio" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_unauthorized(client: AsyncClient):
    response = await client.get("/documents")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_documents_empty(auth_client: AsyncClient):
    response = await auth_client.get("/documents")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_documents_after_upload(auth_client: AsyncClient):
    await auth_client.post(
        "/documents/upload",
        files={"file": ("doc1.pdf", b"content1", "application/pdf")}
    )
    await auth_client.post(
        "/documents/upload",
        files={"file": ("doc2.png", b"content2", "image/png")}
    )

    response = await auth_client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [d["nome_original"] for d in data]
    assert "doc1.pdf" in names
    assert "doc2.png" in names


@pytest.mark.asyncio
async def test_get_document_by_id(auth_client: AsyncClient):
    upload_resp = await auth_client.post(
        "/documents/upload",
        files={"file": ("find-me.pdf", b"content", "application/pdf")}
    )
    doc_id = upload_resp.json()["id"]

    response = await auth_client.get(f"/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
    assert data["nome_original"] == "find-me.pdf"


@pytest.mark.asyncio
async def test_get_document_not_found(auth_client: AsyncClient):
    response = await auth_client.get("/documents/99999")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_document(auth_client: AsyncClient):
    upload_resp = await auth_client.post(
        "/documents/upload",
        files={"file": ("delete-me.pdf", b"content", "application/pdf")}
    )
    doc_id = upload_resp.json()["id"]

    response = await auth_client.delete(f"/documents/{doc_id}")
    assert response.status_code == 200
    assert "sucesso" in response.json()["message"]

    get_response = await auth_client.get(f"/documents/{doc_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_document_not_found(auth_client: AsyncClient):
    response = await auth_client.delete("/documents/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_download_url(auth_client: AsyncClient):
    upload_resp = await auth_client.post(
        "/documents/upload",
        files={"file": ("download-me.pdf", b"content", "application/pdf")}
    )
    doc_id = upload_resp.json()["id"]

    response = await auth_client.get(f"/documents/{doc_id}/download")
    assert response.status_code == 200
    data = response.json()
    assert "download_url" in data
    assert data["download_url"] == "https://minio.test/url"
    assert data["expires_in"] == 3600


@pytest.mark.asyncio
async def test_get_download_url_not_found(auth_client: AsyncClient):
    response = await auth_client.get("/documents/99999/download")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_stats_empty(auth_client: AsyncClient):
    response = await auth_client.get("/documents/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["uploaded"] == 0
    assert data["by_type"] == {}


@pytest.mark.asyncio
async def test_get_stats_with_documents(auth_client: AsyncClient):
    await auth_client.post(
        "/documents/upload",
        files={"file": ("doc1.pdf", b"content1", "application/pdf")}
    )
    await auth_client.post(
        "/documents/upload",
        files={"file": ("doc2.png", b"content2", "image/png")}
    )

    response = await auth_client.get("/documents/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["uploaded"] == 2
