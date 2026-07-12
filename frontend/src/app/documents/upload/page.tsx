'use client';

import { useState, useRef, useEffect } from 'react';
import api from '@/lib/api';
import { Badge } from '@/components/Badge';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { DocumentDetailModal } from '@/components/DocumentDetailModal';
import { getDocumentTypeLabel } from '@/lib/documentTypes';
import { useToast } from '@/components/Toast';
import { useDocumentStore } from '@/stores/documentStore';

const ALLOWED_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/jpg',
  'image/png',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
];

const MAX_FILE_SIZE = 10 * 1024 * 1024;

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  });
}

function statusBadgeVariant(status: string) {
  const map: Record<string, 'default' | 'success' | 'warning' | 'error' | 'info'> = {
    uploaded: 'warning',
    processing: 'info',
    processed: 'success',
    error: 'error',
  };
  return map[status] || 'default';
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    uploaded: 'Pendente',
    processing: 'Processando',
    processed: 'Processado',
    error: 'Erro',
  };
  return map[status] || status;
}

export default function UploadPage() {
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [detailDocId, setDetailDocId] = useState<number | null>(null);

  const {
    documents,
    uploadingFiles,
    stats,
    loading,
    loadDocuments,
    loadStats,
    uploadFile,
    deleteDocument,
    processOcr,
    init,
  } = useDocumentStore();

  useEffect(() => {
    init();
  }, [init]);

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'Tipo de arquivo não permitido. Use PDF, imagens (JPG, PNG) ou documentos Word.';
    }
    if (file.size > MAX_FILE_SIZE) {
      return `Arquivo muito grande. Tamanho máximo: ${formatBytes(MAX_FILE_SIZE)}`;
    }
    return null;
  };

  const handleUpload = async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      toast(validationError, 'error');
      return;
    }

    const docId = await uploadFile(file);
    if (docId) {
      toast(`${file.name} enviado com sucesso!`, 'success');
    } else {
      toast(`Erro ao enviar ${file.name}`, 'error');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    Array.from(e.dataTransfer.files).forEach(file => handleUpload(file));
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    Array.from(e.target.files || []).forEach(file => handleUpload(file));
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDelete = async (documentId: string) => {
    if (!confirm('Tem certeza que deseja excluir este documento?')) return;
    try {
      await deleteDocument(documentId);
      toast('Documento excluído', 'success');
    } catch (err: any) {
      toast(err.response?.data?.detail || 'Erro ao excluir documento', 'error');
    }
  };

  const handleDownload = async (documentId: string, filename: string) => {
    try {
      const response = await api.get(`/documents/${documentId}/download`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      toast(err.response?.data?.detail || 'Erro ao baixar documento', 'error');
    }
  };

  const handleProcessOcr = async (documentId: string) => {
    try {
      await processOcr(documentId);
      toast('Processamento OCR iniciado', 'success');
    } catch (err: any) {
      toast(err.response?.data?.detail || 'Erro ao iniciar processamento OCR', 'error');
    }
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Upload de Documentos</h1>
          <p className="mt-1 text-sm text-gray-600">
            Envie seus documentos fiscais para processamento automático
          </p>
        </div>
        <div className="flex items-center space-x-6 text-sm">
          <div>
            <span className="text-gray-600">Total:</span>{' '}
            <span className="font-semibold text-gray-900">{stats.total}</span>
          </div>
          <div>
            <span className="text-gray-600">Processados:</span>{' '}
            <span className="font-semibold text-green-600">{stats.processados}</span>
          </div>
          <div>
            <span className="text-gray-600">Pendentes:</span>{' '}
            <span className="font-semibold text-yellow-600">{stats.pendentes}</span>
          </div>
        </div>
      </div>

      <div className="mb-8">
        <div
          onDrop={handleDrop}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={(e) => { e.preventDefault(); setIsDragging(false); }}
          className={`border-2 border-dashed rounded-lg p-12 text-center transition ${
            isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white hover:border-gray-400'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            onChange={handleFileSelect}
            className="hidden"
          />
          <div className="space-y-4">
            <svg className={`w-16 h-16 mx-auto ${isDragging ? 'text-blue-500' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-lg font-medium text-gray-700">
              {isDragging ? 'Solte os arquivos aqui' : 'Arraste arquivos aqui'}
            </p>
            <p className="text-sm text-gray-500">ou</p>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
            >
              Selecionar Arquivos
            </button>
            <p className="text-xs text-gray-500">
              PDF, JPG, PNG, DOC, DOCX • Máximo {formatBytes(MAX_FILE_SIZE)} por arquivo
            </p>
          </div>
        </div>
      </div>

      {uploadingFiles.length > 0 && (
        <div className="mb-8 space-y-3">
          <h2 className="text-lg font-semibold text-gray-900">Fazendo upload...</h2>
          {uploadingFiles.map((uf, index) => (
            <div key={index} className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    {uf.status === 'uploading' && (
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
                    )}
                    {uf.status === 'success' && (
                      <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    )}
                    {uf.status === 'error' && (
                      <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{uf.file.name}</p>
                    <p className="text-xs text-gray-500">{formatBytes(uf.file.size)}</p>
                  </div>
                </div>
                <div className="text-sm font-medium text-gray-700">{uf.progress}%</div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    uf.status === 'success' ? 'bg-green-600' : uf.status === 'error' ? 'bg-red-600' : 'bg-blue-600'
                  }`}
                  style={{ width: `${uf.progress}%` }}
                />
              </div>
              {uf.error && <p className="mt-2 text-sm text-red-600">{uf.error}</p>}
              {uf.status === 'success' && <p className="mt-2 text-sm text-green-600">Upload concluído com sucesso!</p>}
            </div>
          ))}
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Meus Documentos</h2>
        {loading ? (
          <LoadingSpinner message="Carregando documentos..." />
        ) : documents.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="mt-4 text-gray-600">Nenhum documento enviado ainda.</p>
            <p className="text-sm text-gray-500">Faça upload do seu primeiro documento acima.</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Documento</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo MIME</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ações</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{doc.nome_original}</div>
                      <div className="text-xs text-gray-500">{doc.mime_type}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{getDocumentTypeLabel(doc.tipo)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{doc.mime_type}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge label={statusLabel(doc.status)} variant={statusBadgeVariant(doc.status)} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{formatDate(doc.created_at)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                      <button onClick={() => setDetailDocId(Number(doc.id))} className="text-blue-600 hover:text-blue-900">
                        Detalhes
                      </button>
                      <button onClick={() => handleProcessOcr(doc.id)} className="text-purple-600 hover:text-purple-900">
                        OCR
                      </button>
                      <button onClick={() => handleDownload(doc.id, doc.nome_original)} className="text-blue-600 hover:text-blue-900">
                        Download
                      </button>
                      <button onClick={() => handleDelete(doc.id)} className="text-red-600 hover:text-red-900">
                        Excluir
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <DocumentDetailModal documentId={detailDocId} onClose={() => setDetailDocId(null)} />
    </div>
  );
}
