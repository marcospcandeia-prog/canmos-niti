# Authentication API Documentation

API de autenticação do CANMOS-NITI.

---

## Endpoints

Base URL: `http://localhost:8000/auth`

### 1. POST /auth/register

Registrar novo usuário.

**Request:**
```json
{
  "nome": "João da Silva",
  "cpf": "12345678900",
  "email": "joao@example.com",
  "telefone": "11999999999",
  "senha": "senhaSegura123",
  "lgpd_consent": true
}
```

**Response (201 Created):**
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
  "updated_at": "2026-06-03T22:00:00"
}
```

**Errors:**
- `400 Bad Request` - CPF ou email já cadastrado
- `422 Unprocessable Entity` - Dados inválidos

**Validações:**
- `nome`: Mínimo 3 caracteres
- `cpf`: Exatamente 11 dígitos (apenas números)
- `email`: Email válido
- `senha`: Mínimo 8 caracteres
- `lgpd_consent`: Deve ser `true`

---

### 2. POST /auth/login

Fazer login e obter tokens.

**Request:**
```json
{
  "email": "joao@example.com",
  "senha": "senhaSegura123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2FvQGV4YW1wbGUuY29tIiwidXNlcl9pZCI6MSwiZXhwIjoxNzM1OTQwNDAwLCJpYXQiOjE3MzU5Mzk1MDAsInR5cGUiOiJhY2Nlc3MifQ.xyz",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2FvQGV4YW1wbGUuY29tIiwidXNlcl9pZCI6MSwiZXhwIjoxNzM2NTQ0MzAwLCJpYXQiOjE3MzU5Mzk1MDAsInR5cGUiOiJyZWZyZXNoIn0.abc",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Token Info:**
- `access_token`: Válido por **15 minutos** (900 segundos)
- `refresh_token`: Válido por **7 dias**
- `token_type`: Sempre "bearer"

**Errors:**
- `401 Unauthorized` - Email ou senha incorretos
- `403 Forbidden` - Usuário inativo

---

### 3. POST /auth/refresh

Renovar access token usando refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new_token.xyz",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Errors:**
- `401 Unauthorized` - Refresh token inválido ou expirado

---

### 4. POST /auth/logout

Fazer logout (invalidar tokens).

**Request:**
```json
{}
```

**Response (200 OK):**
```json
{
  "message": "Logout realizado com sucesso"
}
```

**Nota:** 
- Implementação atual: apenas retorna mensagem de sucesso
- Frontend deve remover tokens do localStorage/cookies
- Implementação futura: blacklist de tokens no Redis

---

## Usando Tokens em Requisições

### Header de Autorização

Para acessar rotas protegidas, inclua o access token no header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Exemplo com cURL

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "senha": "senhaSegura123"
  }'

# Usar token em rota protegida
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Exemplo com JavaScript (Fetch)

```javascript
// Login
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'joao@example.com',
    senha: 'senhaSegura123'
  })
});

const data = await response.json();
const { access_token, refresh_token } = data;

// Salvar tokens
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);

// Usar token em requisição
const protectedResponse = await fetch('http://localhost:8000/users/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

### Exemplo com Axios

```javascript
import axios from 'axios';

// Configurar interceptor para adicionar token automaticamente
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login
const { data } = await axios.post('/auth/login', {
  email: 'joao@example.com',
  senha: 'senhaSegura123'
});

localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);

// Requisição protegida (token adicionado automaticamente)
const user = await axios.get('/users/me');
```

---

## Fluxo de Autenticação Recomendado

```
1. Usuário registra
   POST /auth/register
   
2. Usuário faz login
   POST /auth/login
   → Recebe access_token + refresh_token
   → Salva tokens em localStorage/cookies

3. Requisições protegidas
   GET /users/me
   Header: Authorization: Bearer {access_token}

4. Access token expira (15min)
   → Frontend detecta 401 Unauthorized
   → Frontend chama POST /auth/refresh
   → Recebe novo access_token
   → Retenta requisição original

5. Refresh token expira (7 dias)
   → Frontend redireciona para login
   → Usuário faz login novamente

6. Logout
   POST /auth/logout
   → Frontend remove tokens
   → Redireciona para página de login
```

---

## Segurança

### Password Hashing
- Algoritmo: **bcrypt**
- Cost factor: **12 rounds**
- Senhas nunca são armazenadas em plain text

### JWT Tokens

**Access Token:**
- Algoritmo: **HS256**
- Expiration: **15 minutos**
- Payload:
  ```json
  {
    "sub": "joao@example.com",
    "user_id": 1,
    "exp": 1735940400,
    "iat": 1735939500,
    "type": "access"
  }
  ```

**Refresh Token:**
- Algoritmo: **HS256**
- Expiration: **7 dias**
- Payload:
  ```json
  {
    "sub": "joao@example.com",
    "user_id": 1,
    "exp": 1736544300,
    "iat": 1735939500,
    "type": "refresh"
  }
  ```

### LGPD

- **Consentimento obrigatório** no registro (`lgpd_consent: true`)
- Data do consentimento registrada em `lgpd_consent_at`
- Todas ações de autenticação podem ser auditadas

---

## Errors Reference

| Status Code | Descrição | Causa |
|-------------|-----------|-------|
| 200 | OK | Requisição bem-sucedida |
| 201 | Created | Usuário criado com sucesso |
| 400 | Bad Request | CPF ou email já cadastrado |
| 401 | Unauthorized | Credenciais inválidas ou token expirado |
| 403 | Forbidden | Usuário inativo |
| 422 | Unprocessable Entity | Dados de entrada inválidos |
| 500 | Internal Server Error | Erro interno do servidor |

---

## Rate Limiting (Futuro)

**Planejado:**
- Login: 5 tentativas por IP a cada 15 minutos
- Register: 3 registros por IP por hora
- Refresh: 10 renovações por usuário a cada hora

**Implementação:** Redis + middleware FastAPI

---

## Testing

### Swagger UI

Acesse: http://localhost:8000/docs

1. Clique em **POST /auth/register** → Try it out
2. Preencha os dados → Execute
3. Copie o `access_token` do response
4. Clique em **Authorize** (canto superior direito)
5. Cole o token: `Bearer {seu_token}`
6. Agora você pode testar rotas protegidas

### cURL Examples

```bash
# Registrar
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste User",
    "cpf": "11122233344",
    "email": "teste@example.com",
    "senha": "senha123",
    "lgpd_consent": true
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "senha": "senha123"
  }'

# Refresh (copie refresh_token do login)
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "SEU_REFRESH_TOKEN"
  }'

# Logout
curl -X POST http://localhost:8000/auth/logout \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Próximos Passos

- [ ] Implementar blacklist de refresh tokens (Redis)
- [ ] Rate limiting
- [ ] 2FA (Two-Factor Authentication)
- [ ] Password reset
- [ ] Email verification
- [ ] OAuth2 (Google, Facebook)
