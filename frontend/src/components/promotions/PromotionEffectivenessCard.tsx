import { Megaphone, TrendingUp, CircleDollarSign, Target, PackageOpen, AlertTriangle } from 'lucide-react'
import type { PromotionEffectiveness } from '../../types'
import { formatCurrency, formatNumber, formatPercent } from '../../utils'

interface Props {
  effectiveness?: PromotionEffectiveness
  deep?: any
}

function mockData(): { eff: PromotionEffectiveness; deep: any } {
  const lift = 42.3
  const roi = 225
  const incremental = 58210
  const totalRev = 195840
  return {
    eff: {
      promotion_id: 1,
      promotion_name: 'Summer Flash Sale #3 - 25% Off Grocery',
      incremental_revenue: incremental,
      lift_percentage: lift,
      roi: roi,
      total_units_sold: 28412,
      total_revenue: totalRev,
      cost_of_promotion: 18200,
    },
    deep: {
      promotion_type: 'FLASH_SALE',
      promo_duration_days: 3,
      budget: 15000,
      discount_percent: 25,
      gross_profit: totalRev * 0.39,
      net_profit: totalRev * 0.39 - 18200,
      baseline_daily_revenue: 38900,
      promo_daily_revenue: 65280,
      cannibalization_estimate_pct: 18.5,
    },
  }
}

