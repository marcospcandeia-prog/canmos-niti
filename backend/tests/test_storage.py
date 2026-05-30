import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from minio import Minio

from app.modules.storage.service import StorageService


def run_async(coro):
    return asyncio.run(coro)


class TestStorageLocalMode:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        with patch("app.modules.storage.service.StorageService._minio_available", return_value=False):
            self.service = StorageService(base_path=str(tmp_path / "storage"))
            yield

    def test_upload_local(self):
        content = b"test content"
        path = run_async(self.service.upload("u1", "test.pdf", content, "application/pdf"))
        saved = Path(path).read_bytes()
        assert saved == content

    def test_download_local(self):
        content = b"download test"
        path = run_async(self.service.upload("u1", "dl.pdf", content, "application/pdf"))
        downloaded = run_async(self.service.download(path))
        assert downloaded == content

    def test_delete_local(self):
        content = b"to delete"
        path = run_async(self.service.upload("u1", "del.pdf", content, "application/pdf"))
        run_async(self.service.delete(path))
        assert not Path(path).exists()

    def test_delete_missing_local(self):
        run_async(self.service.delete("/nonexistent/file.pdf"))


class TestStorageMinioMode:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.mock_client = MagicMock(spec=Minio)
        self.mock_client.bucket_exists.return_value = True
        with (
            patch("app.modules.storage.service.StorageService._minio_available", return_value=True),
            patch("app.modules.storage.service.Minio", return_value=self.mock_client),
        ):
            self.service = StorageService(base_path=str(tmp_path / "storage"))
            yield

    def test_upload_minio(self):
        run_async(self.service.upload("u1", "test.pdf", b"content", "application/pdf"))
        self.mock_client.put_object.assert_called_once()

    def test_download_minio(self):
        self.mock_client.get_object.return_value.read.return_value = b"minio data"
        data = run_async(self.service.download("u1/test.pdf"))
        assert data == b"minio data"

    def test_delete_minio(self):
        run_async(self.service.delete("u1/test.pdf"))
        self.mock_client.remove_object.assert_called_once()

    def test_get_url_minio(self):
        self.mock_client.presigned_get_object.return_value = "http://presigned.url"
        url = self.service.get_url("u1/test.pdf")
        assert url == "http://presigned.url"

    def test_get_url_local(self):
        with patch("app.modules.storage.service.StorageService._minio_available", return_value=False):
            service = StorageService(base_path=str(Path.cwd()))
            url = service.get_url("local/path.pdf")
        assert url == "local/path.pdf"
