"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { api } from "@/services/api";
import { useAuthStore } from "@/modules/auth/store";

interface SimResult {
  resultado: {
    modelo_recomendado: string;
    ir_devido: number;
    retencoes_fonte: number;
    restituicao: number;
    status: string;
  };
  modelo_completo: { base_calculo: number; deducoes_total: number; ir_devido: number };
  modelo_simplificado: { base_calculo: number; desconto: number; ir_devido: number };
  obrigatoriedade: { obrigatorio: boolean; motivos: string[] };
  alertas: string[];
}

const fmt = (v: number) =>
  new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(v);

export default function SimulationPage() {
  const router = useRouter();
  const { accessToken } = useAuthStore();
  const [dependentes, setDependentes] = useState(0);
  const [result, setResult] = useState<SimResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!accessToken) router.push("/login");
    else simulate();
  }, [accessToken]);

  async function simulate() {
    setLoading(true);
    try {
      const r = await api.get(`/api/v1/tax/simulation?num_dependentes=${dependentes}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setResult(r.data);
    } catch {
      toast.error("Erro ao calcular simulação");
    } finally {
      setLoading(false);
    }
  }

  const isRestituicao = result && result.resultado.restituicao >= 0;

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card px-6 py-4 flex items-center gap-3">
        <button onClick={() => router.push("/dashboard")} className="text-muted-foreground hover:text-foreground">←</button>
        <div>
          <h1 className="font-semibold">Simulador IRPF 2024</h1>
          <p className="text-xs text-muted-foreground">Motor tributário determinístico — tabela oficial RFB</p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Controles */}
        <div className="bg-card border border-border rounded-xl p-6 mb-6 flex items-center gap-6 flex-wrap">
          <div>
            <label className="block text-sm font-medium mb-1.5">Número de dependentes</label>
            <div className="flex items-center gap-3">
              <button onClick={() => setDependentes(Math.max(0, dependentes - 1))}
                className="w-8 h-8 rounded-lg border border-border flex items-center justify-center hover:bg-accent transition text-lg">−</button>
              <span className="text-2xl font-bold w-6 text-center">{dependentes}</span>
              <button onClick={() => setDependentes(Math.min(10, dependentes + 1))}
                className="w-8 h-8 rounded-lg border border-border flex items-center justify-center hover:bg-accent transition text-lg">+</button>
            </div>
          </div>
          <button onClick={simulate} disabled={loading}
            className="px-6 py-2.5 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:bg-primary/90 transition disabled:opacity-60">
            {loading ? "Calculando..." : "Recalcular"}
          </button>
        </div>

        {result && (
          <>
            {/* Resultado principal */}
            <div className={`rounded-2xl p-8 mb-6 ${isRestituicao
              ? "bg-emerald-500/10 border border-emerald-500/20"
              : "bg-red-500/10 border border-red-500/20"}`}>
              <p className="text-sm text-muted-foreground mb-1">
                {isRestituicao ? "💰 Restituição estimada" : "📋 Imposto a pagar"}
              </p>
              <p className={`text-5xl font-bold ${isRestituicao ? "text-emerald-500" : "text-red-500"}`}>
                {fmt(Math.abs(result.resultado.restituicao))}
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                Modelo recomendado: <strong className="text-foreground capitalize">{result.resultado.modelo_recomendado}</strong>
                {" · "}IR devido: <strong className="text-foreground">{fmt(result.resultado.ir_devido)}</strong>
                {" · "}Retido: <strong className="text-foreground">{fmt(result.resultado.retencoes_fonte)}</strong>
              </p>
            </div>

            {/* Comparativo de modelos */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              {[
                {
                  label: "Modelo Completo",
                  recomendado: result.resultado.modelo_recomendado === "completo",
                  items: [
                    { k: "Base de cálculo", v: fmt(result.modelo_completo.base_calculo) },
                    { k: "Total de deduções", v: fmt(result.modelo_completo.deducoes_total) },
                    { k: "IR devido", v: fmt(result.modelo_completo.ir_devido) },
                  ],
                },
                {
                  label: "Modelo Simplificado",
                  recomendado: result.resultado.modelo_recomendado === "simplificado",
                  items: [
                    { k: "Base de cálculo", v: fmt(result.modelo_simplificado.base_calculo) },
                    { k: "Desconto padrão (20%)", v: fmt(result.modelo_simplificado.desconto) },
                    { k: "IR devido", v: fmt(result.modelo_simplificado.ir_devido) },
                  ],
                },
              ].map((m) => (
                <div key={m.label} className={`bg-card rounded-xl p-5 border-2 ${
                  m.recomendado ? "border-primary" : "border-border"}`}>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold">{m.label}</h3>
                    {m.recomendado && (
                      <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full font-medium">
                        Recomendado
                      </span>
                    )}
                  </div>
                  {m.items.map((i) => (
                    <div key={i.k} className="flex justify-between text-sm py-1.5 border-b border-border last:border-0">
                      <span className="text-muted-foreground">{i.k}</span>
                      <span className="font-medium">{i.v}</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>

            {/* Alertas */}
            {result.alertas.length > 0 && (
              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-5 mb-6">
                <h3 className="font-semibold text-yellow-600 mb-3">⚠️ Alertas</h3>
                <ul className="space-y-2">
                  {result.alertas.map((a, i) => (
                    <li key={i} className="text-sm text-yellow-700 flex items-start gap-2">
                      <span className="mt-0.5">•</span>{a}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Obrigatoriedade */}
            <div className={`rounded-xl p-5 border ${result.obrigatoriedade.obrigatorio
              ? "bg-blue-500/10 border-blue-500/20"
              : "bg-emerald-500/10 border-emerald-500/20"}`}>
              <p className="text-sm font-medium">
                {result.obrigatoriedade.obrigatorio
                  ? "📋 Você é OBRIGADO a declarar o IRPF"
                  : "✅ Declaração facultativa para você"}
              </p>
              {result.obrigatoriedade.motivos.map((m, i) => (
                <p key={i} className="text-xs text-muted-foreground mt-1">• {m}</p>
              ))}
            </div>
          </>
        )}

        {!result && !loading && (
          <div className="text-center py-16 text-muted-foreground">
            <p className="text-4xl mb-4">📄</p>
            <p>Envie documentos para gerar a simulação</p>
            <button onClick={() => router.push("/documents")}
              className="mt-4 px-6 py-2 bg-primary text-primary-foreground rounded-xl text-sm hover:bg-primary/90 transition">
              Enviar documentos →
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
