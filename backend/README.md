# CANMOS-NITI Backend

Backend FastAPI do sistema CANMOS-NITI (Núcleo de Infraestrutura Tributária Inteligente).

---

## Stack

- **Python 3.12**
- **FastAPI 0.115.0** - Framework web moderno
- **SQLAlchemy 2.0** - ORM async
- **Alembic** - Database migrations
- **PostgreSQL** (Supabase) - Banco de dados
- **Pydantic** - Validação e serialização
- **JWT** - Autenticação
- **bcrypt** - Hash de senhas

---

## Estrutura

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── core/                # Infrastructure
│   │   ├── config/          # Settings
│   │   ├── database/        # DB session
│   │   ├── security/        # JWT, bcrypt
│   │   ├── middleware/      # CORS, audit
│   │   └── utils/           # Helpers
│   ├── shared/              # Compartilhado
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   └── modules/             # Features
│       ├── auth/            # Autenticação
│       ├── users/           # Usuários
│       ├── documents/       # Upload docs
│       ├── ocr/             # OCR
│       ├── tax_engine/      # Cálculo IRPF
│       ├── ai/              # Copiloto IA
│       ├── dashboard/       # Dashboard
│       ├── audit/           # Auditoria LGPD
│       └── storage/         # MinIO
├── alembic/                 # Migrations
├── tests/                   # Testes pytest
├── scripts/                 # Utility scripts
└── docs/                    # Documentação
```

---

## Models (SQLAlchemy)

9 entidades principais:

1. **User** - Usuários do sistema
2. **UserProfile** - Perfil estendido
3. **Document** - Documentos enviados
4. **OCRResult** - Resultados OCR
5. **TaxEvent** - Eventos tributários
6. **Declaration** - Declarações IRPF
7. **Validation** - Validações
8. **AIInteraction** - Interações IA
9. **AuditLog** - Logs auditoria (LGPD)

Ver: [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)

---

## Setup

### 1. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar .env

Copiar `.env.example` da raiz do projeto e preencher:

```env
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
JWT_SECRET=...
```

### 4. Rodar migrations

```bash
alembic upgrade head
```

### 5. Iniciar servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acessar:
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health:** http://localhost:8000/health

---

## Migrations (Alembic)

Ver guia completo: [docs/MIGRATIONS.md](docs/MIGRATIONS.md)

### Comandos úteis

```bash
# Status atual
alembic current

# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Criar nova migration (autogenerate)
alembic revision --autogenerate -m "Description"

# Histórico
alembic history

# Verificar schema
python scripts/verify_schema.py
```

---

## Desenvolvimento

### Rodar servidor local

```bash
uvicorn app.main:app --reload
```

### Formato código (Black)

```bash
black app/
```

### Lint (Ruff)

```bash
ruff check app/
```

### Testes

```bash
pytest --cov=app --cov-report=html
```

---

## Produção

### Gunicorn + Uvicorn Workers

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Docker

```bash
docker build -f ../infra/docker/Dockerfile.backend.prod -t canmos-backend .
docker run -p 8000:8000 --env-file .env canmos-backend
```

---

## Documentação Adicional

- [Database Schema](docs/DATABASE_SCHEMA.md) - Modelo de dados completo
- [Migrations Guide](docs/MIGRATIONS.md) - Como trabalhar com Alembic
- [Architecture](../docs/ARCHITECTURE.md) - Decisões arquiteturais

---

## API Routes

### Auth ✅ (Implementado)
- `POST /auth/register` - Registrar novo usuário
- `POST /auth/login` - Fazer login (retorna access + refresh tokens)
- `POST /auth/refresh` - Renovar access token
- `POST /auth/logout` - Fazer logout

Ver documentação completa: [docs/AUTH_API.md](docs/AUTH_API.md)

### Users
- `GET /users/me`
- `PUT /users/me`

### Documents
- `POST /documents/upload`
- `GET /documents`
- `GET /documents/{id}`

### Tax Engine
- `POST /tax-engine/process/{document_id}`
- `GET /tax-engine/events`
- `GET /tax-engine/declaration/{ano}`

### Dashboard
- `GET /dashboard/summary`

### AI
- `POST /ai/ask`

---

## Segurança

### Autenticação

- **JWT** com expiration (15 min access, 7 dias refresh)
- **bcrypt** para hash de senhas (rounds >= 12)
- Middleware `get_current_user` para rotas protegidas

### LGPD

- Consentimento obrigatório no registro
- Auditoria completa em `audit_logs`
- Metadata JSON com detalhes de ações

---

## Troubleshooting

### Erro: "No module named 'app'"

```bash
# Certifique-se de estar no diretório backend/
cd backend

# Ou adicione ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Erro: "asyncpg.exceptions.InvalidPasswordError"

- Verifique se `DATABASE_URL` no `.env` está correto
- Verifique se substituiu `[YOUR-PASSWORD]` pela senha real

### Erro: "relation does not exist"

```bash
# Executar migrations
alembic upgrade head
```

---

## Licença

MIT
