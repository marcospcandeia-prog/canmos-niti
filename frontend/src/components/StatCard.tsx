interface StatCardProps {
  title: string
  value: string | number
  color?: 'blue' | 'green' | 'red' | 'purple' | 'yellow' | 'gray'
  subtitle?: string
}

const colorMap = {
  blue: { text: 'text-blue-600', bg: 'bg-blue-50' },
  green: { text: 'text-green-600', bg: 'bg-green-50' },
  red: { text: 'text-red-600', bg: 'bg-red-50' },
  purple: { text: 'text-purple-600', bg: 'bg-purple-50' },
  yellow: { text: 'text-yellow-600', bg: 'bg-yellow-50' },
  gray: { text: 'text-gray-900', bg: 'bg-gray-50' },
}

export function StatCard({ title, value, color = 'blue', subtitle }: StatCardProps) {
  const colors = colorMap[color]
  return (
    <div className={`rounded-lg ${colors.bg} p-6 shadow-sm`}>
      <p className="text-sm font-medium text-gray-600">{title}</p>
      <p className={`mt-2 text-3xl font-bold ${colors.text}`}>{value}</p>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </div>
  )
}
