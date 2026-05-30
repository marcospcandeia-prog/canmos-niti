"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/services/api";
import { useAuthStore } from "@/modules/auth/store";

interface Metrics {
  usuarios: { total: number; premium: number; free: number; taxa_conversao: number };
  documentos: { total: number };
  tax_events: { total: number };
  ai_chats: { total: number };
  planos: Record<string, number>;
}

interface UserRow {
  id: string;
  nome: string;
  email: string;
  plano: string;
  status: string;
  documentos: number;
  created_at: string;
}

const PLAN_BADGE: Record<string, string> = {
  free: "text-muted-foreground bg-muted",
  premium_monthly: "text-blue-600 bg-blue-500/10",
  premium_annual: "text-emerald-600 bg-emerald-500/10",
};

export default function AdminPage() {
  const router = useRouter();
  const { accessToken } = useAuthStore();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [users, setUsers] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"metrics" | "users" | "logs">("metrics");

  const auth = { headers: { Authorization: `Bearer ${accessToken}` } };

  useEffect(() => {
    if (!accessToken) { router.push("/login"); return; }
    Promise.all([
      api.get("/api/v1/admin/metrics", auth).then(r => setMetrics(r.data)).catch(() => {}),
      api.get("/api/v1/admin/users", auth).then(r => setUsers(r.data.users || [])).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, [accessToken]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
  );

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🏛️</span>
          <div>
            <h1 className="font-bold">Admin Panel</h1>
            <p className="text-xs text-muted-foreground">CANMOS-NITI · Acesso restrito</p>
          </div>
        </div>
        <button onClick={() => router.push("/dashboard")} className="text-sm text-muted-foreground hover:text-foreground">
          ← Dashboard
        </button>
      </header>

      {/* Tabs */}
      <div className="border-b border-border bg-card px-6">
        {(["metrics", "users", "logs"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition capitalize ${
              tab === t ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
            }`}>
            {t === "metrics" ? "📊 Métricas" : t === "users" ? "👥 Usuários" : "📋 Logs"}
          </button>
        ))}
      </div>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* MÉTRICAS */}
        {tab === "metrics" && metrics && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "Total usuários", value: metrics.usuarios.total, icon: "👥" },
                { label: "Premium", value: metrics.usuarios.premium, icon: "⭐" },
                { label: "Taxa conversão", value: `${metrics.usuarios.taxa_conversao}%`, icon: "📈" },
                { label: "Documentos", value: metrics.documentos.total, icon: "📄" },
                { label: "TAX Events", value: metrics.tax_events.total, icon: "🧾" },
                { label: "Chats IA", value: metrics.ai_chats.total, icon: "🤖" },
              ].map((m) => (
                <div key={m.label} className="bg-card border border-border rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <span>{m.icon}</span>
                    <p className="text-xs text-muted-foreground">{m.label}</p>
                  </div>
                  <p className="text-2xl font-bold">{m.value}</p>
                </div>
              ))}
            </div>

            <div className="bg-card border border-border rounded-xl p-5">
              <h3 className="font-semibold mb-4">Distribuição de planos</h3>
              <div className="flex gap-4 flex-wrap">
                {Object.entries(metrics.planos).map(([plano, count]) => (
                  <div key={plano} className={`px-3 py-1.5 rounded-full text-xs font-medium ${PLAN_BADGE[plano] || "bg-muted"}`}>
                    {plano.replace(/_/g, " ")}: {count}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* USUÁRIOS */}
        {tab === "users" && (
          <div className="bg-card border border-border rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="border-b border-border bg-muted/30">
                <tr>
                  {["Nome", "Email", "Plano", "Docs", "Criado em"].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-medium text-muted-foreground">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-accent/30 transition">
                    <td className="px-4 py-3 font-medium">{u.nome}</td>
                    <td className="px-4 py-3 text-muted-foreground">{u.email}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${PLAN_BADGE[u.plano] || "bg-muted"}`}>
                        {u.plano.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">{u.documentos}</td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {new Date(u.created_at).toLocaleDateString("pt-BR")}
                    </td>
                  </tr>
                ))}
                {users.length === 0 && (
                  <tr><td colSpan={5} className="text-center py-8 text-muted-foreground">Nenhum usuário</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
