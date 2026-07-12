import type { Metadata } from 'next'
import './globals.css'
import { AuthProvider } from '@/components/AuthProvider'
import { ToastProvider } from '@/components/Toast'

export const metadata: Metadata = {
  title: 'CANMOS-NITI - Sistema Tributário Inteligente',
  description: 'Núcleo de Infraestrutura Tributária Inteligente',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>
        <AuthProvider>
          <ToastProvider>
            {children}
          </ToastProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
