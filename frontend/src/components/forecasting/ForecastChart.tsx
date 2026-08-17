import { useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import type { ForecastResponse } from '../../types'
import { formatNumber } from '../../utils'

interface Props {
  forecast?: ForecastResponse
}

function generateMock(): ForecastResponse {
  const now = new Date()
  const predictions = []
  for (let i = 1; i <= 30; i++) {
    const d = new Date(now)
    d.setDate(d.getDate() + i)
    const base = 120 + Math.sin(i / 3) * 30 + (i % 7 === 5 || i % 7 === 6 ? 45 : 0)
    const mid = base + (Math.random() - 0.5) * 10
    predictions.push({
      date: d.toISOString().slice(0, 10),
      predicted_value: Math.round(mid),
      lower_bound: Math.round(mid * 0.7),
      upper_bound: Math.round(mid * 1.3),
    })
  }
  return {
    product_id: 1,
    product_name: 'Organic Whole Milk 1 Gallon',
    model_type: 'prophet',
    horizon_days: 30,
    mape: 8.7,
    rmse: 14.2,
    predictions,
    explanation: 'Trend: INCREASING. Key drivers: Seasonality (weekly pattern), Promotions (lift on promo days), Price sensitivity. Confidence: 87%.',
  }
}

export default function ForecastChart({ forecast }: Props) {
  const data = forecast ?? generateMock()

  const chartData = data.predictions.map((p) => ({
    date: p.date.slice(5),
    predicted: p.predicted_value,
    lower: p.lower_bound ?? 0,
    upper: p.upper_bound ?? 0,
  }))

  const total = data.predictions.reduce((a, b) => a + b.predicted_value, 0)
  const avg = total / data.predictions.length

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4 flex-wrap gap-3">
        <div>
          <h3 className="font-semibold text-gray-900">{data.product_name}</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            {data.model_type.toUpperCase()} · {data.horizon_days}-day horizon · MAPE {data.mape}% · RMSE {data.rmse}
          </p>
        </div>
        <div className="flex gap-5 text-right">
          <div>
            <div className="text-xs text-gray-500">Total Predicted</div>
            <div className="font-bold text-lg text-gray-900">{formatNumber(total)} units</div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Avg Daily</div>
            <div className="font-bold text-lg text-brand-600">{formatNumber(avg, 1)}</div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Confidence</div>
            <div className="font-bold text-lg text-emerald-600">{Math.max(50, 100 - (data.mape ?? 20))}%</div>
          </div>
        </div>
      </div>

      <div className="h-[340px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="confidence" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.15} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} interval={4} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line type="monotone" dataKey="upper" stroke="transparent" fill="url(#confidence)" legendType="none" />
            <Line type="monotone" dataKey="lower" stroke="transparent" fill="url(#confidence)" legendType="none" />
            <Line type="monotone" dataKey="predicted" stroke="#3b82f6" strokeWidth={2.5} dot={false} name="Forecast" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 p-4 bg-gradient-to-r from-brand-50 to-indigo-50 rounded-xl border border-brand-100">
        <div className="text-xs font-semibold text-brand-700 mb-1.5">💡 Forecast Explanation</div>
        <div className="text-sm text-gray-700 leading-relaxed">{data.explanation}</div>
      </div>
    </div>
  )
}
