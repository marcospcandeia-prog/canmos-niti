"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";
import { api } from "@/services/api";
import { useAuthStore } from "@/modules/auth/store";

export default function RegisterPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [form, setForm] = useState({ nome: "", email: "", senha: "", lgpd_consent: false });
  const [loading, setLoading] = useState(false);

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/api/v1/auth/register", form);
      const { access_token, refresh_token } = res.data;
      setAuth(access_token, refresh_token);
      toast.success("Conta criada com sucesso!");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erro ao criar conta");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 mb-4">
            <span className="text-3xl">🏛️</span>
          </div>
          <h1 className="text-2xl font-bold">CANMOS-NITI</h1>
          <p className="text-muted-foreground mt-1 text-sm">Comece gratuitamente</p>
        </div>

        <div className="bg-card border border-border rounded-2xl p-8 shadow-lg">
          <h2 className="text-xl font-semibold mb-6">Criar conta</h2>
          <form onSubmit={handleRegister} className="space-y-4">
            {[
              { label: "Nome completo", key: "nome", type: "text", placeholder: "João Silva" },
              { label: "E-mail", key: "email", type: "email", placeholder: "seu@email.com" },
              { label: "Senha", key: "senha", type: "password", placeholder: "Mín. 8 caracteres" },
            ].map(({ label, key, type, placeholder }) => (
              <div key={key}>
                <label className="block text-sm font-medium mb-1.5">{label}</label>
                <input
                  type={type}
                  value={(form as any)[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                  placeholder={placeholder}
                  required
                  className="w-full px-4 py-2.5 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring transition"
                />
              </div>
            ))}
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={form.lgpd_consent}
                onChange={(e) => setForm({ ...form, lgpd_consent: e.target.checked })}
                className="mt-0.5"
                required
              />
              <span className="text-sm text-muted-foreground">
                Concordo com o tratamento de dados pessoais conforme a{" "}
                <span className="text-primary">LGPD</span> e os{" "}
                <span className="text-primary">Termos de Uso</span>
              </span>
            </label>
            <button
              type="submit"
              disabled={loading || !form.lgpd_consent}
              className="w-full py-2.5 px-4 bg-primary text-primary-foreground rounded-lg font-medium text-sm hover:bg-primary/90 transition disabled:opacity-60"
            >
              {loading ? "Criando conta..." : "Criar conta grátis"}
            </button>
          </form>
          <p className="text-center text-sm text-muted-foreground mt-6">
            Já tem conta?{" "}
            <Link href="/login" className="text-primary hover:underline font-medium">
              Entrar
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
