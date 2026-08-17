import { Send, Sparkles, BrainCircuit, BarChart2, ChevronRight } from 'lucide-react'
import { useState } from 'react'
import type { CopilotQueryResponse } from '../../types'

interface Message {
  role: 'user' | 'assistant'
  content: string
  data?: any
  timestamp: Date
  sources?: string[]
  confidence?: number
}

const SUGGESTIONS = [
  { label: 'Show me the KPI dashboard', icon: '📊' },
  { label: 'Forecast demand for product 1 next 30 days', icon: '📈' },
  { label: 'Why did revenue drop? Run RCA', icon: '🔍' },
  { label: 'Generate monthly executive report', icon: '📋' },
  { label: 'What should we reorder?', icon: '📦' },
  { label: 'Recommend price for product 3', icon: '💰' },
  { label: 'Evaluate promotion 1 ROI', icon: '🎯' },
  { label: 'Plan next quarter strategy', icon: '🚀' },
]

function mockResponse(query: string): CopilotQueryResponse {
  const type = detectType(query)
  const map: Record<string, () => CopilotQueryResponse> = {
    kpi: () => ({
      query_type: 'kpi_analysis',
      answer: `**KPI Dashboard Overview**

**Revenue:** $1,247,832.56 — 📈 Growing (+8.4% vs prior period)
**Units Sold:** 48,216 — (+5.2%)
**Gross Margin:** 38.7% — 📈 Improving (+1.2pp)

**Operational Efficiency:**
- Average Order Value: $68.42
- Inventory Turnover: 5.4x (target: 4-8x)
- Stockout Rate: 2.8% (target: <3%) ✅
- Promotion ROI: 187.5% (target: >150%)

**Insight:** Strong quarter with revenue exceeding plan by $47K. Stockout rate is within acceptable range, but promotion ROI is trending below 200% target — consider optimizing flash sale discount depth next cycle.`,
      confidence_score: 0.94,
      sources_used: ['SQL: sales table', 'SQL: inventory table', 'SQL: products table'],
      data_points: [
        { metric: 'Revenue', value: '$1.248M', growth: '+8.4%' },
        { metric: 'Margin', value: '38.7%', growth: '+1.2pp' },
        { metric: 'Units', value: '48,216', growth: '+5.2%' },
      ],
    }),
    forecast: () => ({
      query_type: 'forecast_request',
      answer: `**30-Day Demand Forecast (Product #1 — Organic Whole Milk 1G) — PROPHET Model**

**Summary:**
- Total predicted units: **4,280** (range: 3,120 — 5,640)
- Average daily demand: **142.7 units**
- Model accuracy: MAPE 8.7% | RMSE 14.2

**Peak demand:** 220 units on 2026-09-06 (Saturday)
**Lowest demand:** 68 units on 2026-08-26 (Tuesday)

**Seasonality Pattern:**
- Weekend spike: +35% Sat/Sun vs weekday avg
- Monthly cycle: Week 2 of month historically strongest
- Explanation: Trend is INCREASING with 87% confidence. Key drivers: weekly seasonality (28%), promotion lift (22%), price sensitivity (15%).

🎯 Recommendation: Plan inventory with 95% confidence upper bound (5,640 units) to prevent stockouts. Schedule extra delivery for Fri before weekend peaks.`,
      confidence_score: 0.87,
      sources_used: ['ML: Prophet forecasting model', 'SQL: sales table (180d history)'],
    }),
    rca: () => ({
      query_type: 'root_cause_analysis',
      answer: `**🔍 Root Cause Analysis — TOTAL REVENUE**
Current: $1,247,832 | Expected: $1,287,450
Deviation: **-3.1%** | Confidence: 82%

**🎯 Primary Causes:**
1. [MEDIUM] **pricing** — Price elasticity impact (18.0% contribution)
   Evidence: Price correlation: -0.45
   📍 Category-wide 5% price increase 3w ago reduced volume on elastic SKUs (Avocado, Fresh Bread) by 7.2%.

2. [HIGH] **inventory** — Stock levels mismatch (26.3% contribution)
   Evidence: Inventory correlation: -0.52
   📍 12 critical A-class SKUs stockout 2-4 days in Northeast region. Estimated revenue leakage: $18.4K.

3. [MEDIUM] **promotions** — Promotion cannibalization (15.0% contribution)
   Evidence: Promotion correlation: 0.53
   📍 Flash Sale #3 cannibalized full-margin sales by 18.5% — net impact negative after accounting for discounted margin.

**📊 Contributing:**
- weather: -2.3% (unseasonably cool weather suppressed summer category demand)
- region: +1.4% (West Coast overperforming vs plan offsetting some Northeast losses)

**✅ Recommended Actions:**
1. Optimize replenishment schedules and increase safety stock for high-impact SKUs in Northeast
2. Roll back selective price increases on elastic SKUs (Avocado Hass, Sourdough) — test 2% decrease first
3. Next promotion: tighten category mix — remove cannibalized SKUs from promo eligibility`,
      confidence_score: 0.82,
      sources_used: ['6-dimension correlation engine', 'SQL: cross-table joins (inventory/pricing/promotions/region/weather/competitor)'],
    }),
    default: () => ({
      query_type: 'general_info',
      answer: `I've analyzed your question: **"${query}"**

I can help with:
- 📊 **KPI & Analytics:** Dashboard, trends, comparisons
- 📈 **Forecasting:** 7/30/90-day demand projections + explainability
- 📦 **Inventory:** EOQ, safety stock, PO suggestions, ABC analysis
- 💰 **Pricing:** Elasticity modeling, competitor-aware recommendations
- 🎯 **Promotions:** ROI analysis, cannibalization, campaign design
- 🔍 **RCA:** Root cause across all 6 business dimensions
- 📋 **Reports:** Executive summaries, board-ready outputs
- 🚀 **Planning:** AI-assisted quarterly & category strategies

Need specific data? Try: "Top 10 products" · "Promotion ROI" · "What's our stockout rate?"`,
      confidence_score: 0.9,
      sources_used: ['RAG knowledge base (8 articles)'],
    }),
  }
  return (map[type] ?? map.default)()
}

