import { ArrowRight, Package, Shield, Target, TrendingDown, Calendar } from 'lucide-react'
import type { ForecastExplainability } from '../../types'

interface Props {
  explainability?: ForecastExplainability
}

function mock(): ForecastExplainability {
  return {
    product_id: 1,
    key_drivers: [
      { driver: 'Seasonality (weekly pattern)', impact_percent: 28.4 },
      { driver: 'Promotions (lift on promo days)', impact_percent: 22.1 },
      { driver: 'Price sensitivity', impact_percent: 14.7 },
    ],
    seasonal_patterns: [
      { pattern: 'Peak days: Saturday, Sunday', type: 'weekly' },
      { pattern: 'Low days: Tuesday, Wednesday', type: 'weekly' },
      { pattern: 'Peak months: 11, 12 (Holiday season)', type: 'monthly' },
    ],
    trend_direction: 'increasing',
    confidence_level: 0.87,
    risk_factors: [
      'Promotion calendar changes could significantly impact demand',
      'Weather events may affect foot traffic',
      'Competitor pricing actions could shift demand',
    ],
  }
}

export default function ForecastExplainabilityCard({ explainability }: Props) {
  const data = explainability ?? mock()
  const trendMap: Record<string, { label: string; color: string; icon: any }> = {
    increasing: { label: 'Increasing', color: 'bg-emerald-100 text-emerald-700', icon: TrendingDown },
    decreasing: { label: 'Decreasing', color: 'bg-red-100 text-red-700', icon: TrendingDown },
    stable: { label: 'Stable', color: 'bg-gray-100 text-gray-700', icon: Target },
    insufficient_data: { label: 'Insufficient Data', color: 'bg-amber-100 text-amber-700', icon: Calendar },
  }
  const trend = trendMap[data.trend_direction] ?? trendMap.stable

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-5">
        <div>
          <h3 className="font-semibold text-gray-900">Forecast Drivers &amp; Explainability</h3>
          <p className="text-xs text-gray-500 mt-0.5">Prophet / XGBoost · SHAP-style attribution</p>
        </div>
        <span className={`tag ${trend.color} gap-1.5`}>
          <Package size={12} /> {trend.label}
        </span>
      </div>

      <div className="mb-5">
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2.5">🔑 Key Demand Drivers</div>
        <div className="space-y-2.5">
          {data.key_drivers.map((d, i) => {
            const maxImpact = Math.max(...data.key_drivers.map((k: any) => k.impact_percent ?? 10))
            const pct = ((d.impact_percent ?? 0) / maxImpact) * 100
            return (
              <div key={i}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="font-medium text-gray-800">{d.driver}</span>
                  <span className="font-semibold text-brand-600">{d.impact_percent ?? d.impact}% impact</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-brand-400 via-indigo-500 to-purple-500"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="mb-5">
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2.5">📅 Seasonal Patterns</div>
        <ul className="space-y-1.5">
          {data.seasonal_patterns.map((p, i) => (
            <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
              <ArrowRight size={14} className="mt-0.5 text-gray-400 flex-shrink-0" />
              <span><span className="font-medium capitalize">{p.type}:</span> {p.pattern}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="mb-5">
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2.5">🎯 Model Confidence</div>
        <div className="flex items-center gap-3">
          <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600 rounded-full"
              style={{ width: `${data.confidence_level * 100}%` }}
            />
          </div>
          <div className="font-bold text-emerald-700">{(data.confidence_level * 100).toFixed(0)}%</div>
        </div>
      </div>

      <div>
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2.5 flex items-center gap-1.5">
          <Shield size={12} /> Risk Factors
        </div>
        <ul className="space-y-1.5">
          {data.risk_factors.map((r, i) => (
            <li key={i} className="text-xs text-gray-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 leading-relaxed">
              ⚠️ {r}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
