# Guia de Produção — CANMOS-NITI

## Checklist antes do deploy

### Segurança
- [ ] `JWT_SECRET_KEY` com mínimo 32 chars aleatórios
- [ ] `APP_SECRET_KEY` com mínimo 32 chars aleatórios
- [ ] `APP_DEBUG=false`
- [ ] `APP_ENV=production`
- [ ] Senhas do banco fortes e únicas
- [ ] Chaves MinIO fortes

### Stripe
- [ ] Conta Stripe criada e verificada
- [ ] `STRIPE_SECRET_KEY` de produção (sk_live_...)
- [ ] Produtos e preços criados (`./infra/scripts/stripe-setup.sh`)
- [ ] Webhook configurado no Stripe Dashboard
- [ ] `STRIPE_WEBHOOK_SECRET` configurado

### Email
- [ ] Conta Resend criada
- [ ] Domínio verificado no Resend
- [ ] `RESEND_API_KEY` configurado

### Domínio
- [ ] DNS apontando para o VPS
- [ ] SSL configurado (Certbot)
- [ ] nginx.conf atualizado com domínio

---

## Deploy VPS (Oracle Cloud Free Tier)

### 1. Criar VPS
- Acesse: https://cloud.oracle.com
- Criar VM: Ubuntu 22.04, ARM, 4 vCPU, 24GB RAM
- Gerar chave SSH e salvar

### 2. Setup inicial
```bash
ssh ubuntu@IP_DO_VPS
bash <(curl -s https://raw.githubusercontent.com/SEU_USER/canmos-niti/main/infra/scripts/deploy-vps.sh)
```

### 3. Configurar secrets GitHub (CI/CD automático)
```
Settings → Secrets → Actions:
VPS_HOST = IP do servidor
VPS_USER = ubuntu
VPS_SSH_KEY = conteúdo da chave privada SSH
```

### 4. Deploy automático
Todo push na branch `main` faz deploy automático via GitHub Actions.

---

## Variáveis de ambiente de produção

Copie `.env.example` para `.env.prod` e configure:

```bash
APP_ENV=production
APP_DEBUG=false
APP_SECRET_KEY=<32+ chars aleatórios>
JWT_SECRET_KEY=<32+ chars aleatórios>
DATABASE_URL=postgresql://user:pass@postgres:5432/canmos_niti
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
RESEND_API_KEY=re_...
```

---

## Monitoramento

### Logs em tempo real
```bash
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
```

### Status dos serviços
```bash
docker compose -f docker-compose.prod.yml ps
```

### Health check
```bash
curl https://seudominio.com.br/health
```

---

## Backup automático

```bash
# Adicionar ao crontab do servidor
0 3 * * * docker compose -f /opt/canmos-niti/docker-compose.prod.yml exec -T postgres pg_dump -U canmos canmos_niti > /backups/canmos-$(date +%Y%m%d).sql
```
