import { useEffect, useState } from 'react'
import { DollarSign, ShoppingBag, Percent, Warehouse, Tag, Megaphone, Activity, ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import KPICard from '../components/dashboard/KPICard'
import RevenueTrendChart from '../components/dashboard/RevenueTrendChart'
import TopProducts from '../components/dashboard/TopProducts'
import AIInsights from '../components/dashboard/AIInsights'
import DimensionCorrelation from '../components/dashboard/DimensionCorrelation'
import type { KPIData } from '../types'
import { kpiApi } from '../services/api'
import { mockKPIs } from '../utils'

function Header({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="px-8 pt-6 pb-5 flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
        <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
      </div>
      <div className="flex items-center gap-2">
        <button className="btn-secondary !py-2 !text-xs gap-1.5">Last 30 days ▾</button>
        <button className="btn-primary !py-2 !text-xs gap-1.5">
          <Activity size={13} /> Refresh Analytics
        </button>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [kpi, setKpi] = useState<KPIData | null>(null)

  useEffect(() => {
    let cancelled = false
    kpiApi
      .getDashboard()
      .then((r) => !cancelled && setKpi(r))
      .catch(() => !cancelled && setKpi(mockKPIs()))
    return () => {
      cancelled = true
    }
  }, [])

  const k = kpi ?? mockKPIs()

  const moduleLinks = [
    { to: '/forecasting', title: 'Demand Forecasting', desc: 'Prophet · XGBoost · 7–90 day horizon', color: 'from-blue-500 to-indigo-500', icon: Activity },
    { to: '/inventory', title: 'Inventory Optimization', desc: 'EOQ · Safety Stock · ABC Analysis', color: 'from-emerald-500 to-teal-500', icon: Warehouse },
    { to: '/pricing', title: 'Pricing Intelligence', desc: 'Elasticity · Competitor · Margin AI', color: 'from-amber-500 to-orange-500', icon: Tag },
    { to: '/promotions', title: 'Promotion Analytics', desc: 'Lift · ROI · Cannibalization', color: 'from-pink-500 to-rose-500', icon: Megaphone },
  ]

  return (
    <div className="min-h-screen">
      <Header title="Retail Intelligence Dashboard" subtitle="AI-powered planning & decision support across all 4 retail modules" />

      <div className="px-8 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4 mb-6">
          <KPICard title="Total Revenue" value={k.total_revenue} growth={k.revenue_growth} format="currency" icon={<DollarSign size={18} />} accent="blue" />
          <KPICard title="Units Sold" value={k.total_units_sold} growth={k.units_growth} format="number" icon={<ShoppingBag size={18} />} accent="purple" />
          <KPICard title="Gross Margin" value={k.gross_margin} growth={k.margin_growth} format="percent" suffix="%" icon={<Percent size={18} />} accent="green" />
          <KPICard title="AOV" value={k.avg_order_value} format="currency" icon={<DollarSign size={18} />} accent="amber" />
          <KPICard title="Inventory Turnover" value={k.inventory_turnover} format="number" suffix="x" icon={<Warehouse size={18} />} accent="purple" />
          <KPICard title="Promotion ROI" value={k.promotion_roi} format="number" suffix="%" icon={<Megaphone size={18} />} accent={k.promotion_roi < 150 ? 'red' : 'green'} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
          <div className="lg:col-span-2">
            <RevenueTrendChart />
          </div>
          <div>
            <AIInsights />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
          <div className="lg:col-span-2">
            <TopProducts />
          </div>
          <div>
            <DimensionCorrelation />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-gray-900">Retail Planning Modules</h2>
            <div className="text-xs text-gray-500">4 integrated modules · 12+ REST APIs · Event-driven</div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {moduleLinks.map((m, i) => (
              <Link
                key={i}
                to={m.to}
                className="group p-5 bg-white rounded-xl border border-gray-100 hover:border-brand-200 hover:shadow-lg transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${m.color} flex items-center justify-center text-white shadow-md`}>
                    <m.icon size={20} />
                  </div>
                  <ArrowUpRight size={16} className="text-gray-300 group-hover:text-brand-500 transition-colors" />
                </div>
                <div className="font-semibold text-gray-900 group-hover:text-brand-700 transition-colors">{m.title}</div>
                <div className="text-xs text-gray-500 mt-1 leading-snug">{m.desc}</div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
