#!/bin/bash
# CANMOS-NITI — Script de inicialização automática

set -e

echo "🏛️  CANMOS-NITI — Setup Automático"
echo "===================================="

# Verificar dependências
command -v docker >/dev/null 2>&1 || { echo "❌ Docker não encontrado. Instale em https://docker.com"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1 || { echo "❌ Docker Compose não encontrado"; exit 1; }

# Copiar .env se não existir
if [ ! -f ".env" ]; then
  echo "📋 Criando .env a partir do .env.example..."
  cp .env.example .env
  echo "⚠️  Configure suas chaves em .env antes de continuar"
fi

echo "🐳 Subindo containers..."
docker compose up -d --build

echo "⏳ Aguardando serviços..."
sleep 10

echo "🗄️  Rodando migrations..."
docker compose exec backend alembic upgrade head

echo ""
echo "✅ CANMOS-NITI está no ar!"
echo ""
echo "  🌐 Frontend:  http://localhost:3000"
echo "  🔧 Backend:   http://localhost:8000"
echo "  📚 API Docs:  http://localhost:8000/docs"
echo "  🗄️  MinIO:     http://localhost:9001"
echo "  🔍 Qdrant:    http://localhost:6333"
echo ""
echo "📦 Baixando modelo Ollama (llama3.2)..."
docker compose exec ollama ollama pull llama3.2

echo "🎉 Tudo pronto!"
