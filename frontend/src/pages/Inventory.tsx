import InventoryOptimizationTable from '../components/inventory/InventoryOptimizationTable'
import { inventoryApi } from '../services/api'
import { useEffect, useState } from 'react'
import { formatCurrency, formatNumber } from '../utils'

export default function InventoryPage() {
  const [kpis, setKpis] = useState<any>(null)
  const [abc, setAbc] = useState<any>(null)

  useEffect(() => {
    let c = false
    inventoryApi.kpis().then((r) => !c && setKpis(r)).catch(() => !c && setKpis(mockKPIs()))
    inventoryApi.abcAnalysis().then((r) => !c && setAbc(r)).catch(() => !c && setAbc(mockABC()))
    return () => { c = true }
  }, [])

  const k = kpis ?? mockKPIs()
  const a = abc ?? mockABC()

  return (
    <div className="min-h-screen">
      <div className="px-8 pt-6 pb-5">
        <h1 className="text-2xl font-bold text-gray-900">Inventory Optimization</h1>
        <p className="text-sm text-gray-500 mt-1">EOQ · Safety Stock · Reorder Points · ABC Analysis · Purchase Order Automation</p>
      </div>

      <div className="px-8 pb-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <KPI label="Total SKUs" value={formatNumber(k.total_sku_count)} accent="from-blue-500 to-indigo-500" />
          <KPI label="Inventory Value" value={formatCurrency(k.total_inventory_value)} accent="from-emerald-500 to-teal-500" />
          <KPI label="Stockout Risk" value={`${k.stockout_rate.toFixed(1)}%`} highlight={k.stockout_rate > 3} accent="from-red-500 to-rose-500" />
          <KPI label="Overstocked" value={`${k.overstocked_sku_count} (${k.overstocked_rate.toFixed(1)}%)`} accent="from-purple-500 to-pink-500" />
          <KPI label="Turnover" value={`${k.inventory_turnover.toFixed(2)}x`} accent="from-amber-500 to-orange-500" />
        </div>

        <div className="mb-6">
          <InventoryOptimizationTable />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-gray-900">ABC Classification</h3>
                <p className="text-xs text-gray-500 mt-0.5">Pareto analysis — A = 80% revenue, B = 15%, C = 5%</p>
              </div>
              <div className="text-xs text-gray-500">{a.total_products} SKUs · ${formatNumber(a.total_revenue, 0)}</div>
            </div>
            <div className="grid grid-cols-3 gap-4 mb-4">
              {(['A', 'B', 'C'] as const).map((cls) => (
                <div key={cls} className={`p-4 rounded-xl border ${
                  cls === 'A' ? 'bg-emerald-50 border-emerald-100' : cls === 'B' ? 'bg-amber-50 border-amber-100' : 'bg-gray-50 border-gray-100'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className={`text-lg font-bold ${cls === 'A' ? 'text-emerald-700' : cls === 'B' ? 'text-amber-700' : 'text-gray-700'}`}>Class {cls}</div>
                    <div className="text-[10px] font-semibold uppercase tracking-wide opacity-60">{cls === 'A' ? 'High Value' : cls === 'B' ? 'Medium' : 'Low'}</div>
                  </div>
                  <div className="space-y-1 text-xs">
                    <Row label="Items" value={`${a.summary[cls].item_count} (${a.summary[cls].item_pct}%)`} />
                    <Row label="Revenue" value={`${formatCurrency(a.summary[cls].revenue)} (${a.summary[cls].revenue_pct}%)`} />
                  </div>
                </div>
              ))}
            </div>
            <div className="space-y-2 max-h-[260px] overflow-y-auto">
              {a.classification.slice(0, 12).map((row: any, i: number) => (
                <div key={i} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 text-sm">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className={`w-6 h-6 rounded-md flex items-center justify-center text-[11px] font-bold ${
                      row.class === 'A' ? 'bg-emerald-100 text-emerald-700' : row.class === 'B' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-700'
                    }`}>{row.class}</span>
                    <span className="font-medium text-gray-800 truncate">{row.product_name}</span>
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="text-gray-500">{row.cumulative_pct}%</span>
                    <span className="font-semibold text-gray-900 w-24 text-right">{formatCurrency(row.revenue)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">Replenishment Strategy</h3>
            <div className="space-y-3">
              {[
                { title: 'Safety Stock Calculation', desc: 'Z = 1.65 (95% service level) · Demand std dev · √Lead Time', metric: 'Applied to 100% of SKUs' },
                { title: 'EOQ Optimization', desc: '√(2DS/H) · Balance holding + ordering cost', metric: 'Avg 18% cost reduction' },
                { title: 'Reorder Point Logic', desc: '(Avg Daily Demand × Lead Time) + Safety Stock', metric: 'Dynamic, updated daily' },
                { title: 'Lead Time Adjustments', desc: 'Per-SKU per-region based on vendor SLAs', metric: '7–28 day range' },
                { title: 'Stockout Alerts', desc: 'On-hand ≤ Reorder Point → Kafka event + Copilot notification', metric: `${k.stockout_sku_count} active` },
              ].map((s, i) => (
                <div key={i} className="p-3 rounded-xl border border-gray-100 bg-gray-50/50">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-brand-500 to-indigo-500 text-white flex items-center justify-center text-xs font-bold flex-shrink-0">
                        {i + 1}
                      </div>
                      <div>
                        <div className="font-semibold text-sm text-gray-900">{s.title}</div>
                        <div className="text-xs text-gray-600 mt-0.5 leading-relaxed">{s.desc}</div>
                      </div>
                    </div>
                    <div className="text-[11px] font-semibold text-brand-700 bg-brand-50 px-2 py-1 rounded-md whitespace-nowrap">{s.metric}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function KPI({ label, value, accent, highlight }: any) {
  return (
    <div className={`p-4 rounded-xl border shadow-sm ${highlight ? 'bg-gradient-to-br from-red-50 to-rose-50 border-red-100' : 'bg-white border-gray-100'}`}>
      <div className="flex items-center gap-2 mb-2">
        <div className={`w-7 h-7 rounded-lg bg-gradient-to-br ${accent} opacity-90`} />
        <div className="text-xs font-semibold text-gray-600">{label}</div>
      </div>
      <div className={`text-xl font-bold ${highlight ? 'text-red-700' : 'text-gray-900'}`}>{value}</div>
    </div>
  )
}

function Row({ label, value }: any) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-600">{label}</span>
      <span className="font-semibold text-gray-800">{value}</span>
    </div>
  )
}

function mockKPIs() {
  return {
    total_sku_count: 1248,
    total_inventory_value: 2847500,
    stockout_sku_count: 35,
    stockout_rate: 2.8,
    overstocked_sku_count: 142,
    overstocked_rate: 11.4,
    avg_days_of_supply: 38.5,
    inventory_turnover: 5.4,
  }
}

function mockABC() {
  const classes = ['A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'C', 'C', 'C', 'C', 'C']
  const names = ['Organic Whole Milk 1G', 'Avocado Hass Premium', 'Sourdough Artisan Loaf', 'Free-Range Eggs Doz', 'Grass Fed Beef 1lb',
    'Fresh Atlantic Salmon', 'Greek Yogurt Plain 32oz', 'Organic Baby Spinach 5oz', 'Almond Milk Unsweetened', 'Chicken Breast Boneless',
    'Pasta Marinara Sauce', 'Blueberries 6oz', 'Cheddar Block Sharp', 'Orange Juice Pulp Free', 'Peanut Butter Crunchy']
  let cumRev = 0
  const totalRev = 1247832
  const revs = [142318, 128492, 118503, 98475, 82350, 71293, 64285, 52183, 48575, 42395, 38291, 27182, 21487, 17283, 14835]
  return {
    total_products: 1248,
    total_revenue: totalRev,
    summary: {
      A: { item_count: 250, item_pct: 20.0, revenue: 998265, revenue_pct: 80.0 },
      B: { item_count: 312, item_pct: 25.0, revenue: 187175, revenue_pct: 15.0 },
      C: { item_count: 686, item_pct: 55.0, revenue: 62390, revenue_pct: 5.0 },
    },
    classification: names.map((n, i) => {
      cumRev += revs[i]
      return {
        product_id: i + 1, product_name: n, sku: `SKU-${(10000 + i)}`,
        revenue: revs[i], units: Math.round(revs[i] / 15), profit: revs[i] * 0.38, margin_pct: 38,
        cumulative_pct: Math.round(cumRev / totalRev * 1000) / 10, class: classes[i],
      }
    }),
  }
}
