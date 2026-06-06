#!/bin/bash
# Script para verificar dependências antes de subir Docker

set -e

echo "Checking dependencies..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not found. Please install Docker."
    exit 1
fi
echo "✓ Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo "ERROR: Docker Compose not found. Please install Docker Compose."
    exit 1
fi
echo "✓ Docker Compose found: $(docker compose version)"

# Check .env file
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Please copy .env.example to .env and configure."
    exit 1
fi
echo "✓ .env file found"

# Check required ENV vars
source .env
REQUIRED_VARS=(
    "DATABASE_URL"
    "SUPABASE_URL"
    "SUPABASE_ANON_KEY"
    "JWT_SECRET"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "ERROR: $var not set in .env"
        exit 1
    fi
done
echo "✓ Required ENV vars configured"

echo ""
echo "All dependencies OK! Ready to run:"
echo "  docker compose up -d"
