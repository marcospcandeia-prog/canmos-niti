import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <p className="text-8xl font-bold text-muted-foreground/20 mb-4">404</p>
        <h1 className="text-2xl font-bold mb-2">Página não encontrada</h1>
        <p className="text-muted-foreground mb-8">
          A página que você procura não existe ou foi removida.
        </p>
        <Link href="/" className="px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition">
          Voltar ao início
        </Link>
      </div>
    </div>
  );
}
