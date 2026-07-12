'use client'

import { useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import { Sidebar } from './Sidebar'
import { LoadingSpinner } from './LoadingSpinner'

const authPages = ['/auth/login', '/auth/register', '/', '/privacidade', '/termos']

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { user, loading, loadUser } = useAuthStore()

  useEffect(() => {
    loadUser()
  }, [loadUser])

  const isAuthPage = authPages.some((p) => pathname === p || pathname.startsWith(p + '/'))

  if (loading) {
    return <LoadingSpinner message="Inicializando..." />
  }

  if (isAuthPage || !user) {
    return <>{children}</>
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 lg:ml-64 pt-14 lg:pt-0">{children}</main>
    </div>
  )
}
