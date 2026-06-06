'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'

interface DashboardSummary {
  ano_base: number
  restituicao_estimada: number
  imposto_devido: number
  total_rendimentos: number
  documentos_enviados: number
  documentos_processados: number
  total_tax_events: number
  alertas: Array<{ severidade: string; mensagem: string }>
}

export default function DashboardPage() {
  const router = useRouter()
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/auth/login')
      return
    }

    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [summaryRes, userRes] = await Promise.all([
        api.get('/dashboard/summary?ano_base=2025'),
        api.get('/users/me'),
      ])

      setSummary(summaryRes.data)
      setUser(userRes.data)
    } catch (error) {
      console.error('Erro ao carregar dados:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/auth/login')
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Carregando...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">CANMOS-NITI</h1>
            <div className="flex items-center space-x-4">
              <a
                href="/profile"
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                {user?.nome}
              </a>
              <button
                onClick={handleLogout}
                className="rounded-md bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700"
              >
                Sair
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="mt-1 text-sm text-gray-600">
            Ano base: {summary?.ano_base}
          </p>
        </div>

        {/* Cards de Métricas */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg bg-white p-6 shadow">
            <p className="text-sm font-medium text-gray-600">Restituição Estimada</p>
            <p className="mt-2 text-3xl font-bold text-green-600">
              R$ {summary?.restituicao_estimada.toFixed(2)}
            </p>
          </div>

          <div className="rounded-lg bg-white p-6 shadow">
            <p className="text-sm font-medium text-gray-600">Imposto Devido</p>
            <p className="mt-2 text-3xl font-bold text-red-600">
              R$ {summary?.imposto_devido.toFixed(2)}
            </p>
          </div>

          <div className="rounded-lg bg-white p-6 shadow">
            <p className="text-sm font-medium text-gray-600">Total Rendimentos</p>
            <p className="mt-2 text-3xl font-bold text-blue-600">
              R$ {summary?.total_rendimentos.toFixed(2)}
            </p>
          </div>

          <div className="rounded-lg bg-white p-6 shadow">
            <p className="text-sm font-medium text-gray-600">Documentos</p>
            <p className="mt-2 text-3xl font-bold text-gray-900">
              {summary?.documentos_processados} / {summary?.documentos_enviados}
            </p>
            <p className="text-xs text-gray-500">Processados</p>
          </div>
        </div>

        {/* Alertas */}
        {summary?.alertas && summary.alertas.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold text-gray-900">Alertas</h3>
            <div className="mt-4 space-y-3">
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

        {/* Actions */}
        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <a
            href="/documents/upload"
            className="block rounded-lg bg-blue-600 px-6 py-4 text-center text-white hover:bg-blue-700 transition"
          >
            <p className="font-semibold">Enviar Documentos</p>
            <p className="text-sm opacity-90">Upload de PDFs e imagens</p>
          </a>

          <a
            href="/declarations"
            className="block rounded-lg bg-green-600 px-6 py-4 text-center text-white hover:bg-green-700 transition"
          >
            <p className="font-semibold">Declarações IRPF</p>
            <p className="text-sm opacity-90">Ver e criar declarações</p>
          </a>

          <a
            href="/chat"
            className="block rounded-lg bg-purple-600 px-6 py-4 text-center text-white hover:bg-purple-700 transition"
          >
            <p className="font-semibold">Assistente IA</p>
            <p className="text-sm opacity-90">Tire suas duvidas</p>
          </a>
        </div>
      </main>
    </div>
  )
}
