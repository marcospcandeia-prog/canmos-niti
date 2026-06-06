# Database Schema - CANMOS-NITI

Documentação completa do schema do banco de dados PostgreSQL (Supabase).

---

## Diagrama ER (Resumido)

```
┌─────────────┐
│   users     │◄──────────┐
└─────┬───────┘           │
      │                   │
      │ 1:1               │ 1:N
      ▼                   │
┌──────────────┐          │
│user_profiles │          │
└──────────────┘          │
                          │
      ┌───────────────────┤
      │                   │
      ▼ 1:N               │
┌─────────────┐           │
│  documents  │           │
└─────┬───────┘           │
      │                   │
      │ 1:1               │
      ▼                   │
┌─────────────┐           │
│ ocr_results │           │
└─────────────┘           │
                          │
      ┌───────────────────┤
      │                   │
      ▼ 1:N               │
┌─────────────┐           │
│ tax_events  │           │
└─────────────┘           │
                          │
      ┌───────────────────┤
      │                   │
      ▼ 1:N               │
┌──────────────┐          │
│ declarations │          │
└─────┬────────┘          │
      │                   │
      │ 1:N               │
      ▼                   │
┌──────────────┐          │
│ validations  │          │
└──────────────┘          │
                          │
      ┌───────────────────┤
      │                   │
      ▼ 1:N               │
┌────────────────┐        │
│ai_interactions │        │
└────────────────┘        │
                          │
      ┌───────────────────┘
      │ 1:N
      ▼
┌─────────────┐
│ audit_logs  │
└─────────────┘
```

---

## Tabelas

### 1. users

Usuários do sistema (autenticação e dados pessoais).

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| `id` | Integer | Chave primária | PK, Auto Increment |
| `uuid` | UUID | Identificador externo | Unique, Index |
| `nome` | String(255) | Nome completo | NOT NULL |
| `cpf` | String(11) | CPF (apenas números) | Unique, Index, NOT NULL |
| `email` | String(255) | Email | Unique, Index, NOT NULL |
| `telefone` | String(20) | Telefone | Nullable |
| `senha_hash` | String(255) | Hash bcrypt da senha | NOT NULL |
| `status` | String(20) | Status da conta | Default: 'active' |
| `lgpd_consent_at` | DateTime | Data consentimento LGPD | Nullable |
| `created_at` | DateTime | Data criação | NOT NULL, Default: NOW() |
| `updated_at` | DateTime | Data atualização | NOT NULL, Default: NOW() |

**Valores `status`:** `active`, `inactive`, `suspended`

**Relações:**
- 1:1 com `user_profiles`
- 1:N com `documents`, `tax_events`, `declarations`, `ai_interactions`, `audit_logs`

---

### 2. user_profiles

Perfil estendido do usuário (informações complementares).

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| `id` | Integer | Chave primária | PK, Auto Increment |
| `user_id` | Integer | FK para users | FK, Unique, NOT NULL |
| `profissao` | String(255) | Profissão | Nullable |
| `estado_civil` | String(50) | Estado civil | Nullable |
| `possui_dependentes` | Boolean | Tem dependentes? | Default: false |
| `possui_investimentos` | Boolean | Tem investimentos? | Default: false |
| `created_at` | DateTime | Data criação | NOT NULL |
| `updated_at` | DateTime | Data atualização | NOT NULL |

**Valores `estado_civil`:** `solteiro`, `casado`, `divorciado`, `viuvo`

---

### 3. documents

Documentos enviados pelos usuários.

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| `id` | Integer | Chave primária | PK, Auto Increment |
| `user_id` | Integer | FK para users | FK, Index, NOT NULL |
| `tipo` | String(100) | Tipo do documento | Nullable |
| `nome_original` | String(255) | Nome do arquivo | NOT NULL |
| `storage_path` | String(500) | Caminho no MinIO | NOT NULL |
| `mime_type` | String(100) | MIME type | NOT NULL |
| `hash_arquivo` | String(64) | SHA256 hash | Index, NOT NULL |
| `status` | String(50) | Status processamento | Default: 'uploaded' |
| `created_at` | DateTime | Data upload | NOT NULL |
| `updated_at` | DateTime | Data atualização | NOT NULL |

**Valores `tipo`:** `informe_rendimentos`, `recibo_medico`, `comprovante_educacao`, `doacao`, etc

**Valores `status`:** `uploaded`, `processing`, `processed`, `error`

**Relações:**
- N:1 com `users`
- 1:1 com `ocr_results`
- 1:N com `tax_events`

---

### 4. ocr_results

