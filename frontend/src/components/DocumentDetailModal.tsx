'use client'

import { useEffect, useState } from 'react'
import api from '@/lib/api'
import { Badge } from './Badge'
import { LoadingSpinner } from './LoadingSpinner'
import { getDocumentTypeLabel } from '@/lib/documentTypes'

interface DocumentDetail {
  id: number
  nome_original: string
  tipo: string | null
  mime_type: string
  hash_arquivo: string
  status: string
  created_at: string
  updated_at: string
  ocr_texto: string | null
  ocr_confianca: number | null
  ocr_engine: string | null
  ocr_status: string | null
}

interface Props {
  documentId: number | null
  onClose: () => void
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

function statusVariant(status: string) {
  const map: Record<string, 'default' | 'success' | 'warning' | 'error' | 'info'> = {
    uploaded: 'warning', processing: 'info', processed: 'success', error: 'error',
  }
  return map[status] || 'default'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    uploaded: 'Pendente', processing: 'Processando', processed: 'Processado', error: 'Erro',
  }
  return map[status] || status
}

export function DocumentDetailModal({ documentId, onClose }: Props) {
  const [doc, setDoc] = useState<DocumentDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [ocrLoading, setOcrLoading] = useState(false)

  useEffect(() => {
    if (documentId) load()
  }, [documentId])

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.get(`/documents/${documentId}`)
      setDoc(res.data)
    } catch { /* ignore */ }
    finally { setLoading(false) }
  }

  const handleTriggerOcr = async () => {
    setOcrLoading(true)
    try {
      await api.post(`/ocr/process/${documentId}`)
      setTimeout(load, 1000)
    } catch { /* ignore */ }
    finally { setOcrLoading(false) }
  }

  if (!documentId) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full mx-4 max-h-[85vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        {loading ? (
          <div className="p-12"><LoadingSpinner message="Carregando detalhes..." /></div>
        ) : doc ? (
          <div className="p-6">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{doc.nome_original}</h2>
                <p className="text-sm text-gray-500 mt-1">{doc.mime_type}</p>
              </div>
              <div className="flex items-center space-x-3">
                <Badge label={statusLabel(doc.status)} variant={statusVariant(doc.status)} />
                <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <InfoRow label="Tipo" value={getDocumentTypeLabel(doc.tipo)} />
              <InfoRow label="Hash" value={doc.hash_arquivo.substring(0, 20) + '...'} />
              <InfoRow label="Criado em" value={formatDate(doc.created_at)} />
              <InfoRow label="Atualizado em" value={formatDate(doc.updated_at)} />
            </div>

            <div className="border-t pt-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Resultado OCR</h3>
                {doc.status === 'uploaded' && (
                  <button
                    onClick={handleTriggerOcr}
                    disabled={ocrLoading}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm font-medium disabled:bg-gray-400"
                  >
                    {ocrLoading ? 'Processando...' : 'Processar OCR'}
                  </button>
                )}
              </div>

              {doc.ocr_texto ? (
                <div className="space-y-3">
                  <div className="flex space-x-4 text-sm">
                    <span className="text-gray-600">Confiança: <strong>{doc.ocr_confianca ? (doc.ocr_confianca * 100).toFixed(0) : '-'}%</strong></span>
                    <span className="text-gray-600">Engine: <strong>{doc.ocr_engine || '-'}</strong></span>
                    <Badge label={doc.ocr_status || '-'} variant={doc.ocr_status === 'success' ? 'success' : 'error'} />
                  </div>
                  <pre className="bg-gray-50 border rounded-lg p-4 text-sm text-gray-700 whitespace-pre-wrap max-h-60 overflow-y-auto font-mono leading-relaxed">
                    {doc.ocr_texto}
                  </pre>
                </div>
              ) : (
                <div className="bg-gray-50 border rounded-lg p-8 text-center">
                  <svg className="mx-auto h-10 w-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="mt-3 text-gray-600">Documento ainda não processado</p>
                  <p className="text-sm text-gray-500">Clique em &quot;Processar OCR&quot; para extrair o texto</p>
                </div>
              )}
            </div>

            <div className="border-t pt-6 mt-6 flex justify-end">
              <button onClick={onClose} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition">
                Fechar
              </button>
            </div>
          </div>
        ) : (
          <div className="p-12 text-center text-gray-600">Documento não encontrado</div>
        )}
      </div>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium text-gray-500 uppercase">{label}</p>
      <p className="text-sm text-gray-900 mt-1">{value}</p>
    </div>
  )
}
