"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

export default function PaymentSuccessPage() {
  const router = useRouter();
  const params = useSearchParams();

  useEffect(() => {
    if (params.get("success") === "true") {
      toast.success("🎉 Pagamento confirmado! Bem-vindo ao Premium.");
    }
    const timer = setTimeout(() => router.replace("/dashboard"), 3000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="text-6xl mb-6">🎉</div>
        <h1 className="text-2xl font-bold mb-2">Pagamento confirmado!</h1>
        <p className="text-muted-foreground mb-6">
          Sua assinatura Premium está ativa. Redirecionando para o dashboard...
        </p>
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary" />
        </div>
      </div>
    </div>
  );
}
