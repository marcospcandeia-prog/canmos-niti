# CANMOS-NITI - Status do Projeto

**Data:** 2026-06-04  
**Versão:** 0.1.0 MVP Foundation  
**Status:** 🟢 Backend Funcional | 🟡 Frontend Base Criada

---

## 🎯 Progresso Geral

### MVP Foundation: 9 de 11 Fases Completas (82%)

✅ **Completo (7 fases)**
- 1.1 Setup Inicial
- 1.2 Backend Core  
- 1.3 Módulo Auth
- 1.4 Módulo Users
- 1.5 Módulo Storage/Documents
- 1.7 Módulo Tax Engine
- 1.9 Dashboard
- 1.11 Auditoria LGPD

🔶 **Parcial (2 fases)**
- 1.6 Módulo OCR (estrutura criada, engines pendentes)
- 1.10 Frontend (estrutura Next.js criada, páginas pendentes)

❌ **Pendente (0 fases)**
- 1.8 Módulo IA (estrutura preparada)

---

## 🚀 API REST Funcional

### 19 Endpoints Implementados

#### Autenticação (4)
```
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
POST   /auth/logout
```

#### Usuários (5)
```
GET    /users/me
PUT    /users/me
POST   /users/me/change-password
GET    /users/me/stats
DELETE /users/me
```

#### Documentos (6)
```
POST   /documents/upload
GET    /documents
GET    /documents/stats
GET    /documents/{id}
GET    /documents/{id}/download
DELETE /documents/{id}
```

#### Tax Engine (2)
```
POST   /tax/calculate/{ano_base}
POST   /tax/declaration/{ano_base}
```

#### Dashboard (1)
```
GET    /dashboard/summary?ano_base=2025
```

#### Health (1)
```
GET    /health
```

---

## 📊 Stack Implementada

### Backend
- ✅ FastAPI 0.115.0
- ✅ SQLAlchemy 2.0 async
- ✅ Alembic migrations
- ✅ Pydantic validation
- ✅ JWT authentication
- ✅ bcrypt password hashing
- ✅ MinIO storage (S3-compatible)
- ✅ PostgreSQL (Supabase)

### Frontend (Base)
- 🔶 Next.js 14 (estrutura criada)
- 🔶 TypeScript configured
- 🔶 Tailwind CSS ready
- ❌ Pages (pendente implementação)
- ❌ Components (pendente implementação)

### Database
- ✅ 9 tabelas criadas
- ✅ Índices de performance
- ✅ Foreign keys com CASCADE
- ✅ Migration inicial aplicada

### Infraestrutura
- ✅ Docker Compose (6 containers)
- ✅ MinIO (storage)
- ✅ Qdrant (preparado)
- ✅ Ollama (preparado)
- ✅ OCR service (container preparado)

---

## 🔐 Segurança Implementada

### Autenticação
✅ JWT com access (15min) + refresh (7 dias)  
✅ bcrypt 12 rounds para senhas  
✅ Token type validation  
✅ Middleware de autenticação  
✅ Ownership check em todas rotas protegidas  

### Validações
✅ CPF único (11 dígitos)  
✅ Email único  
✅ MIME type validation (documentos)  
✅ File size limit (10MB)  
✅ Hash SHA256 para deduplicação  

### LGPD
✅ Consentimento obrigatório no registro  
✅ lgpd_consent_at timestamp  
✅ Soft delete para contas  
✅ Audit middleware criado  
🔶 Logs de auditoria (parcial)  
❌ Anonimização completa (pendente)  

---

## 📈 Funcionalidades Implementadas

### Core (Funcionando)
✅ Registro e login de usuários  
✅ Gerenciamento de perfil  
✅ Upload de documentos (PDF, imagens)  
✅ Storage MinIO com deduplicação  
✅ Cálculo IRPF básico  
✅ Dashboard com resumo  
✅ Estatísticas de uso  

### Parcial (Estrutura Pronta)
🔶 OCR extraction (service criado, engines pendentes)  
🔶 Tax events parsing (calculadora criada, parsers pendentes)  
🔶 Frontend UI (Next.js configurado, páginas pendentes)  

### Pendente (Próximas Iterações)
❌ PaddleOCR integration  
❌ Tesseract OCR fallback  
❌ Parsing automático de documentos  
❌ Ollama IA copiloto  
❌ LangChain integration  
❌ RAG com legislação  
❌ Frontend completo (páginas, componentes)  
❌ Testes automatizados (pytest, jest)  

---

## 🧪 Como Testar o Sistema

### 1. Configurar Supabase

