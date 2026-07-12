import { create } from 'zustand'
import { api } from '@/lib/api'
import type { UserProfile } from '@/types'

interface AuthState {
  user: UserProfile | null
  loading: boolean
  setUser: (user: UserProfile | null) => void
  loadUser: () => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: true,
  setUser: (user) => set({ user }),
  loadUser: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ user: null, loading: false })
      return
    }
    try {
      const response = await api.get('/users/me')
      set({ user: response.data, loading: false })
    } catch {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, loading: false })
    }
  },
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null })
    window.location.href = '/auth/login'
  },
}))
