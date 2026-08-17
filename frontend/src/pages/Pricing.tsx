import PricingRecommendationCard from '../components/pricing/PricingRecommendationCard'
import { pricingApi } from '../services/api'
import { useEffect, useState } from 'react'
import { formatCurrency } from '../utils'

export default function PricingPage() {
  const [elasticity, setElasticity] = useState<any>(null)
  const [bulk, setBulk] = useState<any[]>([])

  useEffect(() => {
    let c = false
    pricingApi.elasticity(1).then((r) => !c && setElasticity(r)).catch(() => !c && setElasticity(mockElasticity()))
    pricingApi.bulkRecommendations().then((r) => !c && setBulk(r.recommendations ?? [])).catch(() => !c && setBulk(mockBulk()))
    return () => { c = true }
  }, [])

  const e = elasticity ?? mockElasticity()
  const b = bulk.length ? bulk : mockBulk()

  return (
    <div className="min-h-screen">
      <div className="px-8 pt-6 pb-5">
        <h1 className="text-2xl font-bold text-gray-900">Pricing Intelligence</h1>
        <p className="text-sm text-gray-500 mt-1">Price elasticity modeling · Competitor benchmarking · AI-optimized recommendations · Margin-aware</p>
      </div>

      <div className="px-8 pb-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
          <div className="lg:col-span-2">
            <PricingRecommendationCard />
          </div>
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-gray-900">Price Elasticity Curve</h3>
                <p className="text-xs text-gray-500 mt-0.5">Product #{e.product_id} · {e.calculation_method}</p>
              </div>
              <span className={`tag ${e.elasticity_category === 'elastic' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'}`}>
                {e.elasticity_category.toUpperCase()} (e = {e.elasticity})
              </span>
            </div>
            <div className="space-y-2">
              {e.curve.map((p: any, i: number) => (
                <div key={i} className={`p-2.5 rounded-lg text-sm ${
                  p.price_change_pct === 0 ? 'bg-blue-50 border border-blue-100' :
                  p.expected_profit > 0 ? 'bg-gray-50' : 'bg-red-50/50 border border-red-100'
                }`}>
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                        p.price_change_pct < 0 ? 'bg-red-100 text-red-700' : p.price_change_pct > 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-200 text-gray-700'
                      }`}>{p.price_change_pct > 0 ? '+' : ''}{p.price_change_pct}%</span>
                      <span className="font-semibold text-gray-900">{formatCurrency(p.new_price)}</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs">
                      <span className="text-gray-500">Qty {p.expected_qty.toFixed(0)}</span>
                      <span className="text-gray-500">Rev {formatCurrency(p.expected_revenue)}</span>
                      <span className="font-bold text-emerald-700">{formatCurrency(p.expected_profit)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
            <div>
              <h3 className="font-semibold text-gray-900">Bulk Pricing Recommendations</h3>
              <p className="text-xs text-gray-500 mt-0.5">AI-generated pricing opportunities ranked by margin upside</p>
            </div>
            <div className="flex items-center gap-2">
              <button className="btn-secondary !py-1.5 !text-xs">By Category</button>
              <button className="btn-primary !py-1.5 !text-xs">Apply Selected ▾</button>
            </div>
          </div>
          <div className="overflow-x-auto rounded-xl border border-gray-100">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left border-b border-gray-100">
                  <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide">Product</th>
                  <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">Current</th>
                  <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">Recommended</th>
                  <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">Elasticity</th>
                  <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">Demand Δ</th>
                  <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">Revenue Δ</th>
                  <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">Margin Δ</th>
                  <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {b.map((p: any, i: number) => (
                  <tr key={i} className="border-b border-gray-50 hover:bg-gray-50/70">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{p.product_name}</div>
                      <div className="text-[11px] text-gray-500">SKU #{p.product_id.toString().padStart(5, '0')}</div>
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700">{formatCurrency(p.current_price)}</td>
                    <td className="px-4 py-3 text-right">
                      <span className={`font-bold ${p.recommended_price > p.current_price ? 'text-emerald-600' : p.recommended_price < p.current_price ? 'text-red-600' : 'text-gray-900'}`}>
                        {formatCurrency(p.recommended_price)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700 font-mono text-xs">{p.price_elasticity.toFixed(3)}</td>
                    <td className={`px-4 py-3 text-right font-semibold ${p.expected_demand_change_pct > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {p.expected_demand_change_pct > 0 ? '+' : ''}{p.expected_demand_change_pct.toFixed(1)}%
                    </td>
                    <td className={`px-4 py-3 text-right font-semibold ${p.expected_revenue_change_pct > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {p.expected_revenue_change_pct > 0 ? '+' : ''}{p.expected_revenue_change_pct.toFixed(1)}%
                    </td>
                    <td className={`px-4 py-3 text-right font-semibold ${p.margin_impact_pct > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {p.margin_impact_pct > 0 ? '+' : ''}{p.margin_impact_pct.toFixed(1)}pp
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button className="text-xs font-medium text-brand-600 hover:text-brand-700 px-2.5 py-1 rounded-lg hover:bg-brand-50">Apply</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

function mockElasticity() {
  return {
    product_id: 1,
    product_name: 'Organic Whole Milk 1 Gallon',
    current_price: 5.99,
    elasticity: -0.73,
    elasticity_category: 'inelastic',
    calculation_method: 'regression_based',
    curve: [
      { price_change_pct: -20, new_price: 4.79, expected_qty: 175, expected_revenue: 838, expected_profit: 226 },
      { price_change_pct: -10, new_price: 5.39, expected_qty: 150, expected_revenue: 809, expected_profit: 242 },
      { price_change_pct: 0, new_price: 5.99, expected_qty: 128, expected_revenue: 767, expected_profit: 249 },
      { price_change_pct: 10, new_price: 6.59, expected_qty: 112, expected_revenue: 738, expected_profit: 258 },
      { price_change_pct: 20, new_price: 7.19, expected_qty: 98, expected_revenue: 705, expected_profit: 254 },
    ],
  }
}

function mockBulk(): any[] {
  return [
    { product_id: 1, product_name: 'Organic Whole Milk 1G', current_price: 5.99, recommended_price: 6.49, price_elasticity: -0.73, expected_demand_change_pct: -3.6, expected_revenue_change_pct: 4.8, margin_impact_pct: 1.8 },
    { product_id: 2, product_name: 'Avocado Hass Premium', current_price: 2.49, recommended_price: 2.29, price_elasticity: -1.42, expected_demand_change_pct: 12.6, expected_revenue_change_pct: 3.8, margin_impact_pct: -0.5 },
    { product_id: 3, product_name: 'Sourdough Artisan Loaf', current_price: 7.99, recommended_price: 8.49, price_elasticity: -0.55, expected_demand_change_pct: -2.4, expected_revenue_change_pct: 6.2, margin_impact_pct: 2.1 },
    { product_id: 4, product_name: 'Free-Range Eggs Doz', current_price: 6.99, recommended_price: 6.99, price_elasticity: -0.32, expected_demand_change_pct: 0, expected_revenue_change_pct: 0, margin_impact_pct: 0 },
    { product_id: 5, product_name: 'Grass Fed Beef 1lb', current_price: 12.99, recommended_price: 13.79, price_elasticity: -0.61, expected_demand_change_pct: -3.1, expected_revenue_change_pct: 5.8, margin_impact_pct: 1.9 },
    { product_id: 6, product_name: 'Fresh Atlantic Salmon', current_price: 17.99, recommended_price: 18.79, price_elasticity: -0.48, expected_demand_change_pct: -1.8, expected_revenue_change_pct: 4.6, margin_impact_pct: 1.7 },
  ]
}
