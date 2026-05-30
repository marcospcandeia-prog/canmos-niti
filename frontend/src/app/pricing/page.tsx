"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { api } from "@/services/api";
import { useAuthStore } from "@/modules/auth/store";

const PLANS = [
  {
    key: "free",
    name: "Free",
    price: "Grátis",
    period: "para sempre",
    color: "border-border",
    badge: null,
    features: [
      "Até 3 documentos",
      "OCR básico",
      "Dashboard simplificado",
      "Sem chat IA",
    ],
    cta: "Começar grátis",
    action: "register",
  },
  {
    key: "premium_monthly",
    name: "Premium",
    price: "R$ 29,90",
    period: "por mês",
    color: "border-primary",
    badge: "Mais popular",
    features: [
      "Documentos ilimitados",
      "OCR avançado (PaddleOCR)",
      "Tax Engine completo",
      "Chat IA tributário",
      "Simulador IRPF",
      "Alertas malha fina",
      "Exportar declaração",
    ],
    cta: "Assinar mensal",
    action: "checkout",
  },
  {
    key: "premium_annual",
    name: "Premium Anual",
    price: "R$ 199,00",
    period: "por ano · economize 44%",
    color: "border-emerald-500",
    badge: "Melhor valor",
    features: [
      "Tudo do Premium",
      "Prioridade no suporte",
      "Acesso antecipado a novidades",
      "2 meses grátis",
    ],
    cta: "Assinar anual",
    action: "checkout",
  },
];

export default function PricingPage() {
  const router = useRouter();
  const { accessToken } = useAuthStore();
  const [loading, setLoading] = useState<string | null>(null);

  async function handleCheckout(planKey: string) {
    if (!accessToken) {
      router.push("/register");
      return;
    }
    setLoading(planKey);
    try {
      const res = await api.post(
        "/api/v1/payments/checkout",
        {
          plan: planKey,
          success_url: `${window.location.origin}/dashboard?success=true`,
          cancel_url: `${window.location.origin}/pricing`,
        },
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      window.location.href = res.data.checkout_url;
    } catch {
      toast.error("Erro ao iniciar checkout. Tente novamente.");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border px-6 py-4 flex items-center justify-between max-w-6xl mx-auto">
        <button onClick={() => router.push("/")} className="flex items-center gap-2">
          <span className="text-2xl">🏛️</span>
          <span className="font-bold">CANMOS-NITI</span>
        </button>
        <button onClick={() => router.push(accessToken ? "/dashboard" : "/login")}
          className="text-sm text-muted-foreground hover:text-foreground">
          {accessToken ? "Dashboard →" : "Entrar"}
        </button>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-20">
        {/* Hero */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold mb-4">Planos simples, sem surpresas</h1>
          <p className="text-muted-foreground text-lg">
            Declare seu IR com IA. Comece grátis, evolua quando precisar.
          </p>
        </div>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {PLANS.map((plan) => (
            <div
              key={plan.key}
              className={`bg-card border-2 ${plan.color} rounded-2xl p-8 flex flex-col relative`}
            >
              {plan.badge && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-primary text-primary-foreground text-xs font-semibold rounded-full">
                  {plan.badge}
                </span>
              )}
              <div className="mb-6">
                <h2 className="font-bold text-lg mb-2">{plan.name}</h2>
                <div className="flex items-end gap-1">
                  <span className="text-3xl font-bold">{plan.price}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">{plan.period}</p>
              </div>

              <ul className="space-y-2.5 flex-1 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm">
                    <span className="text-emerald-500">✓</span>
                    {f}
                  </li>
                ))}
              </ul>

              <button
                onClick={() =>
                  plan.action === "register"
                    ? router.push("/register")
                    : handleCheckout(plan.key)
                }
                disabled={loading === plan.key}
                className={`w-full py-3 rounded-xl font-semibold text-sm transition ${
                  plan.color === "border-primary"
                    ? "bg-primary text-primary-foreground hover:bg-primary/90"
                    : "border border-border hover:bg-accent"
                } disabled:opacity-60`}
              >
                {loading === plan.key ? "Redirecionando..." : plan.cta}
              </button>
            </div>
          ))}
        </div>

        {/* Trust signals */}
        <div className="mt-16 text-center">
          <p className="text-sm text-muted-foreground mb-4">
            Pagamentos processados com segurança pelo Stripe · Cancele quando quiser
          </p>
          <div className="flex justify-center gap-8 text-xs text-muted-foreground">
            <span>🔒 LGPD compliant</span>
            <span>🔐 SSL/TLS</span>
            <span>💳 Stripe Secure</span>
            <span>🛡️ Dados criptografados</span>
          </div>
        </div>
      </main>
    </div>
  );
}
