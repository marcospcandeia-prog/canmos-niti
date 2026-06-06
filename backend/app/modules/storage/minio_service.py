"""
MinIO Storage Service
S3-compatible object storage for documents
"""

import hashlib
import io
from datetime import timedelta
from typing import BinaryIO, Optional

from minio import Minio
from minio.error import S3Error

from app.core.config.settings import get_settings

settings = get_settings()


class MinIOService:
    """MinIO storage service"""
    
    def __init__(self):
        """Initialize MinIO client"""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Ensure bucket exists, create if not"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"✓ MinIO bucket '{self.bucket_name}' created")
            else:
                print(f"✓ MinIO bucket '{self.bucket_name}' exists")
        except S3Error as e:
            print(f"✗ Error ensuring bucket exists: {e}")
            raise
    
    def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str,
        file_size: int
    ) -> str:
        """
        Upload file to MinIO
        
        Args:
            file_data: File binary data
            object_name: Object name in bucket (path)
            content_type: MIME type
            file_size: File size in bytes
            
        Returns:
            Storage path (object_name)
            
        Raises:
            S3Error: If upload fails
        """
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type
            )
            return object_name
        except S3Error as e:
            print(f"✗ Error uploading file: {e}")
            raise
    
    def download_file(self, object_name: str) -> bytes:
        """
        Download file from MinIO
        
        Args:
            object_name: Object name in bucket
            
        Returns:
            File binary data
            
        Raises:
            S3Error: If download fails
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"✗ Error downloading file: {e}")
            raise
    
    def delete_file(self, object_name: str) -> None:
        """
        Delete file from MinIO
        
        Args:
            object_name: Object name in bucket
            
        Raises:
            S3Error: If delete fails
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
        except S3Error as e:
            print(f"✗ Error deleting file: {e}")
            raise
    
    def file_exists(self, object_name: str) -> bool:
        """
        Check if file exists in MinIO
        
        Args:
            object_name: Object name in bucket
            
        Returns:
            True if exists, False otherwise
        """
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False
    
    def get_presigned_url(
        self,
        object_name: str,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """
        Generate presigned URL for temporary download access
        
        Args:
            object_name: Object name in bucket
            expires: URL expiration time
            
        Returns:
            Presigned URL
            
        Raises:
            S3Error: If generation fails
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print(f"✗ Error generating presigned URL: {e}")
            raise
    
    @staticmethod
    def calculate_file_hash(file_data: BinaryIO) -> str:
        """
        Calculate SHA256 hash of file
        
        Args:
            file_data: File binary data
            
        Returns:
            SHA256 hash (hex string)
        """
        sha256_hash = hashlib.sha256()
        
        # Reset file pointer to beginning
        file_data.seek(0)
        
        # Read file in chunks to handle large files
        for byte_block in iter(lambda: file_data.read(4096), b""):
            sha256_hash.update(byte_block)
        
        # Reset file pointer again for subsequent reads
        file_data.seek(0)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    def generate_storage_path(user_id: int, filename: str) -> str:
        """
        Generate storage path for file with user isolation
        
        Args:
            user_id: User ID
            filename: Original filename
            
        Returns:
            Storage path (e.g., "users/123/documents/filename.pdf")
        """
        # Sanitize filename (remove path separators)
        safe_filename = filename.replace("/", "_").replace("\\", "_")
        
        return f"users/{user_id}/documents/{safe_filename}"
    
    def get_file_info(self, object_name: str) -> Optional[dict]:
        """
        Get file metadata from MinIO
        
        Args:
            object_name: Object name in bucket
            
        Returns:
            File info dict or None if not found
        """
        try:
            stat = self.client.stat_object(self.bucket_name, object_name)
            return {
                "size": stat.size,
                "etag": stat.etag,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "metadata": stat.metadata
            }
        except S3Error:
            return None


# Singleton instance
_minio_service: Optional[MinIOService] = None


def get_minio_service() -> MinIOService:
    """
    Get MinIO service singleton instance
    
    Returns:
        MinIO service instance
    """
    global _minio_service
    if _minio_service is None:
        _minio_service = MinIOService()
    return _minio_service
