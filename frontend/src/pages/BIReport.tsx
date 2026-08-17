import { useEffect, useState } from 'react'
import { kpiApi } from '../services/api'
import type { ExecutiveReport } from '../types'
import { formatCurrency, formatNumber, formatPercent } from '../utils'

function mockReport(): ExecutiveReport {
  const now = new Date().toISOString()
  return {
    report_period: 'Last 30 days (monthly)',
    generated_at: now,
    summary: 'Positive period with revenue at $1,247,833 (+8.4%). Margin 38.7% with 48,216 units sold across monthly period. Strong category performance offset by Northeast stockouts and promotion cannibalization.',
    kpi_summary: {
      total_revenue: 1247832.56, revenue_growth: 8.4, total_units_sold: 48216, units_growth: 5.2,
      gross_margin: 38.7, margin_growth: 1.2, avg_order_value: 68.42, inventory_turnover: 5.4,
      stockout_rate: 2.8, promotion_roi: 187.5,
    },
    top_performers: [
      { product_id: 1, product_name: 'Organic Whole Milk 1G', sku: 'SKU-00001', revenue: 142318, units: 28412, profit: 46176, margin_pct: 32.4 },
      { product_id: 2, product_name: 'Avocado Hass Premium', sku: 'SKU-00002', revenue: 128492, units: 52238, profit: 53324, margin_pct: 41.5 },
      { product_id: 3, product_name: 'Sourdough Artisan Loaf', sku: 'SKU-00003', revenue: 118503, units: 15031, profit: 66592, margin_pct: 56.2 },
      { product_id: 4, product_name: 'Free-Range Eggs Doz', sku: 'SKU-00004', revenue: 98475, units: 14287, profit: 28262, margin_pct: 28.7 },
      { product_id: 5, product_name: 'Grass Fed Beef 1lb', sku: 'SKU-00005', revenue: 82350, units: 6570, profit: 28657, margin_pct: 34.8 },
    ],
    underperformers: [
      { product_id: 20, product_name: 'Frozen Pizza Margherita', sku: 'SKU-00020', revenue: 12450, units: 2890, profit: 2365, margin_pct: 19.0 },
      { product_id: 21, product_name: 'Canned Tuna in Water', sku: 'SKU-00021', revenue: 11280, units: 5013, profit: 1580, margin_pct: 14.0 },
      { product_id: 22, product_name: 'White Bread Loaf', sku: 'SKU-00022', revenue: 14820, units: 6897, profit: 2519, margin_pct: 17.0 },
      { product_id: 23, product_name: 'Chips Plain 8oz', sku: 'SKU-00023', revenue: 17283, units: 9210, profit: 3975, margin_pct: 23.0 },
      { product_id: 24, product_name: 'Sugary Cereal Family', sku: 'SKU-00024', revenue: 19285, units: 5230, profit: 4243, margin_pct: 22.0 },
    ],
    key_insights: [
      'Revenue growth of 8.4% outpaced industry benchmarks, driven by strong category performance in Avocado and Dairy',
      'Healthy gross margin of 38.7% indicates effective cost management and pricing discipline',
      'Stockout rate of 2.8% is within target, but Northeast region at 5.2% requires attention',
      'Inventory turnover at 5.4x suggests healthy balance, though C-class items show 12-day oversupply',
    ],
    recommendations: [
      'Focus on top-performing categories to replicate Organic Whole Milk success — premiumize via private label',
      'Address underperformance in Frozen Pizza — apply RCA corrective actions: reset merchandising, optimize shelf',
      'Continue optimizing promotion mix targeting 200%+ ROI — BOGO + Flash Sale for CPG categories',
      'Implement AI-driven reorder point recommendations to reduce Northeast stockouts by 60%',
    ],
    risk_alerts: [
      'Promotion ROI below 200% target — review Summer Flash Sale #3 mechanics and discount depth',
      'Low inventory turnover tying up working capital in C-class SKUs — markdown or bundle strategy required',
    ],
  }
}

