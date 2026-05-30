# Setup de Contas Externas — CANMOS-NITI

Siga estes passos em ordem para colocar o sistema em produção.

---

## 1. GitHub — Repositório do Código

1. Acesse https://github.com/new
2. Nome: `canmos-niti` (privado)
3. No terminal do projeto:
```bash
git remote add origin https://github.com/SEU_USUARIO/canmos-niti.git
git push -u origin main
```

---

## 2. Stripe — Pagamentos

1. Crie conta em https://stripe.com/br
2. Ative sua conta (verificação de identidade)
3. No Dashboard Stripe → **Desenvolvedores → Chaves de API**:
   - Copie `Chave secreta` → `.env` `STRIPE_SECRET_KEY`
   - Copie `Chave publicável` → `.env` `STRIPE_PUBLISHABLE_KEY`

4. Criar produtos (automatizado):
```bash
# Instale a Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login
bash infra/scripts/stripe-setup.sh
```
   Ou manualmente no Dashboard → Produtos → Adicionar produto

5. Configurar Webhook:
   - Dashboard → Desenvolvedores → Webhooks → Adicionar endpoint
   - URL: `https://seudominio.com.br/api/v1/payments/webhook`
   - Eventos: `checkout.session.completed`, `customer.subscription.*`
   - Copie `Signing secret` → `.env` `STRIPE_WEBHOOK_SECRET`

---

## 3. Resend — Emails transacionais

1. Crie conta em https://resend.com
2. Adicione seu domínio (DNS TXT/CNAME)
3. API Keys → Create API Key
4. Copie a chave → `.env` `RESEND_API_KEY`

---

## 4. Vercel — Frontend (deploy automático)

1. Acesse https://vercel.com
2. Import Project → seu repo GitHub `canmos-niti`
3. **Root Directory:** `frontend`
4. **Environment Variables** no Vercel:
   ```
   NEXT_PUBLIC_API_URL = https://seudominio.com.br
   ```
5. Deploy automático a cada push na `main`

---

## 5. Oracle Cloud Free Tier — VPS para Backend+IA

1. Acesse https://cloud.oracle.com/free
2. Criar conta (cartão necessário, não cobra)
3. Criar instância:
   - **Shape:** VM.Standard.A1.Flex (ARM)
   - **OCPUs:** 4 | **RAM:** 24 GB
   - **OS:** Ubuntu 22.04
   - **Storage:** 200 GB
4. Baixar chave SSH gerada
5. Conectar:
```bash
ssh -i sua_chave.pem ubuntu@IP_DO_VPS
```
6. Deploy:
```bash
bash <(curl -s https://raw.githubusercontent.com/SEU_USER/canmos-niti/main/infra/scripts/deploy-vps.sh)
```

---

## 6. Domínio (opcional mas recomendado)

- **Registro.br**: https://registro.br — domínio `.com.br` a partir de R$ 40/ano
- **Cloudflare**: DNS gratuito + CDN + SSL automático

Configuração DNS:
```
A    @          IP_DO_VPS
A    www        IP_DO_VPS
A    api        IP_DO_VPS  (ou subdomínio para o Railway)
```

---

## 7. Secrets GitHub Actions (CI/CD automático)

Em Settings → Secrets → Actions do seu repositório:
```
VPS_HOST      = IP do servidor Oracle
VPS_USER      = ubuntu
VPS_SSH_KEY   = conteúdo da chave privada SSH (-----BEGIN...)
```

---

## Checklist final antes de ir ao ar

- [ ] GitHub repo criado e código enviado
- [ ] Stripe conta ativa + produtos criados + webhook configurado
- [ ] Resend domínio verificado + API key
- [ ] VPS Oracle Cloud rodando
- [ ] Domínio apontando para VPS
- [ ] SSL ativo (Certbot)
- [ ] `.env.prod` configurado no VPS
- [ ] `docker compose -f docker-compose.prod.yml up -d` executado
- [ ] `alembic upgrade head` executado
- [ ] Ollama model baixado (`ollama pull llama3.2`)
- [ ] Vercel conectado ao GitHub
- [ ] Primeiro usuário criado e pagamento testado (modo teste Stripe)

**Tempo estimado total de setup:** 2-4 horas
