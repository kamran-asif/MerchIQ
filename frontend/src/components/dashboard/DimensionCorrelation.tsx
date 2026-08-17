import { useMemo } from 'react'
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts'

export default function DimensionCorrelation() {
  const data = useMemo(
    () => [
      { dimension: 'Inventory', revenue: 72, units: 85 },
      { dimension: 'Pricing', revenue: 88, units: 78 },
      { dimension: 'Promotions', revenue: 91, units: 93 },
      { dimension: 'Region', revenue: 64, units: 60 },
      { dimension: 'Weather', revenue: 58, units: 62 },
      { dimension: 'Competitor', revenue: 76, units: 70 },
    ],
    []
  )

  return (
    <div className="card h-full">
      <div className="mb-3">
        <h3 className="font-semibold text-gray-900">6-Dimension Impact Analysis</h3>
        <p className="text-xs text-gray-500 mt-0.5">Correlation strength vs KPIs</p>
      </div>
      <div className="h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 11, fill: '#475569' }} />
            <PolarRadiusAxis tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} domain={[0, 100]} />
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Radar name="Revenue Impact" dataKey="revenue" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} strokeWidth={2} />
            <Radar name="Unit Volume" dataKey="units" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} strokeWidth={2} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
