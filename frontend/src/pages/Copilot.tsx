import CopilotChat from '../components/copilot/CopilotChat'

export default function CopilotPage() {
  return (
    <div className="min-h-screen p-6 flex flex-col" style={{ height: 'calc(100vh - 0px)' }}>
      <div className="px-2 pb-4 flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Retail Copilot</h1>
          <p className="text-sm text-gray-500 mt-1">10+ natural language query types · LangGraph + RAG · LLM reasoning across 6 business dimensions</p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-[11px]">
          {['KPI Analysis', 'Forecast Explainability', 'Root Cause', 'Executive Reports', 'Inventory', 'Pricing', 'Promotions', 'AI Planning'].map((t) => (
            <span key={t} className="px-2.5 py-1 rounded-full bg-white border border-gray-200 text-gray-600 font-medium">
              ✓ {t}
            </span>
          ))}
        </div>
      </div>
      <div className="flex-1 min-h-0">
        <CopilotChat />
      </div>
    </div>
  )
}
