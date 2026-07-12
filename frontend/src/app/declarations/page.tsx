'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { Badge } from '@/components/Badge';
import { StatCard } from '@/components/StatCard';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { useToast } from '@/components/Toast';
import { useDeclarationStore } from '@/stores/declarationStore';
import type { Declaration } from '@/types';

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  });
}

function statusBadgeVariant(status: string) {
  const map: Record<string, 'default' | 'success' | 'warning' | 'error' | 'info'> = {
    draft: 'default',
    rascunho: 'default',
    pending: 'warning',
    submitted: 'info',
    validated: 'success',
    error: 'error',
  };
  return map[status] || 'default';
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    draft: 'Rascunho',
    rascunho: 'Rascunho',
    pending: 'Pendente',
    submitted: 'Enviada',
    validated: 'Validada',
    error: 'Erro',
  };
  return map[status] || status;
}

export default function DeclarationsPage() {
  const { toast } = useToast();
  const [selectedYear, setSelectedYear] = useState<number>(2025);
  const [creatingNew, setCreatingNew] = useState(false);

  const {
    declarations,
    selectedDeclaration,
    loading,
    loadDeclarations,
    createDeclaration,
    calculate,
    selectDeclaration,
  } = useDeclarationStore();

  useEffect(() => {
    loadDeclarations();
  }, [selectedYear, loadDeclarations]);

  const handleCreateDeclaration = async () => {
    setCreatingNew(true);
    try {
      await createDeclaration(selectedYear);
      await loadDeclarations();
    } catch (err: any) {
      toast(err.response?.data?.detail || 'Erro ao criar declaração', 'error');
    } finally {
      setCreatingNew(false);
    }
  };

  const handleCalculate = async () => {
    try {
      await calculate(selectedYear);
    } catch (err: any) {
      toast(err.response?.data?.detail || 'Erro ao calcular impostos', 'error');
    }
  };

  const handleDownloadPdf = async () => {
    if (!selectedDeclaration) return;
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/tax/declaration/${selectedDeclaration.ano_base}/pdf`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) throw new Error('Erro ao gerar PDF');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `declaracao_irpf_${selectedDeclaration.ano_base}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      toast('PDF gerado com sucesso', 'success');
    } catch {
      toast('Erro ao gerar PDF da declaração', 'error');
    }
  };

  const years = [2025, 2024, 2023, 2022];

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Declarações de IRPF</h1>
          <p className="mt-1 text-sm text-gray-600">Gerencie suas declarações de Imposto de Renda</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {years.map(year => (
              <option key={year} value={year}>Ano-base: {year}</option>
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

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <h3 className="text-sm font-medium text-blue-900">Como funciona</h3>
            <p className="mt-1 text-sm text-blue-700">
              1. Envie seus documentos fiscais na seção de upload<br />
              2. Aguarde o processamento automático (OCR + IA)<br />
              3. Clique em &quot;Calcular Impostos&quot; para simular<br />
              4. Crie uma declaração quando estiver pronto<br />
              5. Revise os dados antes de enviar à Receita Federal
            </p>
          </div>
        </div>
      </div>

      {selectedDeclaration && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Declaração IRPF {selectedDeclaration.ano_base}
              </h2>
              {selectedDeclaration.created_at && (
                <p className="text-sm text-gray-500 mt-1">Criada em {formatDate(selectedDeclaration.created_at)}</p>
              )}
            </div>
            <Badge label={statusLabel(selectedDeclaration.status)} variant={statusBadgeVariant(selectedDeclaration.status)} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard title="Rendimentos Tributáveis" value={formatCurrency(selectedDeclaration.total_rendimentos ?? 0)} color="blue" />
            <StatCard title="Deduções" value={formatCurrency(selectedDeclaration.total_deducoes ?? 0)} color="purple" />
            <StatCard title="Base de Cálculo" value={formatCurrency(selectedDeclaration.base_calculo ?? 0)} color="gray" />
            <StatCard title="Imposto Devido" value={formatCurrency(selectedDeclaration.imposto_devido)} color="red" />
            <StatCard title="Imposto Retido" value={formatCurrency(selectedDeclaration.total_retencao ?? 0)} color="yellow" />
            <StatCard
              title={(selectedDeclaration.restituicao_estimada ?? 0) > 0 ? 'A Restituir' : 'A Pagar'}
              value={formatCurrency(Math.abs(selectedDeclaration.restituicao_estimada ?? selectedDeclaration.imposto_pagar ?? 0))}
              color={(selectedDeclaration.restituicao_estimada ?? 0) > 0 ? 'green' : 'red'}
            />
          </div>

          <div className="mt-6 flex justify-end space-x-3">
            <button onClick={() => selectDeclaration(null)} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition">
              Fechar
            </button>
            <button onClick={handleDownloadPdf} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
              Download PDF
            </button>
            <button onClick={() => toast('Envio em desenvolvimento', 'info')} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">
              Enviar à Receita
            </button>
          </div>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Histórico de Declarações</h2>
        {loading ? (
          <LoadingSpinner message="Carregando declarações..." />
        ) : declarations.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">Nenhuma declaração encontrada</h3>
            <p className="mt-2 text-sm text-gray-500">Você ainda não criou declarações para {selectedYear}.</p>
            <button onClick={handleCreateDeclaration} disabled={creatingNew} className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:bg-gray-400">
              {creatingNew ? 'Criando...' : 'Criar Primeira Declaração'}
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ano</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resultado</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Criada Em</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ações</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {declarations.map((declaration) => (
                  <tr key={declaration.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{declaration.ano_base}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge label={statusLabel(declaration.status)} variant={statusBadgeVariant(declaration.status)} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {declaration.restituicao_estimada > 0 ? (
                        <span className="text-green-600 font-semibold">Restituir {formatCurrency(declaration.restituicao_estimada)}</span>
                      ) : declaration.imposto_devido > 0 ? (
                        <span className="text-red-600 font-semibold">Pagar {formatCurrency(declaration.imposto_devido)}</span>
                      ) : (
                        <span className="text-gray-600">Zerada</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{formatDate(declaration.created_at || '')}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button onClick={() => selectDeclaration(declaration)} className="text-blue-600 hover:text-blue-900">
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
  );
}
