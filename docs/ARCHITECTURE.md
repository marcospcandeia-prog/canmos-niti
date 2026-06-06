# ARQUITETURA CANMOS-NITI

---

## PRINCÍPIOS ARQUITETURAIS

### Modular Monolith

O sistema é construído como **monolito modular**, não microserviços.

**Por quê?**
- Simplicidade inicial (MVP)
- Menos complexidade operacional
- Fácil desenvolvimento local
- Deploy simples
- Performance superior (sem latência rede)

**Preparado para futuro:**
- Módulos bem desacoplados
- Interfaces claras entre módulos
- Possível extração para microserviços se necessário

---

## SEPARAÇÃO DE RESPONSABILIDADES

### Core Fiscal (Tax Engine)
- **Função:** Cálculo tributário determinístico
- **Características:**
  - Auditável
  - Reproduzível
  - Baseado em regras RFB
  - SEM IA
  - Versionado (tabelas IRPF por ano)

### IA (Copiloto)
- **Função:** Explicação e contextualização
- **Características:**
  - NÃO altera cálculos
  - NÃO toma decisões fiscais
  - Apenas explica e sugere
  - Usa contexto (tax_events + declarations)

**REGRA DE OURO:** IA NUNCA escreve em `tax_events` ou `declarations`.

---

## CAMADAS

```
┌─────────────────────────────────────────┐
│           FRONTEND (Next.js)            │
│  - Páginas App Router                   │
│  - Componentes UI (shadcn/ui)           │
│  - State Management (Zustand)           │
│  - API Client (Axios)                   │
└─────────────────┬───────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────┐
│           BACKEND (FastAPI)             │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │         ROUTERS (API)             │ │
│  │  /auth, /users, /documents, etc   │ │
│  └───────────┬───────────────────────┘ │
│              │                          │
│  ┌───────────▼───────────────────────┐ │
│  │      MODULES (Business Logic)     │ │
│  │  - auth                           │ │
│  │  - users                          │ │
│  │  - documents                      │ │
│  │  - ocr                            │ │
│  │  - tax_engine  ◄───┐              │ │
│  │  - ai             │              │ │
│  │  - dashboard       │              │ │
│  │  - audit           │              │ │
│  │  - storage         │              │ │
│  └───────────┬────────┴──────────────┘ │
│              │                          │
│  ┌───────────▼───────────────────────┐ │
│  │    SHARED (Models, Schemas)       │ │
│  │  - SQLAlchemy Models              │ │
│  │  - Pydantic Schemas               │ │
│  │  - Shared Services                │ │
│  └───────────┬───────────────────────┘ │
│              │                          │
│  ┌───────────▼───────────────────────┐ │
│  │      CORE (Infrastructure)        │ │
│  │  - Config (Settings)              │ │
│  │  - Database (Session)             │ │
│  │  - Security (JWT, Hash)           │ │
│  │  - Middleware (CORS, Audit)       │ │
│  └───────────┬───────────────────────┘ │
└──────────────┼───────────────────────┘
               │
      ┌────────┼────────┐
      │        │        │
┌─────▼──┐ ┌──▼───┐ ┌──▼─────┐
│MinIO   │ │Ollama│ │Qdrant  │
│Storage │ │IA    │ │Vector  │
└────────┘ └──────┘ └────────┘
      │
┌─────▼──────────────────┐
│  Supabase PostgreSQL   │
│  (Cloud Free Tier)     │
└────────────────────────┘
```

---

## FLUXO DOCUMENTAL

