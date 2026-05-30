# 🏛️ CANMOS-NITI
**Núcleo de Infraestrutura Tributária Inteligente**

Plataforma SaaS de IRPF com IA — automatize declarações, calcule restituições e evite malha fina.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Next.js 15 + TailwindCSS + shadcn/ui |
| Backend | FastAPI + Python |
| Banco | PostgreSQL |
| Storage | MinIO |
| IA | Ollama + LangChain |
| OCR | PaddleOCR + Tesseract |
| Vetorial | Qdrant |
| Infra | Docker Compose |
| Pagamentos | Stripe |

---

## Início rápido

```bash
# 1. Clonar
git clone <repo>
cd CANMOS-NITI

# 2. Setup automático
chmod +x infra/scripts/setup.sh
./infra/scripts/setup.sh

# 3. Acessar
# Frontend:  http://localhost:3000
# API Docs:  http://localhost:8000/docs
# MinIO:     http://localhost:9001
```

---

## Serviços e portas

| Serviço | Porta |
|---|---|
| Frontend | 3000 |
| Backend API | 8000 |
| PostgreSQL | 5432 |
| MinIO API | 9000 |
| MinIO Console | 9001 |
| Qdrant | 6333 |
| Ollama | 11434 |
| OCR Service | 8001 |

---

## Estrutura

```
canmos-niti/
├── frontend/          # Next.js 15
├── backend/           # FastAPI
│   └── app/
│       ├── modules/   # auth, users, documents, tax_engine, ai, dashboard
│       ├── core/      # config, database, security, middleware
│       └── shared/    # models, schemas, services
├── infra/             # Docker, nginx, scripts
└── docs/              # Documentação
```

---

## Fluxo principal

```
Upload → Storage → OCR → TAX_EVENTS → Tax Engine → Dashboard
```

---

## Roadmap

- [x] **Fase 1** — Foundation (auth, banco, storage, dashboard)
- [ ] **Fase 2** — Document Pipeline (OCR, TAX_EVENTS)
- [ ] **Fase 3** — Tax Engine completo
- [ ] **Fase 4** — IA Tributária (Ollama + LangChain)
- [ ] **Fase 5** — Pagamentos (Stripe)
- [ ] **Fase 6** — Deploy produção

---

## LGPD

O sistema implementa LGPD-first:
- Consentimento explícito no cadastro
- Auditoria completa de ações
- Isolamento por usuário
- Preparado para exclusão de dados

---

Construído com ❤️ como infraestrutura tributária inteligente escalável.
