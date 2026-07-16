# CANMOS-NITI - Status do Projeto

**Data:** 2026-07-16
**Versão:** 0.2.0 MVP Funcional
**Status:** 🟢 Backend Completo | 🟢 Frontend Completo | 🟢 Suítes de Teste Verdes

---

## 🎯 Progresso Geral

### MVP: Todas as 11 fases da Fase 1 concluídas + Fase 2 (Testes) concluída

✅ **Completo**
- 1.1 Setup Inicial
- 1.2 Backend Core
- 1.3 Módulo Auth (JWT access + refresh, 401 correto p/ requisições sem token)
- 1.4 Módulo Users (perfil, senha, stats, export LGPD, exclusão)
- 1.5 Módulo Storage/Documents (MinIO, dedup SHA256)
- 1.6 Módulo OCR (PaddleOCR + Tesseract fallback, worker assíncrono, API própria)
- 1.7 Módulo Tax Engine (calculadora IRPF, 6 parsers, validators, PDF da declaração)
- 1.8 Módulo IA (Ollama, RAG com Qdrant, RAG de legislação, histórico de conversas)
- 1.9 Dashboard
- 1.10 Frontend (todas as páginas, stores Zustand, componentes)
- 1.11 Auditoria LGPD
- 2.x Testes (backend 124 pytest, frontend 94 jest — todos passando)

---

## 🧪 Qualidade (verificado em 2026-07-16)

| Verificação | Resultado |
|-------------|-----------|
| Backend pytest (Python 3.12, SQLite) | ✅ 124/124 |
| Backend ruff | ✅ limpo |
| Frontend jest | ✅ 94/94 |
| Frontend tsc --noEmit | ✅ limpo |
| Frontend next lint | ✅ sem erros |
| Frontend build de produção | ✅ 13 rotas |

---

## 📦 Módulos Backend

- `auth` — registro, login, refresh, logout
- `users` — perfil, senha, stats, export de dados (LGPD), exclusão de conta
- `documents` — upload, listagem, download, stats, deleção
- `storage` — MinIO S3-compatible
- `ocr` — engines PaddleOCR/Tesseract, worker, API dedicada (container próprio)
- `tax_engine` — calculadora IRPF, parsers (informe de rendimentos, recibo
  médico, comprovante de educação, DARF, investimentos, pensão alimentícia),
  classificador de documentos, validators, geração de PDF
- `ai` — chat com Ollama, RAG (Qdrant + embeddings), RAG de legislação,
  conversas persistidas
- `dashboard` — resumo tributário e alertas
- `audit` — middleware LGPD

## 🖥️ Frontend (Next.js 15 + TypeScript)

- Páginas: home, login, register, dashboard, chat IA, declarações,
  upload de documentos, perfil, termos, privacidade
- Estado: Zustand (auth, dashboard, document, declaration, chat, profile)
- Componentes: Sidebar, StatCard, Badge, Toast, LoadingSpinner,
  DocumentDetailModal, AuthProvider
- Testes: 11 suítes Jest com mock de zustand que reseta stores entre testes

---

## 🚀 CI/CD

- GitHub Actions em `.github/workflows/ci.yml`, disparando na branch `master`
- Jobs: backend lint (ruff) → backend tests (pytest+cov) e
  frontend lint (tsc+eslint) → frontend tests → frontend build → deploy
- Deploy: Render (backend) + Vercel (frontend) via deploy hooks
  (requer secrets `RENDER_SERVICE_ID`, `RENDER_DEPLOY_KEY`,
  `VERCEL_DEPLOY_HOOK_ID`)

---

## 🔜 Próximos Passos

### Para produção
1. Configurar os secrets de deploy no GitHub (Render/Vercel)
2. Provisionar serviços gerenciados: MinIO, Qdrant e Ollama acessíveis
   pelo backend em produção
3. Rodar `alembic upgrade head` no Supabase de produção

### Melhorias
4. Anonimização completa LGPD
5. Rate limiting
6. Pessoa Jurídica (PJ)
7. Notificações

---

## 🧰 Ambiente de Desenvolvimento

- Python 3.12 (backend/venv) — `venv\Scripts\python -m pytest tests/`
- Node 20+ (frontend) — `npm test`, `npm run lint`, `npm run build`
- Docker Compose para MinIO, Qdrant, Ollama e OCR

---

**Última atualização:** 2026-07-16 (suítes verdes, CI corrigida p/ master, push realizado)
