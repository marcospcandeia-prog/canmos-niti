'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';

interface Document {
  id: string;
  nome_arquivo: string;
  tipo_documento: string;
  tamanho: number;
  hash_arquivo: string;
  status_processamento: string;
  created_at: string;
}

interface UploadingFile {
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  error?: string;
  documentId?: string;
}

const ALLOWED_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/jpg',
  'image/png',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

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
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [stats, setStats] = useState({ total: 0, processados: 0, pendentes: 0 });

  useEffect(() => {
    loadDocuments();
    loadStats();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await api.get('/documents');
      setDocuments(response.data);
    } catch (err: any) {
      console.error('Erro ao carregar documentos:', err);
      if (err.response?.status === 401) {
        router.push('/auth/login');
      }
    } finally {
      setLoadingDocuments(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/documents/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Erro ao carregar estatísticas:', err);
    }
  };

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'Tipo de arquivo não permitido. Use PDF, imagens (JPG, PNG) ou documentos Word.';
    }
    if (file.size > MAX_FILE_SIZE) {
      return `Arquivo muito grande. Tamanho máximo: ${formatBytes(MAX_FILE_SIZE)}`;
    }
    return null;
  };

  const uploadFile = async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setUploadingFiles(prev => [
        ...prev,
        { file, progress: 0, status: 'error', error: validationError }
      ]);
      return;
    }

    // Adiciona arquivo à lista de upload
    const uploadingFile: UploadingFile = {
      file,
      progress: 0,
      status: 'uploading',
    };
    setUploadingFiles(prev => [...prev, uploadingFile]);
    const fileIndex = uploadingFiles.length;

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          
          setUploadingFiles(prev =>
            prev.map((f, i) =>
              i === fileIndex ? { ...f, progress } : f
            )
          );
        },
      });

      // Sucesso
      setUploadingFiles(prev =>
        prev.map((f, i) =>
          i === fileIndex
            ? { ...f, status: 'success', progress: 100, documentId: response.data.id }
            : f
        )
      );

      // Recarrega lista de documentos
      loadDocuments();
      loadStats();

      // Remove da lista após 3 segundos
      setTimeout(() => {
        setUploadingFiles(prev => prev.filter((_, i) => i !== fileIndex));
      }, 3000);
    } catch (err: any) {
      setUploadingFiles(prev =>
        prev.map((f, i) =>
          i === fileIndex
            ? {
                ...f,
                status: 'error',
                error: err.response?.data?.detail || 'Erro ao fazer upload',
              }
            : f
        )
      );
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    files.forEach(file => uploadFile(file));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    files.forEach(file => uploadFile(file));
    // Reseta o input para permitir upload do mesmo arquivo novamente
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!confirm('Tem certeza que deseja excluir este documento?')) {
      return;
    }

    try {
      await api.delete(`/documents/${documentId}`);
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
      loadStats();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao excluir documento');
    }
  };

  const handleDownload = async (documentId: string, filename: string) => {
    try {
      const response = await api.get(`/documents/${documentId}/download`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao baixar documento');
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { bg: string; text: string; label: string }> = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Pendente' },
      processing: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Processando' },
      completed: { bg: 'bg-green-100', text: 'text-green-800', label: 'Processado' },
      failed: { bg: 'bg-red-100', text: 'text-red-800', label: 'Erro' },
    };

    const badge = badges[status] || badges.pending;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
        {badge.label}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">
                ← Dashboard
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">
                Upload de Documentos
              </h1>
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
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Area */}
        <div className="mb-8">
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`border-2 border-dashed rounded-lg p-12 text-center transition ${
              isDragging
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 bg-white hover:border-gray-400'
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
              <div className="flex justify-center">
                <svg
                  className={`w-16 h-16 ${isDragging ? 'text-blue-500' : 'text-gray-400'}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>

              <div>
                <p className="text-lg font-medium text-gray-700">
                  {isDragging ? 'Solte os arquivos aqui' : 'Arraste arquivos aqui'}
                </p>
                <p className="text-sm text-gray-500 mt-1">ou</p>
              </div>

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

        {/* Uploading Files */}
        {uploadingFiles.length > 0 && (
          <div className="mb-8 space-y-3">
            <h2 className="text-lg font-semibold text-gray-900">Fazendo upload...</h2>
            {uploadingFiles.map((uploadingFile, index) => (
              <div key={index} className="bg-white rounded-lg shadow p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      {uploadingFile.status === 'uploading' && (
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                      )}
                      {uploadingFile.status === 'success' && (
                        <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                      {uploadingFile.status === 'error' && (
                        <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {uploadingFile.file.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatBytes(uploadingFile.file.size)}
                      </p>
                    </div>
                  </div>
                  <div className="text-sm font-medium text-gray-700">
                    {uploadingFile.progress}%
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      uploadingFile.status === 'success'
                        ? 'bg-green-600'
                        : uploadingFile.status === 'error'
                        ? 'bg-red-600'
                        : 'bg-blue-600'
                    }`}
                    style={{ width: `${uploadingFile.progress}%` }}
                  />
                </div>

                {/* Error Message */}
                {uploadingFile.error && (
                  <p className="mt-2 text-sm text-red-600">{uploadingFile.error}</p>
                )}

                {/* Success Message */}
                {uploadingFile.status === 'success' && (
                  <p className="mt-2 text-sm text-green-600">Upload concluído com sucesso!</p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Documents List */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Meus Documentos</h2>

          {loadingDocuments ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Carregando documentos...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p className="mt-4 text-gray-600">Nenhum documento enviado ainda.</p>
              <p className="text-sm text-gray-500">Faça upload do seu primeiro documento acima.</p>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Documento
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tipo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tamanho
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Data
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{doc.nome_arquivo}</div>
                        <div className="text-xs text-gray-500">{doc.hash_arquivo.substring(0, 16)}...</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">{doc.tipo_documento || 'N/A'}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatBytes(doc.tamanho)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(doc.status_processamento)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatDate(doc.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                        <button
                          onClick={() => handleDownload(doc.id, doc.nome_arquivo)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Download
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="text-red-600 hover:text-red-900"
                        >
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
      </div>
    </div>
  );
}
