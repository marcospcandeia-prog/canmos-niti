# Users API Documentation

API de gerenciamento de perfil de usuário do CANMOS-NITI.

**Todas as rotas requerem autenticação.**

---

## Endpoints

Base URL: `http://localhost:8000/users`

**Header obrigatório:**
```http
Authorization: Bearer {access_token}
```

---

### 1. GET /users/me

Obter perfil do usuário autenticado.

**Request:**
```http
GET /users/me
Authorization: Bearer eyJhbGc...
```

**Response (200 OK):**
```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "nome": "João da Silva",
  "cpf": "12345678900",
  "email": "joao@example.com",
  "telefone": "11999999999",
  "status": "active",
  "lgpd_consent_at": "2026-06-03T22:00:00",
  "created_at": "2026-06-03T22:00:00",
  "updated_at": "2026-06-03T22:00:00",
  "profissao": "Engenheiro de Software",
  "estado_civil": "casado",
  "possui_dependentes": true,
  "possui_investimentos": true
}
```

**Errors:**
- `401 Unauthorized` - Token inválido ou expirado

---

### 2. PUT /users/me

Atualizar perfil do usuário.

**Request:**
```http
PUT /users/me
Authorization: Bearer eyJhbGc...
Content-Type: application/json
```

```json
{
  "nome": "João da Silva Santos",
  "telefone": "11988887777",
  "profissao": "Engenheiro de Software Sênior",
  "estado_civil": "casado",
  "possui_dependentes": true,
  "possui_investimentos": true
}
```

**Campos opcionais:**
- `nome`: Nome completo (string, 3-255 caracteres)
- `telefone`: Telefone (string, max 20 caracteres)
- `profissao`: Profissão (string, max 255 caracteres)
- `estado_civil`: Estado civil (enum: "solteiro", "casado", "divorciado", "viuvo")
- `possui_dependentes`: Possui dependentes fiscais (boolean)
- `possui_investimentos`: Possui investimentos (boolean)

**Nota:** Envie apenas os campos que deseja atualizar.

**Response (200 OK):**
```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "nome": "João da Silva Santos",
  "cpf": "12345678900",
  "email": "joao@example.com",
  "telefone": "11988887777",
  "status": "active",
  "lgpd_consent_at": "2026-06-03T22:00:00",
  "created_at": "2026-06-03T22:00:00",
  "updated_at": "2026-06-03T22:30:00",
  "profissao": "Engenheiro de Software Sênior",
  "estado_civil": "casado",
  "possui_dependentes": true,
  "possui_investimentos": true
}
```

**Errors:**
- `401 Unauthorized` - Token inválido
- `422 Unprocessable Entity` - Dados inválidos

---

### 3. POST /users/me/change-password

Alterar senha do usuário.

**Request:**
```http
POST /users/me/change-password
Authorization: Bearer eyJhbGc...
Content-Type: application/json
```

```json
{
  "senha_atual": "senhaAntiga123",
  "senha_nova": "senhaNova456",
  "senha_nova_confirmacao": "senhaNova456"
}
```

**Validações:**
- `senha_atual`: Deve ser a senha atual correta
- `senha_nova`: Mínimo 8 caracteres
- `senha_nova_confirmacao`: Deve ser igual a `senha_nova`

**Response (200 OK):**
```json
{
  "message": "Senha alterada com sucesso"
}
```

**Errors:**
- `400 Bad Request` - Senha atual incorreta
- `401 Unauthorized` - Token inválido
- `422 Unprocessable Entity` - Senhas não conferem ou inválidas

---

### 4. GET /users/me/stats

Obter estatísticas do usuário.

**Request:**
```http
GET /users/me/stats
Authorization: Bearer eyJhbGc...
```

**Response (200 OK):**
```json
{
  "total_documents": 15,
  "documents_processed": 12,
  "total_tax_events": 45,
  "declarations_count": 2,
  "last_activity": "2026-06-03T22:00:00"
}
```

