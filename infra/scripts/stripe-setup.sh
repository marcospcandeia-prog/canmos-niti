#!/bin/bash
# Script para configurar produtos e preços no Stripe
# Requer: stripe CLI instalado e autenticado

echo "💳 Configurando produtos Stripe para CANMOS-NITI..."

# Criar produto
PRODUCT_ID=$(stripe products create \
  --name="CANMOS-NITI Premium" \
  --description="Plataforma de IRPF com IA — Declaração automática" \
  --format=json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Produto criado: $PRODUCT_ID"

# Criar preço mensal
PRICE_MONTHLY=$(stripe prices create \
  --product="$PRODUCT_ID" \
  --unit-amount=2990 \
  --currency=brl \
  --recurring.interval=month \
  --nickname="Premium Mensal" \
  --format=json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Preço mensal: $PRICE_MONTHLY"

# Criar preço anual
PRICE_ANNUAL=$(stripe prices create \
  --product="$PRODUCT_ID" \
  --unit-amount=19900 \
  --currency=brl \
  --recurring.interval=year \
  --nickname="Premium Anual" \
  --format=json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Preço anual: $PRICE_ANNUAL"

echo ""
echo "✅ Adicione ao .env:"
echo "STRIPE_PRICE_PREMIUM_MONTHLY=$PRICE_MONTHLY"
echo "STRIPE_PRICE_PREMIUM_ANNUAL=$PRICE_ANNUAL"

# Configurar webhook
echo ""
echo "📡 Configure o webhook no Stripe Dashboard:"
echo "   URL: https://seudominio.com.br/api/v1/payments/webhook"
echo "   Eventos: checkout.session.completed, customer.subscription.*"
