'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { StatCard } from '@/components/StatCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { useDashboardStore } from '@/stores/dashboardStore'

const CURRENT_YEAR = new Date().getFullYear()
const AVAILABLE_YEARS = Array.from({ length: 5 }, (_, i) => CURRENT_YEAR - i)

export default function DashboardPage() {
  const { summary, loading, selectedYear, loadSummary, setSelectedYear } = useDashboardStore()

  useEffect(() => {
    loadSummary()
  }, [])

  if (loading) return <LoadingSpinner />
  if (!summary) return null

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">Visão geral do ano selecionado</p>
        </div>
        <select
          value={selectedYear}
          onChange={(e) => setSelectedYear(Number(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white"
        >
          {AVAILABLE_YEARS.map(year => (
            <option key={year} value={year}>Ano-base: {year}</option>
          ))}
        </select>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Restituição Estimada"
          value={`R$ ${summary.restituicao_estimada.toFixed(2)}`}
          color="green"
        />
        <StatCard
          title="Imposto Devido"
          value={`R$ ${summary.imposto_devido.toFixed(2)}`}
          color="red"
        />
        <StatCard
          title="Total Rendimentos"
          value={`R$ ${summary.total_rendimentos.toFixed(2)}`}
          color="blue"
        />
        <StatCard
          title="Documentos"
          value={`${summary.documentos_processados} / ${summary.documentos_enviados}`}
          color="gray"
          subtitle="Processados"
        />
      </div>

      {summary.alertas && summary.alertas.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Alertas</h2>
          <div className="space-y-3">
            {summary.alertas.map((alerta, index) => (
              <div
                key={index}
                className={`rounded-lg p-4 ${
                  alerta.severidade === 'warning'
                    ? 'bg-yellow-50 border border-yellow-200'
                    : 'bg-blue-50 border border-blue-200'
                }`}
              >
                <p className="text-sm">{alerta.mensagem}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <Link
          href="/documents/upload"
          className="block rounded-lg bg-blue-600 px-6 py-4 text-center text-white hover:bg-blue-700 transition"
        >
          <p className="font-semibold">Enviar Documentos</p>
          <p className="text-sm opacity-90">Upload de PDFs e imagens</p>
        </Link>
        <Link
          href="/declarations"
          className="block rounded-lg bg-green-600 px-6 py-4 text-center text-white hover:bg-green-700 transition"
        >
          <p className="font-semibold">Declarações IRPF</p>
          <p className="text-sm opacity-90">Ver e criar declarações</p>
        </Link>
        <Link
          href="/chat"
          className="block rounded-lg bg-purple-600 px-6 py-4 text-center text-white hover:bg-purple-700 transition"
        >
          <p className="font-semibold">Assistente IA</p>
          <p className="text-sm opacity-90">Tire suas dúvidas</p>
        </Link>
      </div>
    </div>
  )
}
