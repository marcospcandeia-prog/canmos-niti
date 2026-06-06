# CANMOS-NITI - Quick Start Guide

Guia rápido para subir o ambiente de desenvolvimento.

---

## Pré-requisitos

- **Docker Desktop** instalado e rodando
- **Conta Supabase** (gratuita)
- **Git** (para clonar repositório)

---

## Passo 1: Criar Projeto Supabase

1. Acesse [supabase.com](https://supabase.com) e faça login
2. Clique em "New Project"
3. Preencha:
   - Project name: `canmos-niti`
   - Database Password: Crie uma senha forte
   - Region: Escolha mais próximo (ex: South America)
4. Aguarde criação do projeto (2-3 minutos)
5. Copie as credenciais:

### Database URL
- Vá em: **Settings → Database → Connection String → URI**
- Copie a URL e **substitua `[YOUR-PASSWORD]` pela senha criada**
- Exemplo:
  ```
  postgresql://postgres:SUA_SENHA@db.xyz.supabase.co:5432/postgres
  ```
- **Converta para AsyncPG:**
  ```
  postgresql+asyncpg://postgres:SUA_SENHA@db.xyz.supabase.co:5432/postgres
  ```

### API Keys
- Vá em: **Settings → API**
- Copie:
  - **Project URL** (ex: `https://xyz.supabase.co`)
  - **anon/public key** (começa com `eyJ...`)
  - **service_role key** (começa com `eyJ...`)

---

## Passo 2: Configurar Variáveis de Ambiente

1. Na raiz do projeto, copie o arquivo exemplo:
   ```bash
   cp .env.example .env
   ```

2. Abra `.env` e preencha com suas credenciais Supabase:

```env
# Database - Supabase PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:SUA_SENHA@db.xyz.supabase.co:5432/postgres
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE=eyJhbGc...

# Security - Gerar novo JWT secret
JWT_SECRET=seu-jwt-secret-aqui-use-openssl-rand-hex-32
```

3. **Gerar JWT Secret seguro:**

   **Windows (PowerShell):**
   ```powershell
   -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) })
   ```

   **Linux/Mac:**
   ```bash
   openssl rand -hex 32
   ```

4. Cole o JWT_SECRET gerado no `.env`

---

## Passo 3: Subir Ambiente Docker

### Windows (PowerShell)

```powershell
# Executar script de inicialização
.\infra\scripts\start.ps1
```

### Linux/Mac

```bash
# Dar permissão
chmod +x infra/scripts/*.sh

# Iniciar
docker compose up -d
```

### Ou usar Makefile (Linux/Mac/Git Bash):

```bash
make start
```

---

## Passo 4: Aguardar Containers Iniciarem

Verifique se todos containers estão rodando:

```bash
docker compose ps
```

Você deve ver:
- `canmos-backend` (healthy)
- `canmos-frontend` (running)
- `canmos-minio` (running)
- `canmos-qdrant` (running)
- `canmos-ollama` (running)
- `canmos-ocr` (running)

---

## Passo 5: Download Modelo IA (Ollama)

```bash
docker exec canmos-ollama ollama pull phi3:mini
```

Aguarde download (~2GB). Isso pode levar alguns minutos.

---

## Passo 6: Rodar Migrations do Banco

```bash
cd backend
pip install alembic asyncpg  # Se não tiver localmente
alembic upgrade head
```

Isso criará todas as tabelas no Supabase PostgreSQL.

---

## Passo 7: Acessar Aplicação

### Frontend
http://localhost:3000

### Backend API (Swagger Docs)
http://localhost:8000/docs

### MinIO Console (Storage)
http://localhost:9001
- User: `minioadmin`
- Password: `minioadmin`

---

## Verificações de Saúde

### Backend Health Check
```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "ok",
  "app": "CANMOS-NITI",
  "version": "0.1.0"
}
```

### Frontend
Acesse: http://localhost:3000

---

## Comandos Úteis

### Ver Logs

```bash
# Todos containers
docker compose logs -f

# Apenas backend
docker compose logs -f backend

# Apenas frontend
docker compose logs -f frontend
```

### Parar Ambiente

```bash
docker compose down
```

### Reiniciar

```bash
docker compose restart
```

### Limpar Tudo (cuidado: remove volumes!)

```bash
docker compose down -v
```

---

## Próximos Passos

Agora que o ambiente está rodando:

1. **Desenvolver Módulo Auth** - Login/Registro
2. **Implementar Upload** - Documentos
3. **Integrar OCR** - PaddleOCR/Tesseract
4. **Tax Engine** - Cálculos IRPF
5. **Dashboard** - Interface usuário

Veja `docs/ROADMAP.md` para detalhes completos.

---

## Troubleshooting

### Container não sobe

```bash
# Ver logs de erro
docker compose logs backend

# Verificar se porta já está em uso
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac
```

### Erro de conexão com Supabase

- Verifique se DATABASE_URL está correto
- Verifique se converteu para `postgresql+asyncpg://...`
- Verifique se substituiu `[YOUR-PASSWORD]` pela senha real

### Ollama não baixa modelo

```bash
# Verificar se container está rodando
docker ps | grep ollama

# Tentar manualmente
docker exec -it canmos-ollama bash
ollama pull phi3:mini
```

### MinIO não cria bucket

```bash
# Executar script manualmente
docker exec canmos-minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec canmos-minio mc mb local/canmos-documents
```

---

## Suporte

Para dúvidas ou problemas, abra uma issue no GitHub.
