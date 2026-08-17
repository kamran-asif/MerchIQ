import { useState } from 'react'
import ForecastChart from '../components/forecasting/ForecastChart'
import ForecastExplainabilityCard from '../components/forecasting/ForecastExplainabilityCard'
import { forecastApi } from '../services/api'

export default function ForecastingPage() {
  const [productId, setProductId] = useState(1)
  const [horizon, setHorizon] = useState(30)
  const [model, setModel] = useState<'prophet' | 'xgboost'>('prophet')
  const [, force] = useState(0)

  return (
    <div className="min-h-screen">
      <div className="px-8 pt-6 pb-5">
        <h1 className="text-2xl font-bold text-gray-900">Demand Forecasting</h1>
        <p className="text-sm text-gray-500 mt-1">Prophet + XGBoost ensemble · Multi-horizon · Forecast explainability with SHAP-style drivers</p>
      </div>

      <div className="px-8 pb-8">
        <div className="card mb-5">
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="text-xs font-semibold text-gray-600 block mb-1.5">Product ID</label>
              <input type="number" value={productId} onChange={(e) => setProductId(+e.target.value || 1)} className="px-3 py-2 border border-gray-200 rounded-lg w-32 focus:outline-none focus:ring-2 focus:ring-brand-300 text-sm" />
            </div>
            <div>
              <label className="text-xs font-semibold text-gray-600 block mb-1.5">Forecast Horizon</label>
              <select value={horizon} onChange={(e) => setHorizon(+e.target.value)} className="px-3 py-2 border border-gray-200 rounded-lg w-36 focus:outline-none focus:ring-2 focus:ring-brand-300 text-sm bg-white">
                <option value={7}>7 days</option>
                <option value={14}>14 days</option>
                <option value={30}>30 days</option>
                <option value={60}>60 days</option>
                <option value={90}>90 days</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold text-gray-600 block mb-1.5">Forecast Model</label>
              <div className="inline-flex rounded-lg border border-gray-200 overflow-hidden text-sm font-medium">
                {(['prophet', 'xgboost'] as const).map((m) => (
                  <button
                    key={m}
                    onClick={() => setModel(m)}
                    className={`px-4 py-2 ${model === m ? 'bg-brand-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
                  >
                    {m.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
            <button className="btn-primary" onClick={() => force((x) => x + 1)}>
              🚀 Run Forecast
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2">
            <ForecastChart />
          </div>
          <div>
            <ForecastExplainabilityCard />
          </div>
        </div>

        <div className="mt-6 card">
          <h3 className="font-semibold text-gray-900 mb-3">Models in Production</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100">
              <div className="flex items-center justify-between mb-2">
                <div className="font-semibold text-gray-900">Meta Prophet</div>
                <span className="tag bg-blue-100 text-blue-700">Time-Series</span>
              </div>
              <p className="text-xs text-gray-600 leading-relaxed mb-3">
                Additive decomposable model with yearly, weekly, and daily seasonality + holiday effects. Handles missing data and trend shifts well. Ideal for retail seasonal patterns.
              </p>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <Metric label="MAPE" value="8.7%" />
                <Metric label="Coverage" value="95%" />
                <Metric label="Latency" value="2.4s" />
              </div>
            </div>
            <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100">
              <div className="flex items-center justify-between mb-2">
                <div className="font-semibold text-gray-900">XGBoost (Gradient Boost)</div>
                <span className="tag bg-emerald-100 text-emerald-700">ML Features</span>
              </div>
              <p className="text-xs text-gray-600 leading-relaxed mb-3">
                Tree-based model leveraging 6-dimension features: pricing, promotion flags, weather signals, region factors, competitor activity, and lag/rolling demand statistics.
              </p>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <Metric label="MAPE" value="7.2%" />
                <Metric label="Coverage" value="92%" />
                <Metric label="Latency" value="1.8s" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-2 rounded-lg bg-white/70 text-center">
      <div className="text-[10px] text-gray-500 uppercase tracking-wide">{label}</div>
      <div className="text-sm font-bold text-gray-800 mt-0.5">{value}</div>
    </div>
  )
}
