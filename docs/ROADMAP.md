# ROADMAP CANMOS-NITI
## Núcleo de Infraestrutura Tributária Inteligente

---

## VISÃO GERAL

**Duração Total:** 27-42 dias  
**Objetivo:** Sistema tributário inteligente em produção (MVP)

---

## FASE 1: CONSTRUÇÃO (20-30 dias)

### 1.1 Setup Inicial ✅ (CONCLUÍDO)
- [x] Estrutura de pastas
- [x] Docker Compose
- [x] Dockerfiles
- [x] Variáveis ENV
- [x] Backend base (FastAPI + Settings)
- [x] Database session (SQLAlchemy async)
- [x] README principal

**Status:** Completo

---

### 1.2 Backend Core (3-5 dias)

#### Alembic Migrations
- [ ] Configurar Alembic
- [ ] Criar migration inicial com todas as tabelas:
  - `users`
  - `user_profiles`
  - `documents`
  - `ocr_results`
  - `tax_events`
  - `declarations`
  - `validations`
  - `ai_interactions`
  - `audit_logs`

#### Verificação
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
psql $DATABASE_URL -c "\dt"
```

---

### 1.3 Módulo Auth (2-3 dias)

#### Implementar
- [ ] `/app/core/security/jwt.py` - Geração e validação JWT
- [ ] `/app/core/security/password.py` - Bcrypt hash
- [ ] `/app/modules/auth/schemas.py` - Pydantic schemas
- [ ] `/app/modules/auth/service.py` - Lógica autenticação
- [ ] `/app/modules/auth/router.py` - Rotas FastAPI
- [ ] `/app/shared/models/user.py` - SQLAlchemy User model

#### Rotas
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

#### Verificação
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","cpf":"12345678900","senha":"senha123"}'
```

---

### 1.4 Módulo Users (1-2 dias)

#### Implementar
- [ ] `/app/modules/users/service.py`
- [ ] `/app/modules/users/router.py`
- [ ] Middleware autenticação `get_current_user`

#### Rotas
- `GET /users/me`
- `PUT /users/me`

---

### 1.5 Módulo Storage + Documents (2-3 dias)

#### MinIO Setup
- [ ] Script init bucket: `/infra/scripts/init-minio.sh`
- [ ] Service MinIO: `/app/modules/storage/minio_service.py`

#### Documents
- [ ] Model `Document`
- [ ] Router `POST /documents/upload`
- [ ] Router `GET /documents`
- [ ] Router `GET /documents/{id}`
- [ ] Hash SHA256 para deduplicação

#### Verificação
```bash
curl -F "file=@test.pdf" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/documents/upload
```

---

### 1.6 Módulo OCR (3-4 dias)

#### Implementar
- [ ] `/app/modules/ocr/engines/paddleocr_engine.py`
- [ ] `/app/modules/ocr/engines/tesseract_engine.py`
- [ ] `/app/modules/ocr/service.py` - Orquestrador
- [ ] `/app/modules/ocr/worker.py` - Background task
- [ ] Model `OCRResult`

#### Fluxo
1. Upload → MinIO
2. Dispara task OCR
3. PaddleOCR extrai texto
4. Se falhar → Tesseract
5. Salva `ocr_results`

#### Verificação
```bash
# Verificar OCR result
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/documents/123
```

---

### 1.7 Módulo Tax Engine (4-5 dias)

#### Implementar
- [ ] `/app/modules/tax_engine/parsers/informe_rendimentos_parser.py`
- [ ] `/app/modules/tax_engine/parsers/recibo_medico_parser.py`
- [ ] `/app/modules/tax_engine/calculators/irpf_calculator.py`
- [ ] `/app/modules/tax_engine/validators/`
- [ ] Model `TaxEvent`
- [ ] Model `Declaration`
- [ ] Model `Validation`

#### Tabela IRPF 2025
```python
# Exemplo tabela progressiva
IRPF_TABLE_2025 = [
    {"limite": 2259.20, "aliquota": 0.00, "deducao": 0.00},
    {"limite": 2826.65, "aliquota": 0.075, "deducao": 169.44},
    {"limite": 3751.05, "aliquota": 0.15, "deducao": 381.44},
    {"limite": 4664.68, "aliquota": 0.225, "deducao": 662.77},
    {"limite": float('inf'), "aliquota": 0.275, "deducao": 896.00},
]
```

#### Rotas
- `POST /tax-engine/process/{document_id}`
- `GET /tax-engine/events`
- `GET /tax-engine/declaration/{ano}`

---

### 1.8 Módulo IA (3-4 dias)

#### Implementar
- [ ] `/app/modules/ai/ollama_client.py`
- [ ] `/app/modules/ai/prompts.py` - System prompts
- [ ] `/app/modules/ai/service.py` - LangChain integration
- [ ] `/app/modules/ai/router.py`
- [ ] Model `AIInteraction`

#### Prompt System
```python
SYSTEM_PROMPT = """
Você é um assistente tributário brasileiro especializado em IRPF.
Responda dúvidas com base no contexto fornecido.
IMPORTANTE: Você NÃO deve alterar cálculos ou decisões fiscais.
Apenas explique e contextualize.
"""
```

#### Rotas
- `POST /ai/ask`

---

### 1.9 Módulo Dashboard (2-3 dias)

#### Implementar
- [ ] `/app/modules/dashboard/service.py`
- [ ] `/app/modules/dashboard/router.py`
- [ ] Agregações SQL para métricas

#### Rota
- `GET /dashboard/summary` → JSON com:
  - `restituicao_estimada`
  - `imposto_devido`
  - `total_rendimentos`
  - `total_deducoes`
  - `documentos_enviados`
  - `documentos_processados`
  - `alertas[]`

