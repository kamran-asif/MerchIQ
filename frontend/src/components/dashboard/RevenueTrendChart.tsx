import { useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  Legend,
} from 'recharts'
import { formatCurrency, formatNumber } from '../../utils'

interface RevenueTrendChartProps {
  data?: Array<{ date: string; revenue: number; units: number; profit?: number }>
}

function generateMockTrend() {
  const data = []
  const now = new Date()
  for (let i = 89; i >= 0; i--) {
    const d = new Date(now)
    d.setDate(d.getDate() - i)
    const base = 8000 + Math.sin(i / 7) * 2000 + (i % 7 === 5 || i % 7 === 6 ? 3000 : 0)
    const noise = (Math.random() - 0.5) * 1500
    const rev = Math.max(1000, base + noise)
    data.push({
      date: d.toISOString().slice(5, 10),
      revenue: round(rev),
      units: round(rev / 65),
      profit: round(rev * 0.38),
    })
  }
  return data
}

const round = (n: number) => Math.round(n * 100) / 100

export default function RevenueTrendChart({ data }: RevenueTrendChartProps) {
  const chartData = useMemo(() => data ?? generateMockTrend(), [data])

  return (
    <div className="card h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-gray-900">Revenue &amp; Volume Trend</h3>
          <p className="text-xs text-gray-500 mt-0.5">Last 90 days · daily granularity</p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-brand-500" /> Revenue</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Profit</span>
        </div>
      </div>
      <div className="h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="rev" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="profit" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} interval={14} tickLine={false} axisLine={false} />
            <YAxis
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
              formatter={(value: number) => formatCurrency(value)}
            />
            <Area type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} fill="url(#rev)" name="Revenue" />
            <Area type="monotone" dataKey="profit" stroke="#10b981" strokeWidth={2} fill="url(#profit)" name="Profit" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
