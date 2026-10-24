"""
TenderLens - Object Storage Service (S3 / MinIO Document Vault)
===============================================================
Manages secure storage of raw tender PDFs, extracted Corrigenda, and
compliance matrices in AWS S3 or self-hosted MinIO with local vault fallback.
"""

import os
import io
import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("tenderlens.storage")


class ObjectStorageService:
    def __init__(self):
        self.endpoint_url = os.getenv("MINIO_ENDPOINT") or os.getenv("S3_ENDPOINT_URL")
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("MINIO_ROOT_USER")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv("MINIO_ROOT_PASSWORD")
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "tenderlens-vault")
        self.region_name = os.getenv("AWS_REGION", "ap-south-1")
        self.local_vault_dir = os.path.join(os.getcwd(), ".storage_vault")

        self._s3_client = None
        self._is_connected = False
        self._init_client()

    def _init_client(self):
        if self.access_key and self.secret_key:
            try:
                self._s3_client = boto3.client(
                    "s3",
                    endpoint_url=self.endpoint_url,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region_name
                )
                self._is_connected = True
                logger.info("Object Storage client initialized for bucket: %s", self.bucket_name)
            except Exception as e:
                logger.warning("Failed to initialize S3/MinIO client: %s; using local vault fallback.", e)
                self._is_connected = False
        else:
            logger.info("S3/MinIO credentials not provided; using local disk vault at %s", self.local_vault_dir)
            os.makedirs(self.local_vault_dir, exist_ok=True)

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def upload_document(self, data: bytes, key: str, content_type: str = "application/pdf") -> str:
        """
        Uploads document bytes to S3/MinIO or local vault and returns the storage reference.
        """
        if self._is_connected and self._s3_client:
            try:
                self._s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=data,
                    ContentType=content_type
                )
                return f"s3://{self.bucket_name}/{key}"
            except ClientError as e:
                logger.error("S3 upload failed for %s: %s", key, e)

        # Local vault fallback
        os.makedirs(self.local_vault_dir, exist_ok=True)
        safe_filename = key.replace("/", "_")
        local_path = os.path.join(self.local_vault_dir, safe_filename)
        with open(local_path, "wb") as f:
            f.write(data)
        return f"file://{local_path}"

    def download_document(self, key: str) -> Optional[bytes]:
        """
        Retrieves document bytes by key from S3/MinIO or local vault.
        """
        if self._is_connected and self._s3_client:
            try:
                resp = self._s3_client.get_object(Bucket=self.bucket_name, Key=key)
                return resp["Body"].read()
            except ClientError as e:
                logger.error("S3 download failed for %s: %s", key, e)

        # Local vault fallback
        safe_filename = key.replace("/", "_")
        local_path = os.path.join(self.local_vault_dir, safe_filename)
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()
        return None

    def generate_presigned_url(self, key: str, expiry_seconds: int = 3600) -> Optional[str]:
        """
        Generates a secure temporary pre-signed URL for browser viewing.
        """
        if self._is_connected and self._s3_client:
            try:
                return self._s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": key},
                    ExpiresIn=expiry_seconds
                )
            except ClientError as e:
                logger.error("Presigned URL generation error: %s", e)
        return None


# Global singleton
storage_service = ObjectStorageService()