export default function PromotionEffectivenessCard({ effectiveness, deep }: Props) {
  const m = mockData()
  const e = effectiveness ?? m.eff
  const d = deep ?? m.deep
  const verdict = e.roi >= 200 ? { label: 'EXCELLENT', color: 'text-emerald-600', bg: 'bg-emerald-100', emoji: '🏆' }
    : e.roi >= 100 ? { label: 'GOOD', color: 'text-blue-600', bg: 'bg-blue-100', emoji: '👍' }
    : { label: 'BELOW TARGET', color: 'text-red-600', bg: 'bg-red-100', emoji: '⚠️' }

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-5 flex-wrap gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Megaphone size={16} className="text-pink-500" />
            <h3 className="font-semibold text-gray-900">Promotion Performance</h3>
          </div>
          <div className="text-sm text-gray-600">{e.promotion_name}</div>
          <div className="text-xs text-gray-400 mt-0.5 flex items-center gap-2">
            <span>{d.promotion_duration_days} days · {d.discount_percent}% off</span>
            <span className="w-1 h-1 rounded-full bg-gray-300" />
            <span>Budget: {formatCurrency(d.budget)}</span>
          </div>
        </div>
        <div className={`px-3 py-1.5 rounded-xl ${verdict.bg} flex items-center gap-1.5`}>
          <span className="text-base">{verdict.emoji}</span>
          <span className={`text-xs font-bold uppercase tracking-wider ${verdict.color}`}>{verdict.label}</span>
          <span className="text-xs font-bold text-gray-500 ml-1">ROI {e.roi.toFixed(0)}%</span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
        <StatCard icon={CircleDollarSign} accent="blue" label="Total Revenue" value={formatCurrency(e.total_revenue)} sub={`${d.promo_daily_revenue.toFixed(0)}/day`} />
        <StatCard icon={PackageOpen} accent="purple" label="Units Sold" value={formatNumber(e.total_units_sold)} sub={`${(e.total_units_sold / d.promo_duration_days).toFixed(0)}/day`} />
        <StatCard icon={TrendingUp} accent="emerald" label="Incremental Revenue" value={formatCurrency(e.incremental_revenue)} sub={`+${formatPercent(e.lift_percentage)} lift`} highlight />
        <StatCard icon={Target} accent="amber" label="Promo Cost" value={formatCurrency(e.cost_of_promotion)} sub={`Net Profit ${formatCurrency(d.net_profit)}`} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
        <div className="p-4 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl border border-emerald-100">
          <div className="text-xs font-semibold text-emerald-700 mb-2">📈 Baseline vs. Promotion</div>
          <div className="space-y-2.5">
            <Row label="Baseline daily" value={formatCurrency(d.baseline_daily_revenue)} />
            <Row label="Promo daily" value={formatCurrency(d.promo_daily_revenue)} valueClass="text-emerald-700 font-bold" />
            <div className="h-1.5 bg-white/60 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600 rounded-full" style={{ width: `${Math.min(100, (d.promo_daily_revenue / d.baseline_daily_revenue) * 50)}%` }} />
            </div>
          </div>
        </div>

        <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
          <div className="text-xs font-semibold text-blue-700 mb-2">💰 Financial Breakdown</div>
          <div className="space-y-2.5">
            <Row label="Gross Profit" value={formatCurrency(d.gross_profit)} />
            <Row label="Less: Promo Cost" value={`-${formatCurrency(e.cost_of_promotion)}`} valueClass="text-red-600" />
            <Row label="Net Profit" value={formatCurrency(d.net_profit)} valueClass="text-indigo-700 font-bold" />
          </div>
        </div>

        <div className={`p-4 rounded-xl border ${d.cannibalization_estimate_pct > 15 ? 'bg-red-50 border-red-100' : 'bg-gray-50 border-gray-100'}`}>
          <div className={`text-xs font-semibold mb-2 flex items-center gap-1.5 ${d.cannibalization_estimate_pct > 15 ? 'text-red-700' : 'text-gray-700'}`}>
            <AlertTriangle size={12} /> Cannibalization Risk
          </div>
          <div className="flex items-baseline gap-2 mb-2">
            <span className={`text-2xl font-bold ${d.cannibalization_estimate_pct > 15 ? 'text-red-700' : 'text-gray-700'}`}>
              {d.cannibalization_estimate_pct.toFixed(1)}%
            </span>
            <span className="text-xs text-gray-500">of non-promo categories</span>
          </div>
          <div className="h-2 bg-white/80 rounded-full overflow-hidden mb-2">
            <div className={`h-full rounded-full ${d.cannibalization_estimate_pct > 15 ? 'bg-gradient-to-r from-amber-400 to-red-500' : 'bg-gradient-to-r from-green-400 to-emerald-500'}`}
                 style={{ width: `${Math.min(100, d.cannibalization_estimate_pct * 4)}%` }} />
          </div>
          <div className="text-[11px] text-gray-600 leading-relaxed">
            {d.cannibalization_estimate_pct > 15
              ? 'High cannibalization detected. Review product selection and discount depth for next campaign.'
              : 'Within acceptable range. Monitor regular-price SKU sales for next promo cycle.'}
          </div>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-gradient-to-r from-brand-50 via-purple-50 to-pink-50 border border-purple-100">
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs font-semibold text-purple-700">✨ Promotion Designer Insight</div>
        </div>
        <div className="text-sm text-gray-700 leading-relaxed">
          {e.roi >= 150
            ? `Promotion design is effective with ${e.roi.toFixed(0)}% ROI and ${e.lift_percentage.toFixed(1)}% unit lift. Consider replicating the ${d.promotion_type} mechanics (${d.discount_percent}% off / ${d.promo_duration_days}d cadence) for seasonal events. Watch cannibalization at ${d.cannibalization_estimate_pct}% — tighten category mix next run.`
            : `Rethink discount depth. $${formatCurrency(e.cost_of_promotion)} promo spend generated only ${e.lift_percentage.toFixed(1)}% lift. Reduce discount to ${Math.max(10, d.discount_percent - 10)}% and target high-margin SKUs to hit 150%+ ROI target.`}
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon: Icon, accent, label, value, sub, highlight }: any) {
  const accents: Record<string, string> = {
    blue: 'from-blue-400 to-indigo-500',
    purple: 'from-purple-400 to-pink-500',
    emerald: 'from-emerald-400 to-teal-500',
    amber: 'from-amber-400 to-orange-500',
  }
  return (
    <div className={`p-3 rounded-xl border ${highlight ? 'bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-100' : 'bg-gray-50 border-gray-100'}`}>
      <div className="flex items-center justify-between mb-1.5">
        <div className={`w-7 h-7 rounded-lg bg-gradient-to-br ${accents[accent]} flex items-center justify-center text-white shadow-sm`}>
          <Icon size={14} />
        </div>
      </div>
      <div className="text-lg font-bold text-gray-900">{value}</div>
      <div className="text-[11px] text-gray-500 mt-0.5">{label}</div>
      {sub && <div className="text-[10px] text-gray-400 mt-0.5">{sub}</div>}
    </div>
  )
}

function Row({ label, value, valueClass = 'text-gray-900 font-semibold' }: any) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-gray-600">{label}</span>
      <span className={valueClass}>{value}</span>
    </div>
  )
}
