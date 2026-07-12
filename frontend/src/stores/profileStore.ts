import { create } from 'zustand'
import { api } from '@/lib/api'
import type { UserProfile, UserStats } from '@/types'

interface ProfileState {
  profile: UserProfile | null
  stats: UserStats | null
  loading: boolean
  saving: boolean
  changingPassword: boolean
  editError: string
  editSuccess: boolean
  passwordError: string
  passwordSuccess: boolean
  loadProfile: () => Promise<void>
  loadStats: () => Promise<void>
  updateProfile: (data: Partial<UserProfile>) => Promise<boolean>
  changePassword: (senha_atual: string, nova_senha: string) => Promise<boolean>
  resetEditState: () => void
  resetPasswordState: () => void
}

export const useProfileStore = create<ProfileState>((set, get) => ({
  profile: null,
  stats: null,
  loading: false,
  saving: false,
  changingPassword: false,
  editError: '',
  editSuccess: false,
  passwordError: '',
  passwordSuccess: false,

  loadProfile: async () => {
    set({ loading: true })
    try {
      const res = await api.get('/users/me')
      // Preserve the current profile if the response carries no data,
      // so a transient empty response never blanks out the loaded profile.
      set({ profile: res.data ?? get().profile })
    } catch {
    } finally {
      set({ loading: false })
    }
  },

  loadStats: async () => {
    try {
      const res = await api.get('/users/me/stats')
      set({ stats: res.data })
    } catch {
    }
  },

  updateProfile: async (data) => {
    set({ saving: true, editError: '', editSuccess: false })
    try {
      const res = await api.put('/users/me', data)
      set({ profile: res.data, editSuccess: true, saving: false })
      return true
    } catch (err: any) {
      set({ editError: err.response?.data?.detail || 'Erro ao atualizar perfil', saving: false })
      return false
    }
  },

  changePassword: async (senha_atual, nova_senha) => {
    set({ changingPassword: true, passwordError: '', passwordSuccess: false })
    try {
      await api.post('/users/me/change-password', {
        senha_atual,
        senha_nova: nova_senha,
        senha_nova_confirmacao: nova_senha,
      })
      set({ passwordSuccess: true, changingPassword: false })
      return true
    } catch (err: any) {
      set({ passwordError: err.response?.data?.detail || 'Erro ao alterar senha', changingPassword: false })
      return false
    }
  },

  resetEditState: () => set({ editError: '', editSuccess: false }),
  resetPasswordState: () => set({ passwordError: '', passwordSuccess: false }),
}))
