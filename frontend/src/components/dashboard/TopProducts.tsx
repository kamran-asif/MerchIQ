import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from 'recharts'
import { formatCurrency, formatNumber } from '../../utils'

interface TopProductsProps {
  data?: Array<{ product_name: string; revenue: number; units: number; margin_pct: number }>
}

function generateMockProducts() {
  return [
    { product_name: 'Organic Whole Milk 1G', revenue: 42318, units: 8412, margin_pct: 32.1 },
    { product_name: 'Avocado Hass Premium', revenue: 38914, units: 15210, margin_pct: 41.5 },
    { product_name: 'Sourdough Artisan Loaf', revenue: 32109, units: 10256, margin_pct: 56.2 },
    { product_name: 'Free-Range Eggs Doz', revenue: 28550, units: 7420, margin_pct: 28.7 },
    { product_name: 'Grass Fed Beef 1lb', revenue: 24802, units: 3980, margin_pct: 34.8 },
    { product_name: 'Fresh Atlantic Salmon', revenue: 22145, units: 1654, margin_pct: 29.1 },
    { product_name: 'Greek Yogurt Plain', revenue: 19875, units: 6625, margin_pct: 39.4 },
    { product_name: 'Organic Baby Spinach', revenue: 17421, units: 9280, margin_pct: 47.8 },
  ]
}

export default function TopProducts({ data }: TopProductsProps) {
  const products = data ?? generateMockProducts()

  return (
    <div className="card h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-gray-900">Top Products by Revenue</h3>
          <p className="text-xs text-gray-500 mt-0.5">Last 30 days performance</p>
        </div>
      </div>
      <div className="space-y-2.5">
        {products.slice(0, 6).map((p, idx) => {
          const max = products[0].revenue
          const pct = (p.revenue / max) * 100
          return (
            <div key={idx}>
              <div className="flex items-center justify-between text-sm mb-1">
                <div className="font-medium text-gray-800 truncate max-w-[60%]">{p.product_name}</div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-500">{formatNumber(p.units)} units</span>
                  <span className="font-semibold text-gray-900">{formatCurrency(p.revenue)}</span>
                </div>
              </div>
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-brand-400 to-brand-600"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <div className="flex justify-between mt-1 text-[10px] text-gray-500">
                <span>Margin: <span className="font-medium text-emerald-600">{p.margin_pct.toFixed(1)}%</span></span>
                <span>{pct.toFixed(0)}% of top</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
