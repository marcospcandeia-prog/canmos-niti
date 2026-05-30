"""
Email Service — Resend.
Envios transacionais: boas-vindas, confirmação de pagamento, alertas.
"""
import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY

_BASE_STYLE = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #0a0a0a; color: #e5e5e5; margin: 0; padding: 0; }
.container { max-width: 560px; margin: 40px auto; padding: 0 20px; }
.card { background: #111; border: 1px solid #222; border-radius: 16px; padding: 40px; }
.logo { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
.subtitle { color: #888; font-size: 14px; margin-bottom: 32px; }
h1 { font-size: 22px; font-weight: 600; margin: 0 0 16px; }
p { color: #ccc; line-height: 1.6; margin: 0 0 16px; font-size: 15px; }
.btn { display: inline-block; background: #3b82f6; color: #fff !important;
       padding: 12px 28px; border-radius: 10px; text-decoration: none;
       font-weight: 600; font-size: 15px; margin: 8px 0; }
.highlight { background: #1a1a2e; border: 1px solid #3b82f620;
             border-radius: 12px; padding: 20px; margin: 20px 0; }
.highlight strong { color: #3b82f6; font-size: 32px; }
.footer { text-align: center; color: #555; font-size: 12px; margin-top: 32px; }
"""


def _wrap(body: str) -> str:
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{_BASE_STYLE}</style></head><body>
<div class="container"><div class="card">
<div class="logo">🏛️ CANMOS-NITI</div>
<div class="subtitle">Infraestrutura Tributária Inteligente</div>
{body}
</div>
<div class="footer">
  © 2026 CANMOS-NITI · <a href="#" style="color:#555">Cancelar inscrição</a>
</div></div></body></html>"""


def send_welcome(to_email: str, nome: str) -> bool:
    try:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": "Bem-vindo ao CANMOS-NITI 🏛️",
            "html": _wrap(f"""
<h1>Olá, {nome.split()[0]}! 👋</h1>
<p>Sua conta no <strong>CANMOS-NITI</strong> foi criada com sucesso.</p>
<p>Agora você pode enviar seus documentos e deixar a IA tributária
cuidar da análise do seu Imposto de Renda.</p>
<a href="{settings.APP_URL}/dashboard" class="btn">Acessar minha conta →</a>
<p style="margin-top:24px; font-size:13px; color:#666">
Você se cadastrou usando a plataforma CANMOS-NITI.
Seus dados são protegidos conforme a LGPD.
</p>
"""),
        })
        return True
    except Exception:
        return False


def send_payment_confirmed(to_email: str, nome: str, plano: str, valor: str) -> bool:
    try:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": "✅ Pagamento confirmado — CANMOS-NITI Premium",
            "html": _wrap(f"""
<h1>Pagamento confirmado! 🎉</h1>
<p>Olá <strong>{nome.split()[0]}</strong>, seu plano está ativo.</p>
<div class="highlight">
  <p style="margin:0; color:#888; font-size:13px">Plano contratado</p>
  <strong>{plano}</strong>
  <p style="margin:4px 0 0; color:#888; font-size:13px">{valor}</p>
</div>
<p>Agora você tem acesso a todos os recursos Premium:
documentos ilimitados, Tax Engine completo, IA tributária e muito mais.</p>
<a href="{settings.APP_URL}/dashboard" class="btn">Ir para o dashboard →</a>
"""),
        })
        return True
    except Exception:
        return False


def send_malha_fina_alert(to_email: str, nome: str, alertas: list[str]) -> bool:
    items = "".join(f"<li style='margin:4px 0; color:#f59e0b'>{a}</li>" for a in alertas)
    try:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [to_email],
            "subject": "⚠️ Alerta de inconsistência fiscal — CANMOS-NITI",
            "html": _wrap(f"""
<h1>Atenção: inconsistências detectadas ⚠️</h1>
<p>Olá <strong>{nome.split()[0]}</strong>, identificamos pontos de atenção
na sua declaração que podem aumentar o risco de malha fina:</p>
<div class="highlight">
<ul style="margin:0; padding-left:20px">{items}</ul>
</div>
<p>Acesse o dashboard para ver detalhes e corrigir antes do prazo.</p>
<a href="{settings.APP_URL}/dashboard" class="btn">Ver inconsistências →</a>
"""),
        })
        return True
    except Exception:
        return False
