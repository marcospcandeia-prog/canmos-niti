"use client";

import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { api } from "@/services/api";
import { useAuthStore } from "@/modules/auth/store";

interface Document {
  id: string;
  nome_original: string;
  tipo: string;
  status: string;
  mime_type: string;
  created_at: string;
}

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  uploaded: { label: "Enviado", color: "text-yellow-500" },
  processing: { label: "Processando...", color: "text-blue-500" },
  ocr_done: { label: "OCR concluído", color: "text-blue-400" },
  classified: { label: "Classificado", color: "text-purple-500" },
  tax_events_created: { label: "✓ Processado", color: "text-emerald-500" },
  error: { label: "Erro", color: "text-red-500" },
};

export default function DocumentsPage() {
  const router = useRouter();
  const { accessToken } = useAuthStore();
  const [docs, setDocs] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);

  const authHeader = { headers: { Authorization: `Bearer ${accessToken}` } };

  async function loadDocs() {
    try {
      const res = await api.get("/api/v1/documents/", authHeader);
      setDocs(res.data);
    } catch { }
  }

  useEffect(() => {
    if (!accessToken) { router.push("/login"); return; }
    loadDocs();
    const interval = setInterval(loadDocs, 5000); // polling status
    return () => clearInterval(interval);
  }, [accessToken]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (!acceptedFiles.length) return;
    setUploading(true);

    for (const file of acceptedFiles) {
      const formData = new FormData();
      formData.append("file", file);
      try {
        await api.post("/api/v1/documents/upload", formData, {
          headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "multipart/form-data" },
        });
        toast.success(`${file.name} enviado — OCR iniciado`);
      } catch (err: any) {
        toast.error(err?.response?.data?.detail || `Erro ao enviar ${file.name}`);
      }
    }

    setUploading(false);
    loadDocs();
  }, [accessToken]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"] },
    maxSize: 10 * 1024 * 1024,
  });

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card px-6 py-4 flex items-center gap-3">
        <button onClick={() => router.push("/dashboard")} className="text-muted-foreground hover:text-foreground">←</button>
        <div>
          <h1 className="font-semibold">Documentos</h1>
          <p className="text-xs text-muted-foreground">Envie PDFs, fotos e informes para análise automática</p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition mb-8 ${
            isDragActive
              ? "border-primary bg-primary/5"
              : "border-border hover:border-primary/50 hover:bg-accent/30"
          }`}
        >
          <input {...getInputProps()} />
          <div className="text-4xl mb-3">{uploading ? "⏳" : isDragActive ? "📂" : "📄"}</div>
          {uploading ? (
            <p className="text-sm font-medium">Enviando documentos...</p>
          ) : isDragActive ? (
            <p className="text-sm font-medium">Solte os arquivos aqui</p>
          ) : (
            <>
              <p className="text-sm font-medium mb-1">Arraste documentos ou clique para selecionar</p>
              <p className="text-xs text-muted-foreground">PDF, JPG, PNG · Máximo 10MB por arquivo</p>
              <p className="text-xs text-muted-foreground mt-2">
                Informes de rendimento, recibos médicos, despesas escolares, extratos
              </p>
            </>
          )}
        </div>

        {/* Lista de documentos */}
        {docs.length > 0 && (
          <div>
            <h2 className="font-semibold mb-4">Documentos enviados ({docs.length})</h2>
            <div className="space-y-3">
              {docs.map((doc) => {
                const s = STATUS_LABELS[doc.status] || { label: doc.status, color: "text-muted-foreground" };
                return (
                  <div key={doc.id} className="bg-card border border-border rounded-xl px-5 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">
                        {doc.mime_type === "application/pdf" ? "📄" : "🖼️"}
                      </span>
                      <div>
                        <p className="text-sm font-medium truncate max-w-xs">{doc.nome_original}</p>
                        <p className="text-xs text-muted-foreground">
                          {doc.tipo !== "outros" ? doc.tipo.replace(/_/g, " ") : "Classificando..."} ·{" "}
                          {new Date(doc.created_at).toLocaleDateString("pt-BR")}
                        </p>
                      </div>
                    </div>
                    <span className={`text-xs font-medium ${s.color}`}>{s.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {docs.length === 0 && (
          <p className="text-center text-muted-foreground text-sm">Nenhum documento enviado ainda</p>
        )}
      </main>
    </div>
  );
}
