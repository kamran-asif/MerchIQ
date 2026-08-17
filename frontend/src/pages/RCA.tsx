import { useEffect, useState } from 'react'
import { kpiApi } from '../services/api'
import type { RootCauseAnalysis } from '../types'
import { SearchCode, AlertTriangle, ArrowRight, Lightbulb } from 'lucide-react'

function mockRCA(): RootCauseAnalysis {
  return {
    metric_name: 'Total Revenue',
    current_value: 1247832,
    expected_value: 1287450,
    deviation: -3.1,
    primary_causes: [
      { dimension: 'inventory', factor: 'Stock levels mismatch — 12 critical A-class SKUs in Northeast region', contribution_pct: 26.3, evidence: 'Inventory correlation: -0.52', severity: 'high' },
      { dimension: 'pricing', factor: 'Price elasticity impact — Category-wide 5% price increase reduced volume on elastic SKUs', contribution_pct: 18.0, evidence: 'Price correlation: -0.45', severity: 'medium' },
      { dimension: 'promotions', factor: 'Promotion cannibalization — Flash Sale #3 stole full-margin sales', contribution_pct: 15.0, evidence: 'Promotion correlation: 0.53', severity: 'medium' },
    ],
    contributing_factors: [
      { dimension: 'weather', factor: 'Unseasonably cool weather suppressed summer category demand', contribution_pct: 11.5, evidence: 'Weather correlation: 0.32' },
      { dimension: 'region', factor: 'Northeast underperforming (7-day stockouts avg) offset by West Coast overperformance', contribution_pct: 9.8, evidence: 'Regional std dev: 0.42' },
      { dimension: 'competitor', factor: 'Rival MegaMart matching +10% stocking competing private label', contribution_pct: 8.2, evidence: 'Competitor activity: -0.34 correlation' },
    ],
    recommendations: [
      'Optimize replenishment schedules and increase safety stock by 20% for A-class SKUs in Northeast region',
      'Roll back selective price increases on elastic SKUs (Avocado Hass, Sourdough) — test 2% decrease first',
      'Next promotion: tighten category mix — remove cannibalized SKUs (Frozen Pizza, White Bread) from promo eligibility',
      'Test weather-informed merchandising: warm-weather endcap display rotation based on 10-day forecast',
    ],
    confidence_score: 0.82,
  }
}

