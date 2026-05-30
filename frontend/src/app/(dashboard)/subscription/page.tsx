"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { api } from "@/services/api";
import { useAuthStore } from "@/modules/auth/store";

interface SubInfo {
  plan: string;
  status: string;
  current_period_end?: number;
  cancel_at_period_end?: boolean;
}

export default function SubscriptionPage() {
  const router = useRouter();
  const { accessToken } = useAuthStore();
  const [info, setInfo] = useState<SubInfo | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const authHeader = { headers: { Authorization: `Bearer ${accessToken}` } };

  useEffect(() => {
    if (!accessToken) { router.push("/login"); return; }
    api.get("/api/v1/payments/subscription", authHeader)
      .then((r) => setInfo(r.data))
      .catch(() => {});
  }, [accessToken]);

  async function handleCancel() {
    if (!confirm("Tem certeza? Você perderá o acesso Premium ao fim do período.")) return;
    setCancelling(true);
    try {
      await api.delete("/api/v1/payments/subscription", authHeader);
      toast.success("Assinatura cancelada. Você mantém o acesso até o fim do período.");
      router.push("/dashboard");
    } catch {
      toast.error("Erro ao cancelar assinatura");
    } finally {
      setCancelling(false);
    }
  }

  const PLAN_LABELS: Record<string, string> = {
    free: "Free",
    premium_monthly: "Premium Mensal",
    premium_annual: "Premium Anual",
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card px-6 py-4 flex items-center gap-3">
        <button onClick={() => router.push("/dashboard")} className="text-muted-foreground hover:text-foreground">←</button>
        <h1 className="font-semibold">Minha Assinatura</h1>
      </header>

      <main className="max-w-xl mx-auto px-6 py-12">
        {info && (
          <div className="bg-card border border-border rounded-2xl p-8">
            <div className="flex items-center gap-3 mb-6">
              <span className="text-3xl">💳</span>
              <div>
                <h2 className="font-bold text-xl">{PLAN_LABELS[info.plan] || info.plan}</h2>
                <p className="text-sm text-muted-foreground capitalize">
                  Status: <span className={info.status === "active" ? "text-emerald-500" : "text-yellow-500"}>
                    {info.status === "active" ? "Ativo" : info.status}
                  </span>
                </p>
              </div>
            </div>

            {info.current_period_end && (
              <p className="text-sm text-muted-foreground mb-6">
                {info.cancel_at_period_end
                  ? "⚠️ Cancelamento agendado para "
                  : "Próxima renovação em "}
                <strong>
                  {new Date(info.current_period_end * 1000).toLocaleDateString("pt-BR")}
                </strong>
              </p>
            )}

            {info.plan === "free" ? (
              <button
                onClick={() => router.push("/pricing")}
                className="w-full py-3 bg-primary text-primary-foreground rounded-xl font-semibold hover:bg-primary/90 transition"
              >
                Fazer upgrade para Premium
              </button>
            ) : (
              <div className="space-y-3">
                <button
                  onClick={() => router.push("/pricing")}
                  className="w-full py-3 border border-border rounded-xl text-sm hover:bg-accent transition"
                >
                  Mudar plano
                </button>
                {!info.cancel_at_period_end && (
                  <button
                    onClick={handleCancel}
                    disabled={cancelling}
                    className="w-full py-3 text-red-500 border border-red-500/20 rounded-xl text-sm hover:bg-red-500/5 transition disabled:opacity-50"
                  >
                    {cancelling ? "Cancelando..." : "Cancelar assinatura"}
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
