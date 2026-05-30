#!/bin/bash
# Script de deploy inicial no VPS (Oracle Cloud Free Tier / qualquer Ubuntu 22.04)
# Executar UMA VEZ no servidor: bash deploy-vps.sh

set -e
echo "🏛️  CANMOS-NITI — Deploy VPS"

# ── Instalar dependências ──────────────────────────────────
apt-get update -qq
apt-get install -y git curl docker.io docker-compose-plugin ufw certbot

# ── Docker sem sudo ────────────────────────────────────────
usermod -aG docker $USER || true

# ── Firewall ───────────────────────────────────────────────
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

# ── Clonar projeto ─────────────────────────────────────────
if [ ! -d /opt/canmos-niti ]; then
  git clone https://github.com/SEU_USUARIO/canmos-niti /opt/canmos-niti
fi
cd /opt/canmos-niti

# ── Configurar .env.prod ───────────────────────────────────
if [ ! -f .env.prod ]; then
  cp .env.example .env.prod
  echo ""
  echo "⚠️  CONFIGURE /opt/canmos-niti/.env.prod antes de continuar!"
  echo "   Especialmente: JWT_SECRET_KEY, STRIPE_*, DATABASE_URL"
  exit 1
fi

# ── Subir containers ───────────────────────────────────────
docker compose -f docker-compose.prod.yml up -d --build

# ── Migrations ────────────────────────────────────────────
sleep 10
docker compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# ── Baixar modelo Ollama ──────────────────────────────────
docker compose -f docker-compose.prod.yml exec -T ollama ollama pull llama3.2

# ── SSL com Certbot (opcional) ────────────────────────────
# certbot --nginx -d seudominio.com.br --non-interactive --agree-tos -m seu@email.com

echo ""
echo "✅ CANMOS-NITI rodando em produção!"
echo "   Acesse: http://$(curl -s ifconfig.me)"
