import { type ReactNode } from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { formatCurrency, formatNumber, formatPercent, getGrowthColor } from '../../utils'

interface KPICardProps {
  title: string
  value: number
  growth?: number
  prefix?: string
  suffix?: string
  format?: 'currency' | 'number' | 'percent'
  icon?: ReactNode
  accent?: 'blue' | 'green' | 'amber' | 'purple' | 'red'
}

export default function KPICard({
  title,
  value,
  growth = 0,
  prefix = '',
  suffix = '',
  format = 'number',
  icon,
  accent = 'blue',
}: KPICardProps) {
  const formatValue = () => {
    if (format === 'currency') return formatCurrency(value)
    if (format === 'percent') return `${value.toFixed(1)}%`
    return formatNumber(value, 1)
  }

  const accentMap: Record<string, string> = {
    blue: 'from-blue-50 to-blue-100 text-blue-600',
    green: 'from-green-50 to-green-100 text-green-600',
    amber: 'from-amber-50 to-amber-100 text-amber-600',
    purple: 'from-purple-50 to-purple-100 text-purple-600',
    red: 'from-red-50 to-red-100 text-red-600',
  }

  const GrowthIcon = growth > 0.5 ? TrendingUp : growth < -0.5 ? TrendingDown : Minus
  const growthColor = getGrowthColor(growth)
  const arrowColor = growth > 0.5 ? 'text-green-500' : growth < -0.5 ? 'text-red-500' : 'text-gray-400'

  return (
    <div className="card flex flex-col gap-3 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="text-sm font-medium text-gray-500">{title}</div>
        {icon && (
          <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${accentMap[accent]} flex items-center justify-center`}>
            {icon}
          </div>
        )}
      </div>
      <div className="text-2xl font-bold text-gray-900">
        {prefix}
        {formatValue()}
        {suffix}
      </div>
      <div className={`flex items-center gap-1.5 text-sm font-medium ${growthColor}`}>
        <GrowthIcon size={14} className={arrowColor} />
        <span>{formatPercent(growth)}</span>
        <span className="text-gray-400 font-normal">vs prev</span>
      </div>
    </div>
  )
}