---

### 1.10 Frontend (5-7 dias)

#### Setup
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app
npx shadcn-ui@latest init
```

#### Páginas
- [ ] `/app/auth/login/page.tsx`
- [ ] `/app/auth/register/page.tsx`
- [ ] `/app/dashboard/page.tsx`
- [ ] `/app/documents/page.tsx`
- [ ] `/app/documents/[id]/page.tsx`
- [ ] `/app/tax/declaration/page.tsx`
- [ ] `/app/ai/chat/page.tsx`

#### Componentes shadcn/ui
- [ ] `Sidebar`
- [ ] `Card`
- [ ] `Table`
- [ ] `Button`
- [ ] `Form`
- [ ] `Upload`
- [ ] `Alert`

#### Auth
- [ ] Hook `useAuth` (Zustand)
- [ ] Interceptor Axios (JWT)
- [ ] Protected routes middleware

---

### 1.11 Auditoria LGPD (1-2 dias)

#### Implementar
- [ ] `/app/core/middleware/audit.py`
- [ ] Model `AuditLog`
- [ ] Interceptar ações: CREATE, UPDATE, DELETE, LOGIN, LOGOUT, UPLOAD
- [ ] Campo `lgpd_consent_at` em User

---

## FASE 2: TESTES (3-5 dias)

### 2.1 Backend (pytest)

```bash
cd backend
pip install pytest pytest-asyncio pytest-cov httpx
```

#### Testes Unitários
- [ ] `tests/modules/auth/test_auth.py`
- [ ] `tests/modules/tax_engine/test_irpf_calculator.py`
- [ ] `tests/modules/ocr/test_parsers.py`

#### Testes Integração
- [ ] `tests/integration/test_upload_flow.py`

**Meta:** Cobertura >= 70%

---

### 2.2 Frontend (Jest)

```bash
cd frontend
npm install -D jest @testing-library/react
```

#### Testes
- [ ] `tests/auth/login.test.tsx`
- [ ] `tests/dashboard/summary.test.tsx`
- [ ] `tests/documents/upload.test.tsx`

---

## FASE 3: IMPLANTAÇÃO (2-3 dias)

### 3.1 Build Produção

#### Backend
- [ ] Configurar Gunicorn com Uvicorn workers
- [ ] Variáveis `.env.production`
- [ ] Multi-stage Dockerfile

#### Frontend
- [ ] `npm run build`
- [ ] Standalone output

### 3.2 Migrations Produção

```bash
# Backup
pg_dump $DATABASE_URL > backup.sql

# Migrate
alembic upgrade head
```

---

## FASE 4: HOSPEDAGEM (1-2 dias)

### Opção A: VPS ($5-10/mês)
- **Provedor:** Contabo, Hetzner, DigitalOcean
- **Specs:** 2GB RAM, 1 vCPU, 20GB SSD

#### Setup
```bash
# No VPS
git clone https://github.com/seu-usuario/canmos-niti.git
cd canmos-niti
cp .env.example .env
nano .env  # Configurar
docker compose -f docker-compose.prod.yml up -d
```

#### SSL
```bash
certbot --nginx -d canmos-niti.com.br
```

### Opção B: Self-Hosted Casa (Grátis)
- **Hardware:** Raspberry Pi 4 ou PC antigo
- **Tunnel:** Cloudflare Tunnel
- **Domínio:** DDNS gratuito

### Opção C: Hybrid (Vercel + VPS)
- **Frontend:** Vercel (free)
- **Backend:** VPS

---

## FASE 5: PRODUÇÃO (1-2 dias)

### 5.1 Monitoramento
- [ ] Logs centralizados
- [ ] UptimeRobot (alertas)
- [ ] Healthcheck `/health`

### 5.2 Backup
- [ ] Supabase backup diário (automático)
- [ ] MinIO backup cron:
  ```bash
  0 2 * * * mc mirror local/canmos-documents /backup/
  ```

### 5.3 CI/CD (Opcional MVP)
- [ ] GitHub Actions deploy automático

---

## CHECKLIST PRODUÇÃO

### Segurança
- [ ] HTTPS obrigatório
- [ ] JWT secret >= 256 bits
- [ ] Rate limiting
- [ ] CORS configurado
- [ ] Secrets em ENV

### Performance
- [ ] Frontend com CDN
- [ ] Imagens Docker otimizadas
- [ ] Cache Redis (futuro)

### LGPD
- [ ] Política de privacidade
- [ ] Consentimento obrigatório
- [ ] Endpoint exclusão (futuro)

### Documentação
- [ ] README completo
- [ ] API docs `/docs`
- [ ] Guia usuário

---

## CRONOGRAMA RESUMIDO

| Fase | Duração | Status |
|------|---------|--------|
| 1.1 Setup Inicial | 2-3 dias | ✅ Completo |
| 1.2-1.11 Backend/Frontend | 18-27 dias | ⏳ Pendente |
| 2. Testes | 3-5 dias | ⏳ Pendente |
| 3. Implantação | 2-3 dias | ⏳ Pendente |
| 4. Hospedagem | 1-2 dias | ⏳ Pendente |
| 5. Produção | 1-2 dias | ⏳ Pendente |
| **TOTAL** | **27-42 dias** | |

---

## CRITÉRIOS DE SUCESSO

Sistema considerado pronto quando:

✅ HTTPS acessível publicamente  
✅ Registro/login funcionando  
✅ Upload + OCR + Tax Events automático  
✅ Dashboard mostra restituição estimada  
✅ IA responde perguntas tributárias  
✅ Logs auditáveis (LGPD)  
✅ Backup diário configurado  
✅ Uptime > 99%
