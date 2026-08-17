import { Tag, TrendingUp, TrendingDown, Minus, Target, ShieldCheck, BadgeDollarSign } from 'lucide-react'
import type { PricingRecommendation } from '../../types'
import { formatCurrency, formatPercent } from '../../utils'

interface Props {
  recommendation?: PricingRecommendation
}

function mock(): PricingRecommendation {
  return {
    product_id: 1,
    product_name: 'Organic Whole Milk 1 Gallon',
    current_price: 5.99,
    recommended_price: 6.49,
    price_elasticity: -0.73,
    expected_demand_change: -3.6,
    expected_revenue_change: 4.8,
    competitor_avg_price: 6.12,
    margin_impact: 1.8,
    reasoning: 'Price elasticity is -0.73 (inelastic). Current pricing position: at_market. Competitor average: $6.12. Objective: maximize profit.',
  }
}

export default function PricingRecommendationCard({ recommendation }: Props) {
  const r = recommendation ?? mock()
  const direction = r.recommended_price > r.current_price ? 'increase' : r.recommended_price < r.current_price ? 'decrease' : 'hold'
  const delta = r.recommended_price - r.current_price
  const deltaPct = (delta / r.current_price) * 100

  const elasticityClass = Math.abs(r.price_elasticity) > 1 ? 'elastic' : 'inelastic'

  const cat = r.competitor_avg_price
    ? r.recommended_price < r.competitor_avg_price
      ? { label: 'Price Leader', color: 'bg-emerald-100 text-emerald-700', icon: TrendingDown }
      : r.recommended_price > r.competitor_avg_price * 1.08
      ? { label: 'Premium', color: 'bg-purple-100 text-purple-700', icon: ShieldCheck }
      : { label: 'At Market', color: 'bg-blue-100 text-blue-700', icon: Minus }
    : { label: 'No Comp. Data', color: 'bg-gray-100 text-gray-600', icon: Target }

  const DirIcon = direction === 'increase' ? TrendingUp : direction === 'decrease' ? TrendingDown : Minus
  const dirColor = direction === 'increase' ? 'text-emerald-600' : direction === 'decrease' ? 'text-red-600' : 'text-gray-600'
  const dirBg = direction === 'increase' ? 'bg-emerald-500' : direction === 'decrease' ? 'bg-red-500' : 'bg-gray-400'

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4 flex-wrap gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Tag size={16} className="text-amber-500" />
            <h3 className="font-semibold text-gray-900">AI Pricing Recommendation</h3>
          </div>
          <p className="text-sm text-gray-600">{r.product_name}</p>
          <p className="text-xs text-gray-400 mt-0.5">SKU #{r.product_id.toString().padStart(5, '0')}</p>
        </div>
        <span className={`tag ${cat.color} gap-1.5`}>
          <cat.icon size={12} /> {cat.label}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-5">
        <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
          <div className="text-[11px] font-semibold uppercase text-gray-500 tracking-wide">Current Price</div>
          <div className="mt-1 flex items-baseline gap-2">
            <div className="text-3xl font-bold text-gray-900">{formatCurrency(r.current_price)}</div>
          </div>
        </div>
        <div className="p-4 rounded-xl bg-gradient-to-br from-brand-50 via-indigo-50 to-purple-50 border border-brand-100 relative overflow-hidden">
          <div className="text-[11px] font-semibold uppercase text-brand-700 tracking-wide">Recommended</div>
          <div className="mt-1 flex items-baseline gap-2">
            <div className="text-3xl font-bold text-brand-700">{formatCurrency(r.recommended_price)}</div>
            <div className={`flex items-center gap-0.5 font-semibold text-sm ${dirColor}`}>
              <DirIcon size={14} />
              {formatPercent(deltaPct)}
            </div>
          </div>
          <div className="absolute top-3 right-3 w-10 h-10 rounded-full flex items-center justify-center text-white shadow-lg" style={{ background: `linear-gradient(135deg, var(--tw-gradient-stops))`, backgroundImage: `linear-gradient(135deg, ${direction === 'increase' ? '#10b981' : direction === 'decrease' ? '#ef4444' : '#6b7280'}, ${direction === 'increase' ? '#059669' : direction === 'decrease' ? '#dc2626' : '#4b5563'})` }}>
            <DirIcon size={16} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
        <Metric label="Elasticity" value={r.price_elasticity.toFixed(2)} hint={elasticityClass} color={elasticityClass === 'elastic' ? 'text-red-600' : 'text-emerald-600'} />
        <Metric
          label="Demand Impact"
          value={formatPercent(r.expected_demand_change, true)}
          color={r.expected_demand_change < 0 ? 'text-red-600' : 'text-emerald-600'}
        />
        <Metric
          label="Revenue Impact"
          value={formatPercent(r.expected_revenue_change, true)}
          color={r.expected_revenue_change > 0 ? 'text-emerald-600' : 'text-red-600'}
        />
        <Metric
          label="Margin Impact"
          value={`${r.margin_impact > 0 ? '+' : ''}${r.margin_impact.toFixed(1)}pp`}
          color={r.margin_impact > 0 ? 'text-emerald-600' : 'text-red-600'}
        />
      </div>

      {r.competitor_avg_price && (
        <div className="mb-5 p-3 bg-gray-50 rounded-lg border border-gray-100 flex items-center justify-between text-sm">
          <div className="flex items-center gap-2 text-gray-600">
            <BadgeDollarSign size={16} className="text-indigo-500" />
            <span>Competitor average price</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="font-bold text-gray-900">{formatCurrency(r.competitor_avg_price)}</div>
            <div className={`text-xs font-semibold ${r.recommended_price < r.competitor_avg_price ? 'text-emerald-600' : 'text-amber-600'}`}>
              vs {formatCurrency(r.recommended_price)} ({(((r.recommended_price / r.competitor_avg_price) - 1) * 100).toFixed(1)}%)
            </div>
          </div>
        </div>
      )}

      <div className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl border border-amber-100">
        <div className="text-xs font-semibold text-amber-700 mb-1.5 flex items-center gap-1.5">
          <Target size={12} /> AI Reasoning
        </div>
        <div className="text-sm text-gray-700 leading-relaxed">{r.reasoning}</div>
      </div>
    </div>
  )
}

function Metric({ label, value, hint, color = 'text-gray-900' }: { label: string; value: string; hint?: string; color?: string }) {
  return (
    <div className="p-3 bg-white rounded-lg border border-gray-100">
      <div className="text-[10px] font-semibold uppercase text-gray-500 tracking-wide">{label}</div>
      <div className={`mt-1 font-bold ${color}`}>{value}</div>
      {hint && <div className="text-[10px] text-gray-400 mt-0.5 capitalize">{hint}</div>}
    </div>
  )
}
