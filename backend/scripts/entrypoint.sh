#!/bin/bash
set -e

echo "=== CANMOS-NITI Backend Entrypoint ==="

if [ "$ENVIRONMENT" = "production" ]; then
    echo "Modo produção: rodando migrations..."
    alembic upgrade head
    echo "Migrations concluídas."
else
    echo "Modo desenvolvimento: migrations sob demanda."
fi

exec "$@"
