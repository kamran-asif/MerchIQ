import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: value < 1 ? 2 : 0,
    maximumFractionDigits: 2,
  }).format(value)
}

export function formatNumber(value: number, decimals = 0): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export function formatPercent(value: number, signed = true): string {
  const formatted = `${value.toFixed(1)}%`
  return signed && value > 0 ? `+${formatted}` : formatted
}

export function getGrowthColor(value: number): string {
  if (value > 5) return 'text-green-600'
  if (value < -5) return 'text-red-600'
  return 'text-gray-600'
}

export function getRiskBadgeColor(risk: string): string {
  switch (risk.toLowerCase()) {
    case 'critical':
    case 'high':
      return 'bg-red-100 text-red-800'
    case 'medium':
      return 'bg-yellow-100 text-yellow-800'
    case 'overstocked':
      return 'bg-purple-100 text-purple-800'
    case 'low':
    default:
      return 'bg-green-100 text-green-800'
  }
}

export function mockKPIs() {
  return {
    total_revenue: 1247832.56,
    revenue_growth: 8.4,
    total_units_sold: 48216,
    units_growth: 5.2,
    gross_margin: 38.7,
    margin_growth: 1.2,
    avg_order_value: 68.42,
    inventory_turnover: 5.4,
    stockout_rate: 2.8,
    promotion_roi: 187.5,
  }
}