```
1. USER
   │
   ▼
2. FRONTEND: Upload documento (drag-and-drop)
   │
   ▼
3. BACKEND: POST /documents/upload
   │
   ├─► Validar mime_type (PDF, imagem)
   ├─► Calcular hash SHA256 (deduplicação)
   ├─► Salvar MinIO (storage privado)
   ├─► Criar registro `documents` no Supabase
   │
   ▼
4. Disparar Task OCR (async)
   │
   ▼
5. OCR SERVICE (Container separado)
   │
   ├─► Baixar arquivo de MinIO
   ├─► Tentar PaddleOCR
   │   └─► Se falhar → Tentar Tesseract
   ├─► Salvar texto em `ocr_results`
   │
   ▼
6. TAX ENGINE: Parsing automático
   │
   ├─► Identificar tipo documento (regex/heurística)
   ├─► Extrair: categoria, valor, competência
   ├─► Criar `tax_events`
   │
   ▼
7. TAX ENGINE: Cálculo
   │
   ├─► Agregar tax_events por ano
   ├─► Calcular imposto devido (tabela progressiva)
   ├─► Calcular restituição estimada
   ├─► Executar validações
   ├─► Salvar `declarations` e `validations`
   │
   ▼
8. DASHBOARD: Atualizar métricas
   │
   ▼
9. USER: Ver dashboard com restituição
```

---

## BANCO DE DADOS (Supabase PostgreSQL)

### Entidades Principais

```sql
-- Autenticação
users
  ├── id (PK)
  ├── uuid (unique)
  ├── nome
  ├── cpf (unique)
  ├── email (unique)
  ├── telefone
  ├── senha_hash
  ├── status (active, inactive)
  ├── lgpd_consent_at
  ├── created_at
  └── updated_at

user_profiles
  ├── id (PK)
  ├── user_id (FK → users)
  ├── profissao
  ├── estado_civil
  ├── possui_dependentes
  └── possui_investimentos

-- Documentos
documents
  ├── id (PK)
  ├── user_id (FK → users)
  ├── tipo (informe_rendimentos, recibo_medico, etc)
  ├── nome_original
  ├── storage_path (MinIO)
  ├── mime_type
  ├── hash_arquivo (SHA256)
  ├── status (uploaded, processing, processed, error)
  ├── created_at
  └── updated_at

ocr_results
  ├── id (PK)
  ├── document_id (FK → documents)
  ├── texto_extraido (TEXT)
  ├── confianca (0.0 - 1.0)
  ├── engine_utilizada (paddleocr, tesseract)
  ├── status (pending, success, failed)
  └── created_at

-- Tributário
tax_events
  ├── id (PK)
  ├── user_id (FK → users)
  ├── document_id (FK → documents, nullable)
  ├── categoria (rendimento_trabalho, despesa_medica, etc)
  ├── subcategoria
  ├── valor (NUMERIC) ← FLOAT, não String
  ├── competencia (YYYY-MM)
  ├── origem (ocr, manual)
  ├── metadata_json (JSONB)
  └── created_at

declarations
  ├── id (PK)
  ├── user_id (FK → users)
  ├── ano_base (2025, 2026, etc)
  ├── status (rascunho, finalizada)
  ├── restituicao_estimada (NUMERIC)
  ├── imposto_devido (NUMERIC)
  ├── created_at
  └── updated_at

validations
  ├── id (PK)
  ├── declaration_id (FK → declarations)
  ├── tipo (missing_document, valor_inconsistente, etc)
  ├── severidade (info, warning, error)
  ├── mensagem
  └── created_at

-- IA
ai_interactions
  ├── id (PK)
  ├── user_id (FK → users)
  ├── pergunta (TEXT)
  ├── resposta (TEXT)
  ├── modelo_ia (phi3:mini, qwen2, etc)
  └── created_at

-- Auditoria (LGPD)
audit_logs
  ├── id (PK)
  ├── user_id (FK → users, nullable)
  ├── action (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, UPLOAD)
  ├── entity (users, documents, tax_events, etc)
  ├── entity_id
  ├── metadata_json (JSONB - detalhes da ação)
  └── created_at
```

### Índices Importantes

```sql
-- Performance
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_tax_events_user_id ON tax_events(user_id);
CREATE INDEX idx_tax_events_competencia ON tax_events(competencia);
CREATE INDEX idx_declarations_user_ano ON declarations(user_id, ano_base);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Segurança (unique constraints)
CREATE UNIQUE INDEX idx_users_cpf ON users(cpf);
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_documents_hash ON documents(hash_arquivo, user_id);
```

---

## SEGURANÇA

### Autenticação (JWT)

