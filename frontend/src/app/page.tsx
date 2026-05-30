import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background flex flex-col">
      {/* Hero */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 text-center py-24">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-primary/10 mb-6">
          <span className="text-4xl">🏛️</span>
        </div>
        <h1 className="text-5xl font-bold tracking-tight mb-4">
          CANMOS-NITI
        </h1>
        <p className="text-xl text-muted-foreground max-w-xl mb-2">
          Núcleo de Infraestrutura Tributária Inteligente
        </p>
        <p className="text-muted-foreground max-w-lg mb-10 text-sm">
          Declare seu IR com IA. Envie documentos, calcule restituições,
          detecte inconsistências e evite malha fina — tudo automatizado.
        </p>

        <div className="flex gap-4 flex-wrap justify-center">
          <Link
            href="/register"
            className="px-8 py-3 bg-primary text-primary-foreground rounded-xl font-semibold hover:bg-primary/90 transition"
          >
            Começar grátis
          </Link>
          <Link
            href="/login"
            className="px-8 py-3 border border-border rounded-xl font-semibold hover:bg-accent transition"
          >
            Entrar
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="border-t border-border py-16 px-4">
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { icon: "🤖", title: "IA Tributária", desc: "Análise automática dos seus documentos com inteligência artificial" },
            { icon: "📊", title: "Restituição Calculada", desc: "Veja em tempo real quanto você tem a restituir ou a pagar" },
            { icon: "🛡️", title: "LGPD-First", desc: "Seus dados protegidos com criptografia e auditoria completa" },
          ].map((f) => (
            <div key={f.title} className="text-center">
              <span className="text-4xl">{f.icon}</span>
              <h3 className="font-semibold mt-3 mb-1">{f.title}</h3>
              <p className="text-sm text-muted-foreground">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
