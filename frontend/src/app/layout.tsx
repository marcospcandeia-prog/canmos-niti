import type { Metadata } from 'next'
import './globals.css'

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
      <body>{children}</body>
    </html>
  )
}
