'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';

interface Declaration {
  id: number;
  ano_base: number;
  status: string;
  restituicao_estimada: number;
  imposto_devido: number;
  created_at?: string;
  updated_at?: string;
  // calculation fields (from /tax/calculate)
  total_rendimentos?: number;
  total_deducoes?: number;
  base_calculo?: number;
  total_retencao?: number;
  imposto_pagar?: number;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
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

function getStatusBadge(status: string) {
  const badges: Record<string, { bg: string; text: string; label: string }> = {
    draft: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Rascunho' },
    pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Pendente' },
    submitted: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Enviada' },
    validated: { bg: 'bg-green-100', text: 'text-green-800', label: 'Validada' },
    error: { bg: 'bg-red-100', text: 'text-red-800', label: 'Erro' },
  };

  const badge = badges[status] || badges.draft;
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
      {badge.label}
    </span>
  );
}

function getTypeBadge(tipo: string) {
  const badges: Record<string, { bg: string; text: string }> = {
    completa: { bg: 'bg-blue-50', text: 'text-blue-700' },
    simplificada: { bg: 'bg-green-50', text: 'text-green-700' },
  };

  const badge = badges[tipo] || badges.completa;
  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${badge.bg} ${badge.text}`}>
      {tipo.charAt(0).toUpperCase() + tipo.slice(1)}
    </span>
  );
}

export default function DeclarationsPage() {
  const router = useRouter();
  const [declarations, setDeclarations] = useState<Declaration[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState<number>(2025);
  const [selectedDeclaration, setSelectedDeclaration] = useState<Declaration | null>(null);
  const [creatingNew, setCreatingNew] = useState(false);

  useEffect(() => {
    loadDeclarations();
  }, [selectedYear]);

  const loadDeclarations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/tax/declarations');
      setDeclarations(response.data);
    } catch (err: any) {
      console.error('Erro ao carregar declarações:', err);
      if (err.response?.status === 401) {
        router.push('/auth/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDeclaration = async () => {
    setCreatingNew(true);
    try {
      const response = await api.post(`/tax/declaration/${selectedYear}`);
      setSelectedDeclaration(response.data);
      loadDeclarations();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao criar declaração');
    } finally {
      setCreatingNew(false);
    }
  };

  const handleCalculate = async () => {
    try {
      const response = await api.post(`/tax/calculate/${selectedYear}`);
      const data = response.data;
      setSelectedDeclaration({
        id: 0,
        ano_base: selectedYear,
        status: 'draft',
        restituicao_estimada: data.restituicao_estimada,
        imposto_devido: data.imposto_devido,
        total_rendimentos: data.total_rendimentos,
        total_deducoes: data.total_deducoes,
        base_calculo: data.base_calculo,
        total_retencao: data.total_retencao,
        imposto_pagar: data.imposto_pagar,
      });
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao calcular impostos');
    }
  };

  const years = [2025, 2024, 2023, 2022];

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
                Declarações de IRPF
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(Number(e.target.value))}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {years.map(year => (
                  <option key={year} value={year}>
                    Ano-base: {year}
                  </option>
                ))}
              </select>
              <button
                onClick={handleCalculate}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
              >
                Calcular Impostos
              </button>
              <button
                onClick={handleCreateDeclaration}
                disabled={creatingNew}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:bg-gray-400"
              >
                {creatingNew ? 'Criando...' : 'Nova Declaração'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Info Card */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-blue-900">Como funciona</h3>
              <p className="mt-1 text-sm text-blue-700">
                1. Envie seus documentos fiscais na seção de upload
                <br />
                2. Aguarde o processamento automático (OCR + IA)
                <br />
                3. Clique em "Calcular Impostos" para simular
                <br />
                4. Crie uma declaração quando estiver pronto
                <br />
                5. Revise os dados antes de enviar à Receita Federal
              </p>
            </div>
          </div>
        </div>

        {/* Selected Declaration Details */}
        {selectedDeclaration && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  Declaração IRPF {selectedDeclaration.ano_base}
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  Criada em {formatDate(selectedDeclaration.created_at || '')}
                </p>
              </div>
              <div className="flex items-center space-x-3">
                {getStatusBadge(selectedDeclaration.status)}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-xs font-medium text-blue-600 uppercase tracking-wide">
                  Rendimentos Tributáveis
                </p>
                <p className="mt-2 text-2xl font-bold text-blue-900">
                  {formatCurrency(selectedDeclaration.total_rendimentos ?? 0)}
                </p>
              </div>

              <div className="bg-purple-50 rounded-lg p-4">
                <p className="text-xs font-medium text-purple-600 uppercase tracking-wide">
                  Deduções
                </p>
                <p className="mt-2 text-2xl font-bold text-purple-900">
                  {formatCurrency(selectedDeclaration.total_deducoes ?? 0)}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                  Base de Cálculo
                </p>
                <p className="mt-2 text-2xl font-bold text-gray-900">
                  {formatCurrency(selectedDeclaration.base_calculo ?? 0)}
                </p>
              </div>

              <div className="bg-red-50 rounded-lg p-4">
                <p className="text-xs font-medium text-red-600 uppercase tracking-wide">
                  Imposto Devido
                </p>
                <p className="mt-2 text-2xl font-bold text-red-900">
                  {formatCurrency(selectedDeclaration.imposto_devido)}
                </p>
              </div>

              <div className="bg-yellow-50 rounded-lg p-4">
                <p className="text-xs font-medium text-yellow-600 uppercase tracking-wide">
                  Imposto Retido
                </p>
                <p className="mt-2 text-2xl font-bold text-yellow-900">
                  {formatCurrency(selectedDeclaration.total_retencao ?? 0)}
                </p>
              </div>

              <div className={`rounded-lg p-4 ${(selectedDeclaration.restituicao_estimada ?? 0) > 0 ? 'bg-green-50' : 'bg-red-50'}`}>
                <p className={`text-xs font-medium uppercase tracking-wide ${(selectedDeclaration.restituicao_estimada ?? 0) > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {(selectedDeclaration.restituicao_estimada ?? 0) > 0 ? 'A Restituir' : 'A Pagar'}
                </p>
                <p className={`mt-2 text-2xl font-bold ${(selectedDeclaration.restituicao_estimada ?? 0) > 0 ? 'text-green-900' : 'text-red-900'}`}>
                  {formatCurrency(Math.abs(selectedDeclaration.restituicao_estimada ?? selectedDeclaration.imposto_pagar ?? 0))}
                </p>
              </div>
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => setSelectedDeclaration(null)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
              >
                Fechar
              </button>
              <button
                onClick={() => alert('Download em desenvolvimento')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Download PDF
              </button>
              <button
                onClick={() => alert('Envio em desenvolvimento')}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              >
                Enviar à Receita
              </button>
            </div>
          </div>
        )}

        {/* Declarations List */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Histórico de Declarações
          </h2>

          {loading ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Carregando declarações...</p>
            </div>
          ) : declarations.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <svg
                className="mx-auto h-16 w-16 text-gray-400"
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
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                Nenhuma declaração encontrada
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Você ainda não criou declarações para {selectedYear}.
              </p>
              <div className="mt-6">
                <button
                  onClick={handleCreateDeclaration}
                  disabled={creatingNew}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:bg-gray-400"
                >
                  {creatingNew ? 'Criando...' : 'Criar Primeira Declaração'}
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ano
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Resultado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Criada Em
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {declarations.map((declaration) => (
                    <tr key={declaration.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {declaration.ano_base}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(declaration.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {declaration.restituicao_estimada > 0 ? (
                          <span className="text-green-600 font-semibold">
                            Restituir {formatCurrency(declaration.restituicao_estimada)}
                          </span>
                        ) : declaration.imposto_devido > 0 ? (
                          <span className="text-red-600 font-semibold">
                            Pagar {formatCurrency(declaration.imposto_devido)}
                          </span>
                        ) : (
                          <span className="text-gray-600">Zerada</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatDate(declaration.created_at || '')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                        <button
                          onClick={() => setSelectedDeclaration(declaration)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Ver Detalhes
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
