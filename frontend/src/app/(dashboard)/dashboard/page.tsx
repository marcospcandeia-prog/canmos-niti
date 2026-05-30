"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { api } from "@/services/api";
import { useAuthStore } from "@/modules/auth/store";

interface DashboardSummary {
  usuario: { nome: string; plano: string };
  documentos: { total: number; processados: number; pendentes: number };
  resumo_fiscal: {
    rendimentos_tributaveis: number;
    retencoes_fonte: number;
    deducoes_medicas: number;
    restituicao_estimada: number;
    status: string;
  };
  alertas: { tipo: string; mensagem: string }[];
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value);
}

export default function DashboardPage() {
  const router = useRouter();
  const { accessToken, logout } = useAuthStore();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!accessToken) { router.push("/login"); return; }
    api.get("/api/v1/dashboard/summary", {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
      .then((r) => setSummary(r.data))
      .catch(() => { toast.error("Sessão expirada"); logout(); router.push("/login"); })
      .finally(() => setLoading(false));
  }, [accessToken]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  if (!summary) return null;

  const restituicao = summary.resumo_fiscal.restituicao_estimada;
  const isRestituicao = restituicao >= 0;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🏛️</span>
          <div>
            <h1 className="font-bold text-lg leading-tight">CANMOS-NITI</h1>
            <p className="text-xs text-muted-foreground">Infraestrutura Tributária</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">Olá, {summary.usuario.nome.split(" ")[0]}</span>
          <span className="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary font-medium uppercase">
            {summary.usuario.plano}
          </span>
          <button onClick={() => { logout(); router.push("/login"); }}
            className="text-sm text-muted-foreground hover:text-foreground transition">
            Sair
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Alertas */}
        {summary.alertas.map((a, i) => (
          <div key={i} className={`mb-6 px-4 py-3 rounded-xl text-sm flex items-center gap-2 ${
            a.tipo === "warning" ? "bg-yellow-500/10 text-yellow-600 border border-yellow-500/20"
              : "bg-blue-500/10 text-blue-600 border border-blue-500/20"
          }`}>
            <span>{a.tipo === "warning" ? "⚠️" : "ℹ️"}</span>
            {a.mensagem}
          </div>
        ))}

        {/* Card principal — Restituição */}
        <div className={`rounded-2xl p-8 mb-6 ${
          isRestituicao
            ? "bg-emerald-500/10 border border-emerald-500/20"
            : "bg-red-500/10 border border-red-500/20"
        }`}>
          <p className="text-sm font-medium text-muted-foreground mb-1">
            {isRestituicao ? "💰 Restituição estimada" : "📋 Imposto a pagar estimado"}
          </p>
          <p className={`text-5xl font-bold ${isRestituicao ? "text-emerald-500" : "text-red-500"}`}>
            {formatCurrency(Math.abs(restituicao))}
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            * Estimativa baseada nos documentos processados. Pode variar com documentos adicionais.
          </p>
        </div>

        {/* Cards de métricas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {[
            { label: "Rendimentos tributáveis", value: formatCurrency(summary.resumo_fiscal.rendimentos_tributaveis), icon: "📈" },
            { label: "Retenções na fonte", value: formatCurrency(summary.resumo_fiscal.retencoes_fonte), icon: "🏦" },
            { label: "Deduções médicas", value: formatCurrency(summary.resumo_fiscal.deducoes_medicas), icon: "🏥" },
          ].map((card) => (
            <div key={card.label} className="bg-card border border-border rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2">
                <span>{card.icon}</span>
                <p className="text-xs text-muted-foreground">{card.label}</p>
              </div>
              <p className="text-2xl font-semibold">{card.value}</p>
            </div>
          ))}
        </div>

        {/* Documentos */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h2 className="font-semibold mb-4">Documentos</h2>
          <div className="grid grid-cols-3 gap-4">
            {[
              { label: "Total enviados", value: summary.documentos.total },
              { label: "Processados", value: summary.documentos.processados },
              { label: "Pendentes", value: summary.documentos.pendentes },
            ].map((d) => (
              <div key={d.label} className="text-center">
                <p className="text-3xl font-bold">{d.value}</p>
                <p className="text-xs text-muted-foreground mt-1">{d.label}</p>
              </div>
            ))}
          </div>
          <button
            onClick={() => router.push("/documents")}
            className="mt-4 w-full py-2 px-4 border border-border rounded-lg text-sm hover:bg-accent transition"
          >
            Enviar documentos →
          </button>
        </div>
      </main>
    </div>
  );
}
