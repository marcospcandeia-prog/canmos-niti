import { create } from 'zustand'
import { api } from '@/lib/api'
import type { Declaration } from '@/types'

interface DeclarationState {
  declarations: Declaration[]
  selectedDeclaration: Declaration | null
  loading: boolean
  loadDeclarations: () => Promise<void>
  createDeclaration: (anoBase: number) => Promise<void>
  calculate: (anoBase: number) => Promise<void>
  selectDeclaration: (dec: Declaration | null) => void
}

export const useDeclarationStore = create<DeclarationState>((set, get) => ({
  declarations: [],
  selectedDeclaration: null,
  loading: false,

  loadDeclarations: async () => {
    set({ loading: true })
    try {
      const res = await api.get('/tax/declarations')
      set({ declarations: res.data })
    } catch {
    } finally {
      set({ loading: false })
    }
  },

  createDeclaration: async (anoBase: number) => {
    const res = await api.post(`/tax/declaration/${anoBase}`)
    set({ selectedDeclaration: res.data })
    await get().loadDeclarations()
  },

  calculate: async (anoBase: number) => {
    const res = await api.post(`/tax/calculate/${anoBase}`)
    const data = res.data
    set({
      selectedDeclaration: {
        id: 0,
        ano_base: anoBase,
        status: 'draft',
        restituicao_estimada: data.restituicao_estimada,
        imposto_devido: data.imposto_devido,
        total_rendimentos: data.total_rendimentos,
        total_deducoes: data.total_deducoes,
        base_calculo: data.base_calculo,
        total_retencao: data.total_retencao,
        imposto_pagar: data.imposto_pagar,
      },
    })
  },

  selectDeclaration: (dec) => set({ selectedDeclaration: dec }),
}))
