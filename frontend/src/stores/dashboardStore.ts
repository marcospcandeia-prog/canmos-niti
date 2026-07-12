import { create } from 'zustand'
import { api } from '@/lib/api'
import type { DashboardSummary } from '@/types'

interface DashboardState {
  summary: DashboardSummary | null
  loading: boolean
  selectedYear: number
  loadSummary: (year?: number) => Promise<void>
  setSelectedYear: (year: number) => void
}

const CURRENT_YEAR = new Date().getFullYear()

export const useDashboardStore = create<DashboardState>((set, get) => ({
  summary: null,
  loading: false,
  selectedYear: CURRENT_YEAR,

  loadSummary: async (year?: number) => {
    const anoBase = year ?? get().selectedYear
    set({ loading: true })
    try {
      const res = await api.get(`/dashboard/summary?ano_base=${anoBase}`)
      set({ summary: res.data })
    } catch {
    } finally {
      set({ loading: false })
    }
  },

  setSelectedYear: (year: number) => {
    set({ selectedYear: year })
    get().loadSummary(year)
  },
}))