function detectType(q: string): string {
  const s = q.toLowerCase()
  if (/kpi|dashboard|revenue|margin|how (are|do) we|total/.test(s)) return 'kpi'
  if (/forecast|predict|demand|projection|how many.*sell/.test(s)) return 'forecast'
  if (/root cause|why.*(drop|decline|decrease)|diagnose|investigate|rca/.test(s)) return 'rca'
  if (/executive|report|summary/.test(s)) return 'kpi'
  return 'default'
}

export default function CopilotChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `👋 **Welcome to MerchIq AI Retail Copilot!**

I'm your AI retail intelligence assistant powered by LangGraph + RAG + LLM reasoning across 6 business dimensions.

Ask me anything like:
- "Show me the KPI dashboard"
- "Why did revenue drop?" (root cause analysis)
- "Forecast demand for product 1 next 30 days"
- "Recommend optimal price for product 3"
- "Optimize our purchase orders"
- "Generate monthly executive report"

Or pick a suggestion below to get started 👇`,
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const send = async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || loading) return
    const userMsg: Message = { role: 'user', content: trimmed, timestamp: new Date() }
    setMessages((m) => [...m, userMsg])
    setInput('')
    setLoading(true)
    await new Promise((r) => setTimeout(r, 900 + Math.random() * 800))
    const r = mockResponse(trimmed)
    setMessages((m) => [
      ...m,
      {
        role: 'assistant',
        content: r.answer,
        data: r.data_points,
        sources: r.sources_used,
        confidence: r.confidence_score,
        timestamp: new Date(),
      },
    ])
    setLoading(false)
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 via-white to-indigo-50/30 rounded-2xl border border-gray-100 overflow-hidden">
      <div className="px-5 py-4 bg-white/70 backdrop-blur border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-500 via-pink-500 to-rose-500 flex items-center justify-center text-white shadow-lg shadow-purple-200/50">
            <BrainCircuit size={20} />
          </div>
          <div>
            <div className="font-bold text-gray-900 flex items-center gap-2">
              AI Retail Copilot
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold uppercase tracking-wide">
                Pro
              </span>
            </div>
            <div className="text-xs text-gray-500 flex items-center gap-1.5">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Online · 10+ query types · RAG-enhanced
            </div>
          </div>
        </div>
        <button className="btn-secondary !py-1.5 !text-xs gap-1.5">
          <BarChart2 size={13} /> View knowledge base
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-4 min-h-0">
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
        {loading && (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white flex-shrink-0">
              <Sparkles size={14} />
            </div>
            <div className="bg-white rounded-2xl rounded-tl-md border border-gray-100 px-4 py-3 shadow-sm">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }} />
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {messages.length <= 1 && (
        <div className="px-5 pb-3">
          <div className="text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
            <Sparkles size={11} /> Suggested prompts
          </div>
          <div className="grid grid-cols-2 gap-2">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                onClick={() => send(s.label)}
                className="text-left text-xs p-2.5 rounded-xl bg-white border border-gray-100 hover:border-brand-200 hover:bg-brand-50/50 transition-all group flex items-center gap-2"
              >
                <span>{s.icon}</span>
                <span className="text-gray-700 group-hover:text-brand-700 line-clamp-2">{s.label}</span>
                <ChevronRight size={12} className="ml-auto text-gray-300 group-hover:text-brand-500" />
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="p-4 bg-white/80 backdrop-blur border-t border-gray-100">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            send(input)
          }}
          className="flex items-center gap-2 bg-white rounded-xl border border-gray-200 focus-within:ring-2 focus-within:ring-brand-300 focus-within:border-brand-300 transition-all shadow-sm"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about your retail business... (e.g. 'Why did revenue drop?')"
            className="flex-1 px-4 py-2.5 bg-transparent text-sm focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="m-1.5 inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-700 hover:to-indigo-700 text-white text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            <Send size={14} />
            Send
          </button>
        </form>
        <div className="flex items-center justify-between mt-2 text-[11px] text-gray-400 px-1">
          <span>Supports: KPI · Forecast · RCA · Inventory · Pricing · Promotions · Reports · Planning</span>
          <span className="flex items-center gap-1.5">
            <BrainCircuit size={11} />
            Data-driven · 6-dim context · SQL + Prophet + XGBoost + LLM
          </span>
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-white shadow-sm ${
          isUser ? 'bg-gradient-to-br from-gray-600 to-gray-800' : 'bg-gradient-to-br from-purple-500 to-pink-500'
        }`}
      >
        {isUser ? 'You'[0] : <Sparkles size={14} />}
      </div>
      <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div
          className={`px-4 py-3 rounded-2xl border shadow-sm whitespace-pre-wrap ${
            isUser
              ? 'bg-gradient-to-br from-brand-600 to-indigo-600 text-white rounded-tr-md border-transparent'
              : 'bg-white text-gray-800 rounded-tl-md border-gray-100'
          }`}
          style={{ fontSize: '14px', lineHeight: 1.6 }}
        >
          {renderMarkdown(message.content)}
        </div>

        {message.data && message.data.length > 0 && (
          <div className="mt-2 grid grid-cols-3 gap-2 w-full">
            {message.data.slice(0, 3).map((d: any, i: number) => (
              <div key={i} className="p-2.5 bg-white rounded-lg border border-gray-100 shadow-sm">
                <div className="text-[10px] text-gray-500 uppercase tracking-wide font-semibold">{d.metric}</div>
                <div className="text-base font-bold text-gray-900 mt-0.5">{d.value}</div>
                {d.growth && <div className="text-[11px] text-emerald-600 font-medium">{d.growth}</div>}
              </div>
            ))}
          </div>
        )}

        <div className="flex items-center gap-3 mt-1.5 px-1 text-[10px] text-gray-400 flex-wrap">
          <span>{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          {!isUser && message.confidence != null && (
            <span className="inline-flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Confidence: {(message.confidence * 100).toFixed(0)}%
            </span>
          )}
          {!isUser && message.sources && (
            <span className="truncate max-w-[300px]">
              Sources: {message.sources.join(' · ')}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

function renderMarkdown(text: string) {
  const lines = text.split('\n')
  return lines.map((line, i) => {
    let l = line
    l = l.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    l = l.replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 rounded bg-gray-100 text-[12px] font-mono">$1</code>')
    if (/^\d+\.\s/.test(l)) {
      return <div key={i} className="ml-4" dangerouslySetInnerHTML={{ __html: l }} />
    }
    if (/^-\s/.test(l)) {
      return <div key={i} className="ml-4" dangerouslySetInnerHTML={{ __html: '• ' + l.slice(2) }} />
    }
    if (/^🎯|^📊|^📈|^💰|^✅|^⚠️|^📦|^🔍|^📋|^🚀|^📝|^⭐|^📍|^📅|^🧠|^✨|^👋/.test(l)) {
      return <div key={i} className="mt-1" dangerouslySetInnerHTML={{ __html: l }} />
    }
    return <div key={i} dangerouslySetInnerHTML={{ __html: l || '&nbsp;' }} />
  })
}
