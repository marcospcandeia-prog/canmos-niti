# CANMOS-NITI - Guia de Deploy

## Arquitetura do Deploy

```
                    ┌─────────────┐
                    │   Vercel    │
                    │  Frontend   │
                    │  (Next.js)  │
                    └──────┬──────┘
                           │ HTTPS
                    ┌──────▼──────┐
                    │   Render    │
                    │  Backend    │
                    │  (FastAPI)  │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
   │  Supabase   │  │   MinIO    │  │   Ollama   │
   │ PostgreSQL  │  │   (S3)     │  │   (IA)     │
   └─────────────┘  └─────────────┘  └────────────┘
```

## Pré-requisitos

- Conta [Vercel](https://vercel.com) (frontend)
- Conta [Render](https://render.com) (backend)
- Conta [Supabase](https://supabase.com) (PostgreSQL)
- Docker (para MinIO e Ollama locais, ou serviços cloud)

## 1. Database (Supabase)

1. Crie um projeto em [supabase.com](https://supabase.com)
2. Anote a **Connection String** do PostgreSQL
3. Execute as migrations no banco:
   ```bash
   cd backend
   # Configure DATABASE_URL no .env
   alembic upgrade head
   ```

## 2. Storage (MinIO)

**Opção A - MinIO Cloud (recomendado):**
- Use [MinIO Cloud](https://min.io/) ou [Backblaze B2](https://www.backblaze.com/cloud-storage)

**Opção B - Local (dev):**
```bash
docker run -d -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  --name canmos-minio \
  quay.io/minio/minio server /data --console-address ":9001"
```

## 3. Backend (Render)

### Via Blueprint (recomendado)

O arquivo `render.yaml` na raiz do projeto configura automaticamente:

1. Faça fork/clone do repositório no GitHub
2. No Render, conecte o repositório
3. Selecione "Blueprint" como método de deploy
4. O `render.yaml` será lido automaticamente

### Via Web Dashboard

1. Crie um **Web Service** no Render
2. Configure:
   - **Runtime:** Python 3.12
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** `backend`

3. Adicione as **Environment Variables**:
   ```
   APP_ENV=production
   DATABASE_URL=postgresql+asyncpg://...
   JWT_SECRET=<gerar hash seguro>
   CORS_ORIGINS=https://seu-frontend.vercel.app
   NEXT_PUBLIC_API_URL=https://seu-backend.onrender.com
   MINIO_ENDPOINT=<seu-minio-endpoint>
   MINIO_ACCESS_KEY=...
   MINIO_SECRET_KEY=...
   MINIO_BUCKET=canmos-documents
   ```

## 4. Frontend (Vercel)

1. Conecte o repositório no Vercel
2. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

3. Adicione as **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://seu-backend.onrender.com
   ```

4. **Importante:** Configure o `next.config.js` com o `output: 'standalone'` já definido (presente no projeto).

## 5. Serviços Adicionais

### OCR (Container Docker)

**Render (Docker):**
```yaml
services:
  ocr-service:
    type: docker
    dockerfile_path: infra/docker/Dockerfile.ocr
    env_vars:
      - key: OCR_API_URL
        value: http://backend:8000
```

**Local:**
```bash
docker compose up -d ocr
```

### IA (Ollama)

**Render (Docker) ou VM dedicada:**
```bash
docker run -d -p 11434:11434 --name ollama ollama/ollama
docker exec ollama ollama pull phi3:mini
```

## 6. Verificações Pós-Deploy

```bash
# Health check do backend
curl https://seu-backend.onrender.com/health

# Health check do OCR
curl http://seu-ocr.onrender.com/health

# Testar registro
curl -X POST https://seu-backend.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nome":"Teste","email":"teste@teste.com","cpf":"52998224725","senha":"senha12345","lgpd_consent":true}'

# Testar login
curl -X POST https://seu-backend.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@teste.com","senha":"senha12345"}'
```

## 7. Variáveis de Ambiente (Produção)

### Backend
| Variável | Descrição | Exemplo |
|---|---|---|
| `APP_ENV` | Ambiente | `production` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql+asyncpg://user:pass@host:5432/db` |
| `JWT_SECRET` | Chave secreta JWT | (hash 64+ chars) |
| `CORS_ORIGINS` | Origens permitidas | `https://app.vercel.app` |
| `MINIO_ENDPOINT` | Endpoint MinIO | `s3.amazonaws.com` |
| `MINIO_ACCESS_KEY` | Access key | - |
| `MINIO_SECRET_KEY` | Secret key | - |
| `MINIO_BUCKET` | Bucket name | `canmos-prod` |

### Frontend
| Variável | Descrição | Exemplo |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | URL do backend | `https://api.canmos.app` |

## 8. Docker Compose Produção (alternativa)

Para deploy completo via Docker com proxy reverso:

```bash
# Iniciar stack de produção
make start-prod

# Ou manualmente:
docker compose -f docker-compose.prod.yml up -d

# Acessar:
# - Frontend + API: http://localhost (via nginx porta 80)
# - API direta: http://localhost:8000/docs
# - MinIO Console: http://localhost:9001

# Para incluir OCR:
COMPOSE_PROFILES=ocr docker compose -f docker-compose.prod.yml up -d

# Parar:
make stop-prod
```

### Serviços Produção

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **nginx** | 80 | Proxy reverso (frontend + API) |
| **backend** | - | FastAPI (gunicorn, 4 workers) |
| **frontend** | - | Next.js standalone |
| **minio** | - | S3-compatible storage |
| **qdrant** | - | Vector database |
| **ollama** | 11434 | LLM (auto-pulls modelo) |
| **ocr-service** | - | OCR worker (perfil `ocr`) |

## 10. Segurança

1. **JWT_SECRET:** Gerar com `openssl rand -hex 64`
2. **CORS:** Restringir origens ao domínio do frontend
3. **Rate Limiting:** Configurar no Render ou Cloudflare
4. **SSL/TLS:** Habilitado automaticamente por Vercel/Render
5. **Migrations:** Rodar `alembic upgrade head` uma vez, não em todo deploy

## 11. Monitoramento

- **Render:** Logs embutidos no dashboard
- **Vercel:** Analytics e Logs no dashboard
- **Supabase:** Database advisor, query performance
- **Sentry** (opcional): Adicionar para error tracking:
  ```bash
  pip install sentry-sdk
  ```
