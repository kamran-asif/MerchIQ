import PromotionEffectivenessCard from '../components/promotions/PromotionEffectivenessCard'
import { promotionApi } from '../services/api'
import { useEffect, useState } from 'react'
import { formatCurrency } from '../utils'

export default function PromotionsPage() {
  const [recs, setRecs] = useState<any[]>([])

  useEffect(() => {
    let c = false
    promotionApi.recommendations().then((r) => !c && setRecs(r)).catch(() => !c && setRecs(mockRecs()))
    return () => { c = true }
  }, [])

  const r = recs.length ? recs : mockRecs()

  return (
    <div className="min-h-screen">
      <div className="px-8 pt-6 pb-5">
        <h1 className="text-2xl font-bold text-gray-900">Promotion Analytics</h1>
        <p className="text-sm text-gray-500 mt-1">Promotion ROI · Lift measurement · Cannibalization analysis · Campaign recommendations</p>
      </div>

      <div className="px-8 pb-8">
        <div className="mb-6">
          <PromotionEffectivenessCard />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
          {[
            { label: 'Active Promotions', value: 7, sub: '2 ending this week', accent: 'bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-100' },
            { label: 'Avg. Campaign ROI', value: '187%', sub: 'Target: 200%', accent: 'bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-100' },
            { label: 'Incremental Revenue', value: formatCurrency(284750), sub: 'Last 90 days', accent: 'bg-gradient-to-br from-purple-50 to-pink-50 border-purple-100' },
          ].map((c, i) => (
            <div key={i} className={`p-5 rounded-xl border ${c.accent}`}>
              <div className="text-xs font-semibold uppercase tracking-wide text-gray-500">{c.label}</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">{c.value}</div>
              <div className="text-xs text-gray-600 mt-0.5">{c.sub}</div>
            </div>
          ))}
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
            <div>
              <h3 className="font-semibold text-gray-900">AI Promotion Recommendations</h3>
              <p className="text-xs text-gray-500 mt-0.5">Next-best promotion types based on historical performance + elasticity data</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {r.map((rec: any, i: number) => (
              <div key={i} className={`p-4 rounded-xl border transition-all hover:shadow-md ${
                rec.risk_level === 'low' ? 'bg-emerald-50/50 border-emerald-100' :
                rec.risk_level === 'medium' ? 'bg-amber-50/50 border-amber-100' : 'bg-red-50/50 border-red-100'
              }`}>
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="font-semibold text-gray-900 flex items-center gap-2">
                      {rec.name}
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold uppercase tracking-wide ${
                        rec.risk_level === 'low' ? 'bg-emerald-200 text-emerald-800' :
                        rec.risk_level === 'medium' ? 'bg-amber-200 text-amber-800' : 'bg-red-200 text-red-800'
                      }`}>{rec.risk_level}</span>
                    </div>
                    <div className="text-[11px] text-gray-500 mt-0.5 font-mono">{rec.type}</div>
                  </div>
                </div>
                <p className="text-xs text-gray-600 leading-relaxed mb-3 min-h-[48px]">{rec.description}</p>
                <div className="grid grid-cols-3 gap-2 mb-3">
                  <Mini label="Discount" value={`${rec.suggested_discount_percent}%`} />
                  <Mini label="Duration" value={`${rec.recommended_duration_days}d`} />
                  <Mini label="Lift" value={`~${rec.expected_lift_pct}%`} />
                </div>
                <div className="text-[11px] text-gray-600 mb-3">
                  <span className="font-semibold">Best for: </span>{rec.best_for_categories.join(', ')}
                </div>
                <div className="text-xs mb-3">
                  <span className="text-gray-500">Expected ROI: </span>
                  <span className="font-bold text-emerald-700">{rec.expected_roi_range}%</span>
                </div>
                <button className="w-full text-xs font-semibold py-2 rounded-lg bg-white border border-gray-200 hover:border-brand-200 hover:bg-brand-50 hover:text-brand-700 transition-colors">
                  🚀 Launch Campaign
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function Mini({ label, value }: any) {
  return (
    <div className="p-2 rounded-lg bg-white/70 border border-white text-center">
      <div className="text-[10px] text-gray-500 uppercase tracking-wide">{label}</div>
      <div className="text-sm font-bold text-gray-800 mt-0.5">{value}</div>
    </div>
  )
}

function mockRecs() {
  return [
    { type: 'FLASH_SALE', name: 'Flash Sale', suggested_discount_percent: 22, recommended_duration_days: 3, expected_lift_pct: 55, expected_roi_range: '45-100', description: 'Short-duration, high-discount event for quick inventory clearance or traffic spike', best_for_categories: ['Overstocked items', 'Seasonal products', 'Slow-moving SKUs'], risk_level: 'medium' },
    { type: 'BOGO', name: 'Buy One Get One', suggested_discount_percent: 40, recommended_duration_days: 7, expected_lift_pct: 85, expected_roi_range: '40-140', description: 'BOGO promotions drive higher unit volume and clear inventory faster', best_for_categories: ['Complementary products', 'High-margin items', 'Consumer goods'], risk_level: 'high' },
    { type: 'PERCENT_OFF', name: 'Percentage Discount', suggested_discount_percent: 17, recommended_duration_days: 14, expected_lift_pct: 32, expected_roi_range: '25-80', description: 'Standard tiered discount for sustained sales uplift', best_for_categories: ['Category-wide promotions', 'Regular items', 'Customer retention'], risk_level: 'low' },
    { type: 'BUNDLE', name: 'Bundle Deal', suggested_discount_percent: 15, recommended_duration_days: 21, expected_lift_pct: 40, expected_roi_range: '30-80', description: 'Bundled pricing encourages larger basket sizes', best_for_categories: ['Complementary goods', 'Slow-moving combos', 'Gift sets'], risk_level: 'low' },
    { type: 'LOYALTY_EXCLUSIVE', name: 'Loyalty Member Exclusive', suggested_discount_percent: 10, recommended_duration_days: 7, expected_lift_pct: 22, expected_roi_range: '20-55', description: 'Rewards program promotions for customer retention and engagement', best_for_categories: ['High-value customers', 'Repeat purchase items', 'Premium SKUs'], risk_level: 'low' },
  ]
}