Resultados da extração OCR de documentos.

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| `id` | Integer | Chave primária | PK, Auto Increment |
| `document_id` | Integer | FK para documents | FK, Unique Index, NOT NULL |
| `texto_extraido` | Text | Texto extraído | Nullable |
| `confianca` | Float | Confiança (0.0-1.0) | Nullable |
| `engine_utilizada` | String(50) | Engine OCR usada | NOT NULL |
| `status` | String(50) | Status do OCR | Default: 'pending' |
| `created_at` | DateTime | Data extração | NOT NULL |
| `updated_at` | DateTime | Data atualização | NOT NULL |

**Valores `engine_utilizada`:** `paddleocr`, `tesseract`

**Valores `status`:** `pending`, `success`, `failed`

---

### 5. tax_events

Eventos tributários (rendimentos, despesas, deduções).

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| `id` | Integer | Chave primária | PK, Auto Increment |
| `user_id` | Integer | FK para users | FK, Index, NOT NULL |
| `document_id` | Integer | FK para documents | FK, Index, Nullable |
| `categoria` | String(100) | Categoria do evento | Index, NOT NULL |
| `subcategoria` | String(100) | Subcategoria | Nullable |
| `valor` | Numeric(15,2) | Valor monetário | NOT NULL |
| `competencia` | String(7) | Mês/Ano (YYYY-MM) | Index, NOT NULL |
| `origem` | String(50) | Origem do evento | Default: 'ocr' |
| `metadata_json` | JSONB | Metadados adicionais | Nullable |
| `created_at` | DateTime | Data criação | NOT NULL |
| `updated_at` | DateTime | Data atualização | NOT NULL |

**Valores `categoria`:**
- `rendimento_trabalho`
- `rendimento_investimento`
- `despesa_medica`
- `despesa_educacao`
- `doacao`
- `pensao_alimenticia`

**Valores `origem`:** `ocr`, `manual`, `importacao`

**Índices Importantes:**
- `(user_id)`
- `(categoria)`
- `(competencia)`

---

### 6. declarations

Declarações de IRPF.

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| `id` | Integer | Chave primária | PK, Auto Increment |
| `user_id` | Integer | FK para users | FK, Index, NOT NULL |
| `ano_base` | Integer | Ano fiscal | Index, NOT NULL |
| `status` | String(50) | Status da declaração | Default: 'rascunho' |
| `restituicao_estimada` | Numeric(15,2) | Restituição estimada | Nullable |
| `imposto_devido` | Numeric(15,2) | Imposto a pagar | Nullable |
| `created_at` | DateTime | Data criação | NOT NULL |
| `updated_at` | DateTime | Data atualização | NOT NULL |

**Valores `status`:** `rascunho`, `finalizada`, `enviada`

**Índice Composto:** `(user_id, ano_base)` - Declaração única por usuário por ano

---

### 7. validations

Validações/Alertas sobre declarações.

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| `id` | Integer | Chave primária | PK, Auto Increment |
| `declaration_id` | Integer | FK para declarations | FK, Index, NOT NULL |
| `tipo` | String(100) | Tipo da validação | NOT NULL |
| `severidade` | String(20) | Severidade | Default: 'info' |
| `mensagem` | Text | Mensagem da validação | NOT NULL |
| `created_at` | DateTime | Data criação | NOT NULL |
| `updated_at` | DateTime | Data atualização | NOT NULL |

**Valores `tipo`:**
- `missing_document`
- `valor_inconsistente`
- `deducao_invalida`
- `cpf_invalido`

**Valores `severidade`:** `info`, `warning`, `error`

---

### 8. ai_interactions

Interações do usuário com o copiloto de IA.

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| `id` | Integer | Chave primária | PK, Auto Increment |
| `user_id` | Integer | FK para users | FK, Index, NOT NULL |
| `pergunta` | Text | Pergunta do usuário | NOT NULL |
| `resposta` | Text | Resposta da IA | Nullable |
| `modelo_ia` | String(50) | Modelo utilizado | NOT NULL |
| `created_at` | DateTime | Data interação | NOT NULL |
| `updated_at` | DateTime | Data atualização | NOT NULL |

**Valores `modelo_ia`:** `phi3:mini`, `qwen2:1.5b`, `mistral`, `llama3:8b`

---

### 9. audit_logs

Logs de auditoria (LGPD compliance).

| Campo | Tipo | Descrição | Constraints |
|-------|------|-----------|-------------|
| `id` | Integer | Chave primária | PK, Auto Increment |
| `user_id` | Integer | FK para users | FK, Index, Nullable |
| `action` | String(50) | Ação executada | Index, NOT NULL |
| `entity` | String(100) | Entidade afetada | Index, Nullable |
| `entity_id` | Integer | ID da entidade | Nullable |
| `metadata_json` | JSONB | Metadados da ação | Nullable |
| `created_at` | DateTime | Data da ação | Index DESC, NOT NULL |
| `updated_at` | DateTime | Data atualização | NOT NULL |

