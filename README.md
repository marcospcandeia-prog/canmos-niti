# CANMOS-NITI

**Núcleo de Infraestrutura Tributária Inteligente**

Sistema inteligente de processamento documental e cálculo tributário focado em Pessoa Física (PF), utilizando ferramentas gratuitas, open source e self-hosted.

---

## Stack Tecnológica

### Frontend
- **Next.js 14** (App Router)
- **React 18**
- **TypeScript**
- **TailwindCSS**
- **shadcn/ui**

### Backend
- **FastAPI** (Python 3.12)
- **SQLAlchemy 2.0** (Async)
- **Alembic** (Migrations)
- **Pydantic**

### Database
- **Supabase PostgreSQL** (Free Tier)

### Storage
- **MinIO** (S3-compatible, self-hosted)

### OCR
- **PaddleOCR** (Principal)
- **Tesseract** (Fallback)

### IA Local
- **Ollama** (Phi3/Qwen2/Mistral)
- **LangChain**

### Vector Database
- **Qdrant** (Self-hosted)

### Infraestrutura
- **Docker**
- **Docker Compose**

---

## Arquitetura

```
Modular Monolith
├── Frontend (Next.js)    :3000
├── Backend (FastAPI)     :8000
├── MinIO                 :9000
├── Qdrant                :6333
└── Ollama                :11434
```

**Nota:** PostgreSQL está no Supabase (cloud gratuito), não em container local.

---

## Pipeline Principal

```
Upload → MinIO → OCR → Parsing → TAX_EVENTS → Tax Engine → Dashboard
```

---

## Estrutura do Projeto

```
/canmos-niti
  /backend
    /app
      /core              # Config, database, security, middleware
      /shared            # Models, schemas, services
      /modules
        /auth            # Registro, login, JWT
        /users           # Perfil usuário
        /documents       # Upload, listagem
        /ocr             # PaddleOCR + Tesseract
        /tax_engine      # Cálculo IRPF, validações
        /ai              # Copiloto tributário
        /dashboard       # Métricas e resumos
        /audit           # Logs LGPD
        /storage         # Interface MinIO
    /alembic             # Database migrations
    /tests               # Testes pytest

  /frontend
    /src
      /app               # Next.js App Router pages
      /components        # UI components
      /services          # API client
      /hooks             # Auth hooks
      /types             # TypeScript types

  /infra
    /docker              # Dockerfiles
    /nginx               # Reverse proxy
    /scripts             # Init scripts

  /storage               # Volumes Docker (gitignored)
  /docs                  # Documentação
```

---

## Requisitos

- **Docker** >= 24.0
- **Docker Compose** >= 2.20
- **Node.js** >= 20 (para desenvolvimento frontend local)
- **Python** >= 3.12 (para desenvolvimento backend local)
- **Conta Supabase** (Free Tier)

---

## Setup Inicial

### 1. Clonar Repositório

```bash
git clone https://github.com/seu-usuario/canmos-niti.git
cd canmos-niti
```

### 2. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

Editar `.env` e preencher:

- `DATABASE_URL` - Connection string Supabase PostgreSQL
- `SUPABASE_URL` - URL do projeto Supabase
- `SUPABASE_ANON_KEY` - Anon key do Supabase
- `SUPABASE_SERVICE_ROLE` - Service role key do Supabase
- `JWT_SECRET` - Gerar com: `openssl rand -hex 32`

### 3. Criar Projeto Supabase

1. Acessar [supabase.com](https://supabase.com)
2. Criar novo projeto (Free Tier)
3. Copiar credenciais:
   - Database URL (Settings → Database → Connection String → URI)
   - Project URL (Settings → API → Project URL)
   - anon/public key (Settings → API → anon key)
   - service_role key (Settings → API → service_role key)

### 4. Subir Ambiente Docker

```bash
docker compose up -d
```

Aguardar todos containers iniciarem:

- `canmos-backend` → http://localhost:8000
- `canmos-frontend` → http://localhost:3000
- `canmos-minio` → http://localhost:9000
- `canmos-qdrant` → http://localhost:6333
- `canmos-ollama` → http://localhost:11434

### 5. Download Modelo IA (Ollama)

```bash
docker exec canmos-ollama ollama pull phi3:mini
```

### 6. Rodar Migrations

```bash
cd backend
alembic upgrade head
```

### 7. Acessar Aplicação

- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **MinIO Console:** http://localhost:9001

---

## Desenvolvimento

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Testes

### Backend (pytest)

```bash
cd backend
pytest --cov=app --cov-report=html
```

### Frontend (Jest)

```bash
cd frontend
npm test -- --coverage
```

---

## Princípios

- **Modular Monolith** (sem microserviços no MVP)
- **LGPD-first** (auditoria, consentimento, rastreabilidade)
- **Tax Engine determinístico** (sem IA nos cálculos)
- **IA explicativa** (copiloto, não executor)
- **Gratuito e Open Source**

---

## Roadmap

### MVP (Fase 1)
- [x] Setup inicial
- [x] Autenticação JWT
- [x] Upload documentos
- [x] OCR local
- [x] Tax Engine básico
- [x] Dashboard
- [x] IA copiloto

### Futuro
- [x] Testes automatizados (backend 124 pytest, frontend 94 jest)
- [x] RAG com legislação RFB
- [x] CI/CD (GitHub Actions → Render/Vercel)
- [ ] Pessoa Jurídica (PJ)
- [ ] Notificações

---

## Licença

MIT

---

## Contato

Para dúvidas ou contribuições, abra uma issue no GitHub.