export default function BIReportPage() {
  const [report, setReport] = useState<ExecutiveReport | null>(null)
  const [period, setPeriod] = useState('monthly')

  useEffect(() => {
    let c = false
    kpiApi.getExecutiveReport(period).then((r) => !c && setReport(r)).catch(() => !c && setReport(mockReport()))
    return () => { c = true }
  }, [period])

  const r = report ?? mockReport()
  const k = r.kpi_summary

  return (
    <div className="min-h-screen">
      <div className="px-8 pt-6 pb-5 flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Executive Business Report</h1>
          <p className="text-sm text-gray-500 mt-1">Board-ready summary · KPI analysis · AI insights · Strategic recommendations</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="inline-flex rounded-lg border border-gray-200 overflow-hidden text-sm font-medium">
            {(['weekly', 'monthly', 'quarterly'] as const).map((p) => (
              <button key={p} onClick={() => setPeriod(p)}
                className={`px-4 py-2 capitalize ${period === p ? 'bg-brand-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}>
                {p}
              </button>
            ))}
          </div>
          <button className="btn-primary gap-1.5">📄 Export PDF</button>
        </div>
      </div>

      <div className="px-8 pb-8">
        <div className="card mb-6 bg-gradient-to-br from-indigo-50 via-brand-50 to-purple-50 border-brand-100">
          <div className="flex items-start justify-between flex-wrap gap-3 mb-3">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-brand-700">Reporting Period</div>
              <div className="text-xl font-bold text-gray-900 mt-0.5">{r.report_period}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500">Generated</div>
              <div className="text-sm font-medium text-gray-800">{new Date(r.generated_at).toLocaleString()}</div>
            </div>
          </div>
          <div className="p-4 bg-white/70 backdrop-blur rounded-xl border border-white">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">🤖 AI Executive Summary</div>
            <div className="text-sm text-gray-800 leading-relaxed">{r.summary}</div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <KPI label="Revenue" value={formatCurrency(k.total_revenue)} growth={k.revenue_growth} accent="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-100 text-blue-700" />
          <KPI label="Gross Margin" value={`${k.gross_margin.toFixed(1)}%`} growth={k.margin_growth} suffix="pp" accent="bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-100 text-emerald-700" />
          <KPI label="Units Sold" value={formatNumber(k.total_units_sold)} growth={k.units_growth} accent="bg-gradient-to-br from-purple-50 to-pink-50 border-purple-100 text-purple-700" />
          <KPI label="Inventory Turnover" value={`${k.inventory_turnover.toFixed(1)}x`} accent="bg-gradient-to-br from-amber-50 to-orange-50 border-amber-100 text-amber-700" />
          <KPI label="Promotion ROI" value={`${k.promotion_roi.toFixed(0)}%`} accent={`bg-gradient-to-br ${k.promotion_roi < 150 ? 'from-red-50 to-rose-50 border-red-100 text-red-700' : 'from-emerald-50 to-teal-50 border-emerald-100 text-emerald-700'}`} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">⭐ Top Performers</h3>
              <span className="tag bg-emerald-100 text-emerald-700">{r.top_performers.length} SKUs</span>
            </div>
            <div className="space-y-2">
              {r.top_performers.map((p, i) => (
                <PerfRow key={i} rank={i + 1} name={p.product_name} revenue={p.revenue} units={p.units} margin={p.margin_pct} positive />
              ))}
            </div>
          </div>
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">⚠️ Underperformers</h3>
              <span className="tag bg-red-100 text-red-700">{r.underperformers.length} SKUs</span>
            </div>
            <div className="space-y-2">
              {r.underperformers.map((p, i) => (
                <PerfRow key={i} rank={i + 1} name={p.product_name} revenue={p.revenue} units={p.units} margin={p.margin_pct} />
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
          <Section title="💡 Key Insights" items={r.key_insights} color="blue" />
          <Section title="🎯 Recommendations" items={r.recommendations} color="emerald" />
          <Section title="🚨 Risk Alerts" items={r.risk_alerts} color="red" />
        </div>
      </div>
    </div>
  )
}

function KPI({ label, value, growth, suffix = '%', accent }: any) {
  return (
    <div className={`p-4 rounded-xl border ${accent.split(' ')[0]} ${accent.split(' ')[1]}`}>
      <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">{label}</div>
      <div className="flex items-baseline justify-between gap-2 flex-wrap">
        <div className={`text-2xl font-bold ${accent.split(' ')[2]}`}>{value}</div>
        {growth != null && (
          <div className={`text-xs font-bold ${growth > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
            {growth > 0 ? '+' : ''}{growth}{suffix === '%' && growth != null ? '%' : suffix === 'pp' ? 'pp' : ''}
          </div>
        )}
      </div>
    </div>
  )
}

function PerfRow({ rank, name, revenue, units, margin, positive }: any) {
  return (
    <div className={`flex items-center gap-3 p-2.5 rounded-lg transition-colors ${positive ? 'hover:bg-emerald-50/50' : 'hover:bg-red-50/50'}`}>
      <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold ${positive ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
        {rank}
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-medium text-gray-900 truncate">{name}</div>
        <div className="text-[11px] text-gray-500">{formatNumber(units)} units · Margin {margin.toFixed(1)}%</div>
      </div>
      <div className={`text-right ${positive ? 'text-emerald-700' : 'text-red-700'}`}>
        <div className="font-bold">{formatCurrency(revenue)}</div>
      </div>
    </div>
  )
}

function Section({ title, items, color }: any) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 border-blue-100 text-blue-800',
    emerald: 'bg-emerald-50 border-emerald-100 text-emerald-800',
    red: 'bg-red-50 border-red-100 text-red-800',
  }
  const tagColor = colors[color]
  return (
    <div className="card">
      <div className="font-semibold text-gray-900 mb-3">{title}</div>
      <ol className="space-y-2.5">
        {items.map((item: string, i: number) => (
          <li key={i} className={`p-3 rounded-xl border ${tagColor.split(' ')[0]} ${tagColor.split(' ')[1]}`}>
            <div className="flex items-start gap-2.5 text-sm leading-relaxed">
              <span className={`inline-flex items-center justify-center w-5 h-5 rounded-full text-[11px] font-bold flex-shrink-0 ${tagColor.split(' ')[2]} bg-white/60`}>{i + 1}</span>
              <span>{item}</span>
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}