export default function RCAPage() {
  const [metric, setMetric] = useState('revenue')
  const [rca, setRca] = useState<RootCauseAnalysis | null>(null)
  const [loading, setLoading] = useState(false)

  const run = async (m: string) => {
    setLoading(true)
    setMetric(m)
    await new Promise((r) => setTimeout(r, 700))
    try {
      const r = await kpiApi.runRCA(m)
      setRca(r)
    } catch {
      setRca(mockRCA())
    }
    setLoading(false)
  }

  useEffect(() => { run('revenue') }, [])

  const r = rca ?? mockRCA()

  const metrics = [
    { id: 'revenue', label: 'Revenue' },
    { id: 'gross_margin', label: 'Gross Margin' },
    { id: 'units_sold', label: 'Units Sold' },
    { id: 'inventory_turnover', label: 'Inventory Turnover' },
    { id: 'stockout_rate', label: 'Stockout Rate' },
    { id: 'avg_order_value', label: 'Avg Order Value' },
  ]

  return (
    <div className="min-h-screen">
      <div className="px-8 pt-6 pb-5">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2.5">
          <SearchCode className="text-brand-600" /> Root Cause Analysis
        </h1>
        <p className="text-sm text-gray-500 mt-1">6-dimension correlation engine · Inventory · Pricing · Promotions · Region · Weather · Competitor</p>
      </div>

      <div className="px-8 pb-8">
        <div className="card mb-6">
          <div className="flex flex-wrap items-center gap-3">
            <div className="text-sm font-semibold text-gray-600">Analyze metric:</div>
            <div className="flex flex-wrap gap-2">
              {metrics.map((m) => (
                <button
                  key={m.id}
                  onClick={() => run(m.id)}
                  disabled={loading}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all disabled:opacity-50 ${
                    metric === m.id
                      ? 'bg-gradient-to-r from-brand-600 to-indigo-600 text-white shadow-sm'
                      : 'bg-white border border-gray-200 text-gray-700 hover:border-brand-200 hover:bg-brand-50/50'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
            {loading && <div className="text-xs text-brand-600 font-medium animate-pulse ml-auto">🧠 Correlating 6 dimensions...</div>}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="p-4 rounded-xl bg-white border border-gray-100">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Metric</div>
            <div className="text-lg font-bold text-gray-900 mt-1">{r.metric_name}</div>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-100">
            <div className="text-xs font-semibold text-emerald-700 uppercase tracking-wide">Current Value</div>
            <div className="text-lg font-bold text-gray-900 mt-1">${r.current_value.toLocaleString()}</div>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-br from-amber-50 to-orange-50 border-amber-100">
            <div className="text-xs font-semibold text-amber-700 uppercase tracking-wide">Expected (Baseline)</div>
            <div className="text-lg font-bold text-gray-900 mt-1">${r.expected_value.toLocaleString()}</div>
          </div>
          <div className={`p-4 rounded-xl border ${r.deviation < 0 ? 'bg-gradient-to-br from-red-50 to-rose-50 border-red-100' : 'bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-100'}`}>
            <div className={`text-xs font-semibold uppercase tracking-wide flex items-center gap-1 ${r.deviation < 0 ? 'text-red-700' : 'text-emerald-700'}`}>
              <AlertTriangle size={12} /> Deviation
            </div>
            <div className={`text-2xl font-bold mt-1 ${r.deviation < 0 ? 'text-red-700' : 'text-emerald-700'}`}>
              {r.deviation > 0 ? '+' : ''}{r.deviation.toFixed(1)}%
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span className="text-base">🎯</span> Primary Causes ({r.primary_causes.length})
            </h3>
            <div className="space-y-3">
              {r.primary_causes.map((c, i) => (
                <div key={i} className={`p-4 rounded-xl border ${
                  c.severity === 'high' ? 'bg-red-50/70 border-red-100' : 'bg-amber-50/70 border-amber-100'
                }`}>
                  <div className="flex items-start justify-between gap-3 flex-wrap">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        <span className={`text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded ${
                          c.severity === 'high' ? 'bg-red-200 text-red-800' : 'bg-amber-200 text-amber-800'
                        }`}>{c.severity.toUpperCase()}</span>
                        <span className="text-xs font-semibold capitalize text-brand-700 bg-brand-50 px-2 py-0.5 rounded">{c.dimension}</span>
                        <span className="text-xs text-gray-500">{c.evidence}</span>
                      </div>
                      <div className="text-sm font-medium text-gray-900 leading-snug">{c.factor}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] uppercase text-gray-500 tracking-wide">Contribution</div>
                      <div className={`text-xl font-bold ${c.severity === 'high' ? 'text-red-700' : 'text-amber-700'}`}>{c.contribution_pct.toFixed(1)}%</div>
                    </div>
                  </div>
                  <div className="mt-3 h-1.5 bg-white/80 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${
                      c.severity === 'high' ? 'bg-gradient-to-r from-red-400 to-red-600' : 'bg-gradient-to-r from-amber-400 to-orange-500'
                    }`} style={{ width: `${Math.min(100, c.contribution_pct * 2)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span className="text-base">🔗</span> Contributing Factors ({r.contributing_factors.length})
            </h3>
            <div className="space-y-3">
              {r.contributing_factors.map((c, i) => (
                <div key={i} className="p-3.5 rounded-xl bg-gray-50 border border-gray-100">
                  <div className="flex items-start justify-between gap-3 flex-wrap">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="text-xs font-semibold capitalize text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">{c.dimension}</span>
                        <span className="text-[11px] text-gray-500">{c.evidence}</span>
                      </div>
                      <div className="text-sm text-gray-800 leading-snug">{c.factor}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] uppercase text-gray-500 tracking-wide">Impact</div>
                      <div className="text-base font-bold text-indigo-700">{c.contribution_pct.toFixed(1)}%</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-emerald-50/70 via-teal-50/70 to-brand-50/70 border-brand-100">
          <div className="flex items-start justify-between mb-4 flex-wrap gap-3">
            <div>
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <Lightbulb className="text-amber-500" size={18} />
                AI-Generated Recommendations
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">Prioritized by impact × feasibility · Confidence score: {(r.confidence_score * 100).toFixed(0)}%</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-600 rounded-full" style={{ width: `${r.confidence_score * 100}%` }} />
              </div>
              <span className="text-xs font-bold text-emerald-700">{(r.confidence_score * 100).toFixed(0)}%</span>
            </div>
          </div>
          <ol className="space-y-2.5">
            {r.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-3 p-3 rounded-xl bg-white/80 backdrop-blur border border-white shadow-sm">
                <div className="w-7 h-7 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white flex items-center justify-center font-bold text-sm flex-shrink-0 shadow-sm">
                  {i + 1}
                </div>
                <div className="flex-1 min-w-0 text-sm text-gray-800 leading-relaxed pt-0.5">{rec}</div>
                <ArrowRight size={14} className="text-gray-300 mt-1 flex-shrink-0" />
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  )
}