**Campos:**
- `total_documents`: Total de documentos enviados
- `documents_processed`: Documentos processados com sucesso
- `total_tax_events`: Total de eventos tributários gerados
- `declarations_count`: Total de declarações criadas
- `last_activity`: Data/hora da última atividade (nullable)

**Errors:**
- `401 Unauthorized` - Token inválido

---

### 5. DELETE /users/me

Desativar conta do usuário (soft delete).

**Request:**
```http
DELETE /users/me
Authorization: Bearer eyJhbGc...
```

**Response (200 OK):**
```json
{
  "message": "Conta desativada com sucesso"
}
```

**Importante:**
- Esta ação apenas desativa a conta (soft delete)
- O usuário não poderá mais fazer login
- Os dados são mantidos por requisitos legais e LGPD
- Para exclusão completa dos dados, entre em contato com o suporte

**LGPD:**
- Direito ao esquecimento: os dados serão anonimizados após o período de retenção legal
- Logs de auditoria são mantidos por requisitos fiscais

**Errors:**
- `401 Unauthorized` - Token inválido

---

## Exemplos de Uso

### JavaScript (Fetch)

```javascript
// 1. Obter perfil
const token = localStorage.getItem('access_token');

const profileResponse = await fetch('http://localhost:8000/users/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const profile = await profileResponse.json();
console.log(profile);

// 2. Atualizar perfil
const updateResponse = await fetch('http://localhost:8000/users/me', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    profissao: 'Desenvolvedor Full Stack',
    possui_dependentes: true
  })
});

const updatedProfile = await updateResponse.json();

// 3. Alterar senha
const passwordResponse = await fetch('http://localhost:8000/users/me/change-password', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    senha_atual: 'senhaAntiga',
    senha_nova: 'senhaNova123',
    senha_nova_confirmacao: 'senhaNova123'
  })
});

const result = await passwordResponse.json();
console.log(result.message);

// 4. Obter estatísticas
const statsResponse = await fetch('http://localhost:8000/users/me/stats', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const stats = await statsResponse.json();
console.log('Total documentos:', stats.total_documents);

// 5. Desativar conta
const deleteResponse = await fetch('http://localhost:8000/users/me', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const deleteResult = await deleteResponse.json();
console.log(deleteResult.message);
```

### cURL

```bash
# Definir token
TOKEN="seu_access_token_aqui"

# 1. Obter perfil
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN"

# 2. Atualizar perfil
curl -X PUT http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva Santos",
    "profissao": "Desenvolvedor",
    "possui_dependentes": true
  }'

# 3. Alterar senha
curl -X POST http://localhost:8000/users/me/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "senha_atual": "senhaAntiga",
    "senha_nova": "senhaNova123",
    "senha_nova_confirmacao": "senhaNova123"
  }'

# 4. Obter estatísticas
curl -X GET http://localhost:8000/users/me/stats \
  -H "Authorization: Bearer $TOKEN"

# 5. Desativar conta
curl -X DELETE http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Python (httpx)

```python
import httpx

BASE_URL = "http://localhost:8000"
token = "seu_access_token_aqui"
headers = {"Authorization": f"Bearer {token}"}

async with httpx.AsyncClient() as client:
    # 1. Obter perfil
    response = await client.get(f"{BASE_URL}/users/me", headers=headers)
    profile = response.json()
    print(profile)
    
    # 2. Atualizar perfil
    update_data = {
        "profissao": "Engenheiro de Software",
        "possui_investimentos": True
    }
    response = await client.put(
        f"{BASE_URL}/users/me",
        headers=headers,
        json=update_data
    )
    updated_profile = response.json()
    
    # 3. Obter estatísticas
    response = await client.get(f"{BASE_URL}/users/me/stats", headers=headers)
    stats = response.json()
    print(f"Total documentos: {stats['total_documents']}")
```

---

## Fluxo Típico

```
1. Usuário faz login
   POST /auth/login
   → Recebe access_token