```
1. Login:
   POST /auth/login → {access_token, refresh_token}

2. Access Token:
   - Expiration: 15 minutos
   - Payload: {user_id, email, exp}
   - Algorithm: HS256

3. Refresh Token:
   - Expiration: 7 dias
   - Armazenado: HttpOnly cookie (futuro) ou localStorage
   - Usado: POST /auth/refresh → novo access_token

4. Logout:
   POST /auth/logout → Invalida refresh_token
```

### Hash Senha

```python
# bcrypt com rounds >= 12
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("senha123")
is_valid = pwd_context.verify("senha123", hashed)
```

### Storage Privado (MinIO)

- Bucket: `canmos-documents` (privado)
- Acesso: Apenas backend via access/secret keys
- Isolamento: Prefixo por user_id (`{user_id}/documents/`)
- Download: Signed URLs com expiration

### LGPD

- **Consentimento:** Checkbox obrigatório no registro
- **Auditoria:** Todas ações logadas em `audit_logs`
- **Rastreabilidade:** Metadata JSON com detalhes
- **Exclusão:** Endpoint futuro `DELETE /users/me` (soft delete + anonimização)

---

## ESCALABILIDADE FUTURA

### Horizontal (adicionar instâncias)

```
┌────────────────┐
│  Load Balancer │
└───────┬────────┘
        │
   ┌────┴────┬────────┬────────┐
   │         │        │        │
┌──▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐
│BE #1 │ │BE #2 │ │BE #3 │ │BE #4 │
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
   │        │        │        │
   └────────┴────────┴────────┘
            │
      ┌─────▼──────┐
      │ Supabase   │
      │ PostgreSQL │
      └────────────┘
```

**Requisitos:**
- Session state em Redis (não em memória)
- MinIO em cluster
- Queue para OCR (RabbitMQ/Redis)

### Vertical (aumentar recursos)

- Mais RAM para Ollama (modelos maiores)
- Mais vCPUs para OCR (processamento paralelo)
- PostgreSQL connection pooling (PgBouncer)

---

## OBSERVABILIDADE (Futuro)

### Logs

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Document uploaded", extra={"document_id": doc.id, "user_id": user.id})
```

### Métricas

- Request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- OCR processing time
- Tax calculation time

### Tracing (OpenTelemetry)

```
Request → Auth → Upload → MinIO → OCR → TaxEngine → Response
   100ms   10ms    50ms     200ms  5000ms   300ms      = 5660ms total
```

---

## DECISÕES ARQUITETURAIS (ADRs)

### ADR-001: Por que Modular Monolith?
- **Contexto:** MVP inicial, time pequeno
- **Decisão:** Monolito modular
- **Consequências:** Simples deploy, fácil debug, preparado para extração futura

### ADR-002: Por que Supabase (não PostgreSQL local)?
- **Contexto:** Objetivo low cost, evitar gerenciar infra
- **Decisão:** Supabase Free Tier (500MB, 2GB transfer)
- **Consequências:** Grátis, backups automáticos, limitações de espaço

### ADR-003: Por que MinIO (não Supabase Storage)?
- **Contexto:** Documentos PF sensíveis, LGPD
- **Decisão:** MinIO self-hosted (controle total)
- **Consequências:** Mais trabalho operacional, total privacidade

### ADR-004: Por que Ollama (não OpenAI)?
- **Contexto:** Evitar APIs pagas, LGPD (dados não saem do servidor)
- **Decisão:** Ollama local com Phi3/Qwen2
- **Consequências:** Grátis, privado, requer GPU/RAM, modelos menores

---

## PRÓXIMOS PASSOS ARQUITETURAIS (Pós-MVP)

1. **Cache Redis** - Dashboard queries
2. **Queue (RabbitMQ)** - OCR async
3. **Rate Limiting** - Anti-abuse
4. **API Gateway** - Nginx com rate limit
5. **Monitoring** - Prometheus + Grafana
6. **Tracing** - OpenTelemetry + Jaeger
7. **Feature Flags** - LaunchDarkly ou Unleash
8. **Multi-tenant** - Segregação por empresa (PJ)
