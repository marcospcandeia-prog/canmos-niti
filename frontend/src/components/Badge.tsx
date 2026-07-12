type BadgeVariant = 'default' | 'success' | 'warning' | 'error' | 'info'

interface BadgeProps {
  label: string
  variant?: BadgeVariant
}

const variantMap: Record<BadgeVariant, { bg: string; text: string }> = {
  default: { bg: 'bg-gray-100', text: 'text-gray-800' },
  success: { bg: 'bg-green-100', text: 'text-green-800' },
  warning: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
  error: { bg: 'bg-red-100', text: 'text-red-800' },
  info: { bg: 'bg-blue-100', text: 'text-blue-800' },
}

export function Badge({ label, variant = 'default' }: BadgeProps) {
  const v = variantMap[variant]
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${v.bg} ${v.text}`}>
      {label}
    </span>
  )
}
