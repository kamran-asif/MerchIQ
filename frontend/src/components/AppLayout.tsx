import { Outlet, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  TrendingUp,
  Package,
  Tag,
  Percent,
  Search,
  Bot,
  BarChart3,
  Menu,
  X,
  Store,
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '../utils'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/forecasting', label: 'Demand Forecasting', icon: TrendingUp },
  { to: '/inventory', label: 'Inventory', icon: Package },
  { to: '/pricing', label: 'Pricing Intelligence', icon: Tag },
  { to: '/promotions', label: 'Promotion Analytics', icon: Percent },
  { to: '/bi', label: 'BI & RCA Engine', icon: BarChart3 },
  { to: '/copilot', label: 'AI Retail Copilot', icon: Bot },
  { to: '/stores', label: 'Stores & Regions', icon: Store },
]

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside
        className={cn(
          'fixed lg:relative inset-y-0 left-0 z-40 bg-white border-r border-gray-200 transition-all duration-300 flex flex-col',
          sidebarOpen ? 'w-64' : 'w-20'
        )}
      >
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-100">
          <div className={cn('flex items-center gap-2', !sidebarOpen && 'justify-center w-full')}>
            <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
              <Search size={16} className="text-white" />
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="font-bold text-gray-900 text-sm leading-tight">MerchIq</h1>
                <p className="text-xs text-gray-500 leading-tight">Retail Analytics</p>
              </div>
            )}
          </div>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hidden lg:flex p-1 rounded hover:bg-gray-100 text-gray-500"
          >
            {sidebarOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => {
            const active = location.pathname === to
            return (
              <NavLink
                key={to}
                to={to}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  sidebarOpen ? 'justify-start' : 'justify-center',
                  active
                    ? 'bg-brand-50 text-brand-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
                title={label}
              >
                <Icon size={18} className="flex-shrink-0" />
                {sidebarOpen && <span>{label}</span>}
              </NavLink>
            )
          })}
        </nav>

        {sidebarOpen && (
          <div className="p-4 border-t border-gray-100">
            <div className="rounded-lg bg-gradient-to-br from-brand-50 to-brand-100 p-4">
              <p className="text-xs font-semibold text-brand-700 mb-1">Platform Modules</p>
              <p className="text-xs text-gray-600 mb-2">
                5 microservices • 12+ APIs • Event-driven
              </p>
              <div className="flex gap-1 flex-wrap">
                {['Prophet', 'XGBoost', 'LangGraph', 'RAG'].map(t => (
                  <span key={t} className="text-[10px] bg-white/60 text-brand-700 rounded px-1.5 py-0.5 font-medium">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-30">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 capitalize">
              {NAV_ITEMS.find(n => n.to === location.pathname)?.label || 'Dashboard'}
            </h2>
            <p className="text-xs text-gray-500">AI-powered Retail Planning Intelligence</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="tag bg-green-50 text-green-700 border border-green-200">
              ● Live Demo
            </span>
          </div>
        </header>

        <main className="flex-1 p-6 overflow-x-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
