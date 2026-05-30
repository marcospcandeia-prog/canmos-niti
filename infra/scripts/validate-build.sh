#!/bin/bash
# Valida o build completo via Docker (sem dependência de path local)
# Execute no servidor Linux ou no WSL

set -e
echo "🔍 Validando build CANMOS-NITI..."

cd "$(dirname "$0")/../.."

# Backend — importar módulos Python
echo "🐍 Validando backend..."
docker run --rm -v "$(pwd)/backend:/app" python:3.12-slim bash -c "
  pip install -q fastapi sqlalchemy alembic python-jose passlib pydantic pydantic-settings &&
  cd /app &&
  python -c 'from app.main import app; print(\"✅ Backend: OK\")'
"

# Frontend — build Next.js
echo "⚛️  Validando frontend..."
docker run --rm -v "$(pwd)/frontend:/app" -w /app node:22-alpine sh -c "
  npm ci --silent &&
  npm run build &&
  echo '✅ Frontend: OK'
"

echo ""
echo "✅ Validação completa! Pronto para produção."