**Valores `action`:**
- `CREATE`
- `UPDATE`
- `DELETE`
- `LOGIN`
- `LOGOUT`
- `UPLOAD`
- `DOWNLOAD`
- `EXPORT`

**Valores `entity`:** `users`, `documents`, `tax_events`, `declarations`, etc

**Índices Importantes:**
- `(user_id)`
- `(action)`
- `(entity)`
- `(created_at DESC)` - Para consultas temporais rápidas

**Exemplo `metadata_json`:**
```json
{
  "ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "changes": {
    "old_value": "active",
    "new_value": "inactive"
  }
}
```

---

## Índices de Performance

### Índices Únicos
- `users.uuid`
- `users.cpf`
- `users.email`
- `user_profiles.user_id`
- `ocr_results.document_id`

### Índices Compostos
- `declarations(user_id, ano_base)` - Único por usuário/ano

### Índices Temporais
- `audit_logs.created_at DESC` - Consultas históricas

### Índices de Foreign Keys
- Todos os `user_id` são indexados
- `documents.hash_arquivo` - Deduplicação
- `tax_events.competencia` - Filtros por período

---

## Tipos de Dados Importantes

### Numeric vs Float
- **EVITAR `Float`** para valores monetários (imprecisão)
- **USAR `Numeric(15, 2)`** para:
  - `tax_events.valor`
  - `declarations.restituicao_estimada`
  - `declarations.imposto_devido`

### UUID
- Tipo nativo PostgreSQL
- Usado em `users.uuid` para referências externas

### JSONB
- Tipo nativo PostgreSQL (binário, indexável)
- Usado em `tax_events.metadata_json` e `audit_logs.metadata_json`

---

## Cascade Rules

### ON DELETE CASCADE
- `user_profiles` → `users` (perfil excluído se user excluído)
- `documents` → `users`
- `ocr_results` → `documents`
- `tax_events` → `users`
- `declarations` → `users`
- `validations` → `declarations`
- `ai_interactions` → `users`

### ON DELETE SET NULL
- `tax_events.document_id` → `documents` (preserva evento se documento excluído)
- `audit_logs.user_id` → `users` (preserva log se user excluído)

---

## Estimativa de Crescimento

### Por Usuário (1 ano)

| Tabela | Estimativa Registros | Tamanho Estimado |
|--------|----------------------|------------------|
| users | 1 | 500 bytes |
| user_profiles | 1 | 300 bytes |
| documents | 20 | 2 KB |
| ocr_results | 20 | 100 KB |
| tax_events | 50 | 5 KB |
| declarations | 1 | 500 bytes |
| validations | 10 | 2 KB |
| ai_interactions | 30 | 15 KB |
| audit_logs | 200 | 20 KB |

**Total por usuário/ano:** ~145 KB

**1000 usuários:** ~145 MB  
**10000 usuários:** ~1.45 GB

**Supabase Free Tier:** 500 MB (suficiente para ~3400 usuários)

---

## Queries Importantes

### Usuários Ativos

```sql
SELECT COUNT(*) 
FROM users 
WHERE status = 'active' 
AND created_at >= NOW() - INTERVAL '30 days';
```

### Documentos Processados Hoje

```sql
SELECT COUNT(*) 
FROM documents 
WHERE status = 'processed' 
AND DATE(created_at) = CURRENT_DATE;
```

### Restituição Média por Ano

```sql
SELECT 
  ano_base,
  AVG(restituicao_estimada) as media_restituicao,
  COUNT(*) as total_declaracoes
FROM declarations
GROUP BY ano_base
ORDER BY ano_base DESC;
```

### Eventos Tributários por Categoria (Usuário)

```sql
SELECT 
  categoria,
  SUM(valor) as total,
  COUNT(*) as quantidade
FROM tax_events
WHERE user_id = 123
  AND competencia LIKE '2025-%'
GROUP BY categoria
ORDER BY total DESC;
```

---

## Manutenção

### Vacuum (PostgreSQL)

```sql
-- Liberar espaço de registros deletados
VACUUM FULL;

-- Analisar estatísticas para otimização de queries
ANALYZE;
```

### Reindex

```sql
-- Recriar índices (se performance degradar)
REINDEX DATABASE postgres;
```

---

## Backup

### Dump Completo

```bash
pg_dump $DATABASE_URL > backup.sql
```

### Restore

```bash
psql $DATABASE_URL < backup.sql
```

### Backup Automático Supabase

- Supabase Free Tier: Backup diário automático (7 dias retenção)
- Acessar em: Dashboard → Settings → Database → Backups
