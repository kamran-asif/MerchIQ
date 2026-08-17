import { Routes, Route, NavLink, Link } from 'react-router-dom'
import {
  LayoutDashboard,
  TrendingUp,
  Warehouse,
  Tag,
  Megaphone,
  Bot,
  BarChart3,
  SearchCode,
  Sparkles,
} from 'lucide-react'
import Dashboard from './pages/Dashboard'
import ForecastingPage from './pages/Forecasting'
import InventoryPage from './pages/Inventory'
import PricingPage from './pages/Pricing'
import PromotionsPage from './pages/Promotions'
import CopilotPage from './pages/Copilot'
import BIReportPage from './pages/BIReport'
import RCAPage from './pages/RCA'

function App() {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
    { to: '/forecasting', label: 'Demand Forecasting', icon: TrendingUp },
    { to: '/inventory', label: 'Inventory', icon: Warehouse },
    { to: '/pricing', label: 'Pricing Intelligence', icon: Tag },
    { to: '/promotions', label: 'Promotions', icon: Megaphone },
    { to: '/bi-report', label: 'Executive Report', icon: BarChart3 },
    { to: '/rca', label: 'Root Cause Analysis', icon: SearchCode },
    { to: '/copilot', label: 'AI Copilot', icon: Bot, highlight: true },
  ]

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <Link to="/" className="px-6 py-5 border-b border-gray-100 flex items-center gap-2">
          <div className="w-9 h-9 bg-gradient-to-br from-brand-500 to-brand-700 rounded-xl flex items-center justify-center text-white">
            <Sparkles size={20} />
          </div>
          <div>
            <div className="font-bold text-gray-900 text-lg leading-tight">MerchIq</div>
            <div className="text-[10px] text-gray-500 uppercase tracking-wide">Retail Intelligence</div>
          </div>
        </Link>

        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-brand-50 text-brand-700 shadow-sm'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                } ${item.highlight ? 'mt-2' : ''}`
              }
            >
              {item.highlight ? (
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-white">
                  <item.icon size={16} />
                </div>
              ) : (
                <item.icon size={18} />
              )}
              <span className="flex-1">{item.label}</span>
              {item.highlight && (
                <span className="text-[10px] px-1.5 py-0.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full">
                  AI
                </span>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-100">
          <div className="bg-gradient-to-br from-brand-50 to-indigo-50 rounded-xl p-4">
            <div className="text-xs font-semibold text-brand-700 mb-1">4 Retail Modules</div>
            <div className="text-[11px] text-gray-600 leading-snug mb-2">
              Forecasting · Inventory · Pricing · Promotions
            </div>
            <div className="flex -space-x-1">
              {['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'].map((c) => (
                <div key={c} className="w-5 h-5 rounded-full border-2 border-white" style={{ background: c }} />
              ))}
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 min-w-0 overflow-x-hidden">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/forecasting" element={<ForecastingPage />} />
          <Route path="/inventory" element={<InventoryPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/promotions" element={<PromotionsPage />} />
          <Route path="/bi-report" element={<BIReportPage />} />
          <Route path="/rca" element={<RCAPage />} />
          <Route path="/copilot" element={<CopilotPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
