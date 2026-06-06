#!/bin/bash
# Script para inicializar bucket MinIO

set -e

echo "Waiting for MinIO to be ready..."
sleep 10

echo "Creating MinIO bucket: canmos-documents"
mc alias set local http://minio:9000 ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}
mc mb local/canmos-documents --ignore-existing
mc anonymous set none local/canmos-documents

echo "MinIO bucket created successfully!"
