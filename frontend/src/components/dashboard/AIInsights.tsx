import { TriangleAlert, CheckCircle2, AlertTriangle, Info, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

interface InsightItem {
  type: 'success' | 'warning' | 'danger' | 'info'
  title: string
  detail: string
  link?: { to: string; label: string }
}

function generateInsights(): InsightItem[] {
  return [
    {
      type: 'success',
      title: 'Revenue growth +8.4% exceeding 5% target',
      detail: 'Driven by strong performance in Avocado and Dairy categories (+14% vs plan).',
      link: { to: '/bi-report', label: 'View full report' },
    },
    {
      type: 'warning',
      title: '28 SKUs flagged for reorder',
      detail: '3 at critical stockout risk in the Northeast region. Review purchase suggestions.',
      link: { to: '/inventory', label: 'Optimize inventory' },
    },
    {
      type: 'danger',
      title: 'Promotion ROI at 187% below 200% target',
      detail: 'Summer Flash Sale #3 showing cannibalization of 18.5% — reassess discount depth.',
      link: { to: '/rca', label: 'Run RCA' },
    },
    {
      type: 'info',
      title: 'New price recommendations ready',
      detail: '14 SKUs with +2-4% margin upside via pricing AI — review before Friday price change.',
      link: { to: '/pricing', label: 'Review prices' },
    },
  ]
}

const iconMap = {
  success: CheckCircle2,
  warning: AlertTriangle,
  danger: TriangleAlert,
  info: Info,
}

const colorMap: Record<string, string> = {
  success: 'bg-emerald-50 border-emerald-100 text-emerald-700',
  warning: 'bg-amber-50 border-amber-100 text-amber-700',
  danger: 'bg-red-50 border-red-100 text-red-700',
  info: 'bg-brand-50 border-brand-100 text-brand-700',
}

export default function AIInsights() {
  const insights = generateInsights()
  return (
    <div className="card h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <span className="text-lg">🧠</span> AI Business Insights
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">6-dimension correlation engine · generated 3m ago</p>
        </div>
        <Link to="/copilot" className="text-xs font-medium text-brand-600 hover:text-brand-700 flex items-center gap-1">
          Ask AI Copilot <ArrowRight size={12} />
        </Link>
      </div>
      <div className="space-y-3">
        {insights.map((item, i) => {
          const Icon = iconMap[item.type]
          return (
            <div
              key={i}
              className={`p-3 rounded-lg border ${colorMap[item.type]} transition-all hover:shadow-sm`}
            >
              <div className="flex gap-3">
                <Icon size={18} className="mt-0.5 flex-shrink-0" />
                <div className="min-w-0 flex-1">
                  <div className="font-semibold text-sm leading-snug">{item.title}</div>
                  <div className="text-xs mt-1 opacity-80 leading-relaxed">{item.detail}</div>
                  {item.link && (
                    <Link
                      to={item.link.to}
                      className="inline-flex items-center gap-1 text-[11px] font-semibold mt-2 hover:underline"
                    >
                      {item.link.label} <ArrowRight size={10} />
                    </Link>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