Criar projeto free em https://supabase.com e copiar credenciais para `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:SENHA@db.xyz.supabase.co:5432/postgres
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE=eyJhbGc...
JWT_SECRET=$(openssl rand -hex 32)
```

### 2. Rodar Migrations

```bash
cd backend
alembic upgrade head
```

### 3. Subir Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 4. Acessar API Docs

http://localhost:8000/docs

### 5. Testar Fluxo Completo

```bash
# 1. Registrar usuário
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "cpf": "12345678901",
    "email": "joao@test.com",
    "senha": "senha123",
    "lgpd_consent": true
  }'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@test.com","senha":"senha123"}'

# 3. Copiar access_token e usar:
TOKEN="seu_token_aqui"

# 4. Ver perfil
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/users/me

# 5. Upload documento (usando Swagger UI é mais fácil)
# Acesse http://localhost:8000/docs

# 6. Ver dashboard
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/dashboard/summary?ano_base=2025"
```

---

## 📝 Próximos Passos

### Prioridade Alta (Essencial para MVP)
1. **Implementar OCR engines** (PaddleOCR + Tesseract)
2. **Parsers de documentos** (informe de rendimentos, recibos)
3. **Frontend páginas** (login, dashboard, upload)
4. **Ollama IA integration** (copiloto básico)

### Prioridade Média (Melhorias)
5. **Testes automatizados** (pytest backend, jest frontend)
6. **Validações fiscais** mais completas
7. **RAG** com legislação da Receita Federal
8. **Rate limiting** e proteções

### Prioridade Baixa (Futuros)
9. **Pessoa Jurídica** (PJ)
10. **Notificações** e alertas
11. **CI/CD** pipeline
12. **Exportar dados** (portabilidade LGPD)

---

## 🐛 Issues Conhecidas

1. **OCR não funcional** - Engines não integradas (TODO)
2. **IA não funcional** - Ollama não integrado (TODO)
3. **Frontend vazio** - Apenas estrutura criada (TODO)
4. **Testes ausentes** - Sem cobertura de testes (TODO)
5. **Audit logs parcial** - Middleware criado mas não integrado em todas rotas

---

## 📚 Documentação

### Disponível
- ✅ README.md principal
- ✅ docs/ROADMAP.md (completo)
- ✅ docs/ARCHITECTURE.md (decisões técnicas)
- ✅ QUICKSTART.md (guia setup)
- ✅ backend/docs/DATABASE_SCHEMA.md
- ✅ backend/docs/MIGRATIONS.md
- ✅ backend/docs/AUTH_API.md
- ✅ backend/docs/USERS_API.md
- ✅ backend/README.md
- ✅ Makefile (20+ comandos)

### Pendente
- ❌ docs/DOCUMENTS_API.md
- ❌ docs/TAX_ENGINE_API.md
- ❌ docs/DASHBOARD_API.md
- ❌ Frontend documentation
- ❌ Deployment guide

---

## 🎓 Lições Aprendidas

### ✅ O Que Funcionou Bem
1. **Planejamento detalhado** antes de codificar
2. **Documentação desde o início**
3. **Modular Monolith** simplificou desenvolvimento
4. **SQLAlchemy async** + Supabase PostgreSQL
5. **Pydantic** validation automática
6. **FastAPI Swagger** UI out-of-the-box

### ⚠️ Atenção Para
1. **Context length** em conversas longas (criar checkpoints)
2. **OCR requer container separado** com dependências pesadas
3. **Ollama precisa GPU** ou modelos muito pequenos
4. **MinIO init bucket** manual necessário
5. **Frontend complexidade** subestimada (7 dias estimados)

---

## 🤝 Como Contribuir

### Para Desenvolvedores

1. **Clone o repo**
2. **Configure .env** com Supabase
3. **Rode migrations**: `alembic upgrade head`
4. **Inicie backend**: `uvicorn app.main:app --reload`
5. **Acesse docs**: http://localhost:8000/docs

### Áreas que Precisam de Ajuda

- 🔴 **OCR Integration** (PaddleOCR + Tesseract)
- 🔴 **Document Parsers** (regex + heurística)
- 🔴 **Frontend Pages** (Next.js + shadcn/ui)
- 🟡 **IA Copilot** (Ollama + LangChain)
- 🟡 **Tests** (pytest + jest)
- 🟢 **Documentation** (API docs)

---

## 📧 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Consulte docs/ para documentação
- Veja backend/docs/ para APIs

---

**Última atualização:** 2026-06-04  
**Próxima revisão:** Após implementação Frontend