2. Obter perfil inicial
   GET /users/me
   → Mostra dados do usuário

3. Atualizar informações
   PUT /users/me
   → Adiciona profissão, estado civil, etc

4. Ver estatísticas
   GET /users/me/stats
   → Dashboard com resumo de uso

5. Alterar senha (opcional)
   POST /users/me/change-password
   → Troca senha com segurança

6. Desativar conta (raro)
   DELETE /users/me
   → Conta desativada (soft delete)
```

---

## Campos Não Editáveis

Os seguintes campos **não podem** ser alterados via API:

- `id` - ID interno
- `uuid` - UUID externo
- `cpf` - CPF (imutável por requisitos fiscais)
- `email` - Email (requer validação separada - futuro)
- `status` - Status da conta (gerenciado pelo sistema)
- `lgpd_consent_at` - Data de consentimento (imutável)
- `created_at` - Data de criação
- `updated_at` - Data de atualização (automática)

Para alterar **email**, será necessário endpoint específico com validação por email (implementação futura).

---

## LGPD e Privacidade

### Dados Coletados
- Nome, CPF, email, telefone (obrigatórios no registro)
- Profissão, estado civil (opcionais)
- Flags de dependentes e investimentos (opcionais)

### Direitos do Usuário
1. **Acesso**: `GET /users/me` - ver todos seus dados
2. **Retificação**: `PUT /users/me` - corrigir dados incorretos
3. **Exclusão**: `DELETE /users/me` - desativar conta
4. **Portabilidade**: (futuro) exportar dados em JSON

### Retenção de Dados
- Dados mantidos enquanto conta estiver ativa
- Após desativação: período de retenção legal (5 anos fiscais)
- Anonimização após período de retenção
- Logs de auditoria mantidos por requisitos legais

---

## Segurança

### Autenticação
- Todas rotas requerem JWT válido
- Token deve estar no header: `Authorization: Bearer {token}`
- Token expira em 15 minutos (renovar com `/auth/refresh`)

### Proteção de Dados
- Senha nunca retornada em responses
- CPF não pode ser alterado (requisito fiscal)
- Alteração de senha requer senha atual

### Rate Limiting (Futuro)
- GET: 100 requisições por minuto
- PUT/POST: 30 requisições por minuto
- DELETE: 5 requisições por hora

---

## Testing

### Swagger UI

1. Acesse: http://localhost:8000/docs
2. Faça login em `/auth/login`
3. Copie o `access_token`
4. Clique em **Authorize**
5. Cole: `Bearer {seu_token}`
6. Teste os endpoints em `/users/*`

### Postman Collection

```json
{
  "info": {
    "name": "CANMOS-NITI Users API"
  },
  "auth": {
    "type": "bearer",
    "bearer": [{"key": "token", "value": "{{access_token}}"}]
  },
  "item": [
    {
      "name": "Get Profile",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/users/me"
      }
    },
    {
      "name": "Update Profile",
      "request": {
        "method": "PUT",
        "url": "{{base_url}}/users/me",
        "body": {
          "mode": "raw",
          "raw": "{\"profissao\": \"Desenvolvedor\"}"
        }
      }
    }
  ]
}
```

---

## Errors Reference

| Status Code | Descrição | Causa |
|-------------|-----------|-------|
| 200 | OK | Requisição bem-sucedida |
| 400 | Bad Request | Senha atual incorreta |
| 401 | Unauthorized | Token inválido ou expirado |
| 422 | Unprocessable Entity | Dados de entrada inválidos |
| 500 | Internal Server Error | Erro interno do servidor |

---

## Próximas Features

- [ ] Alterar email (com validação por email)
- [ ] Upload de foto de perfil
- [ ] Preferências de notificação
- [ ] 2FA (Two-Factor Authentication)
- [ ] Exportar dados (portabilidade LGPD)
- [ ] Histórico de alterações no perfil
