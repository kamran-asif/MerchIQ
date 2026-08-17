import { ArrowUpDown, Search, Filter, ShoppingCart, Download } from 'lucide-react'
import type { InventoryOptimization } from '../../types'
import { formatCurrency, formatNumber, getRiskBadgeColor } from '../../utils'

interface Props {
  items?: InventoryOptimization[]
}

function mock(): InventoryOptimization[] {
  const names = [
    'Organic Whole Milk 1G', 'Avocado Hass Premium', 'Sourdough Artisan Loaf',
    'Free-Range Eggs Doz', 'Grass Fed Beef 1lb', 'Fresh Atlantic Salmon',
    'Greek Yogurt Plain 32oz', 'Organic Baby Spinach', 'Almond Milk Unsweet',
    'Chicken Breast Boneless', 'Pasta Marinara Sauce', 'Blueberries 6oz',
    'Cheddar Block Sharp', 'Orange Juice Pulp Free', 'Peanut Butter Crunchy',
  ]
  return names.map((n, i) => {
    const current = Math.round(5 + Math.random() * 80)
    const reorder = Math.round(15 + Math.random() * 25)
    const safety = Math.round(8 + Math.random() * 15)
    const recommended = current < reorder ? Math.round(20 + Math.random() * 60) : 0
    const risks = ['low', 'medium', 'high', 'critical', 'overstocked'] as const
    const risk = risks[i % risks.length]
    return {
      product_id: i + 1,
      product_name: n,
      store_id: 1,
      current_stock: current,
      reorder_point: reorder,
      recommended_order: recommended,
      safety_stock: safety,
      eoq: Math.round(30 + Math.random() * 50),
      stockout_risk: risk,
      holding_cost: round(current * 1.2),
      ordering_cost: round(45 + Math.random() * 30),
      total_cost: round(current * 1.2 + 60 + Math.random() * 40),
    }
  })
}

const round = (n: number) => Math.round(n * 100) / 100

export default function InventoryOptimizationTable({ items }: Props) {
  const data = items ?? mock()
  const totalOrderCost = data.reduce((a, b) => a + b.recommended_order * 3.5, 0)
  const critical = data.filter((d) => ['critical', 'high'].includes(d.stockout_risk)).length

  return (
    <div className="card">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="font-semibold text-gray-900">Inventory Optimization</h3>
          <p className="text-xs text-gray-500 mt-0.5">EOQ + Safety Stock + ABC analysis · Auto-generated PO suggestions</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input placeholder="Search SKU..." className="pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-300 w-44" />
          </div>
          <button className="btn-secondary !py-1.5 !text-xs gap-1.5"><Filter size={14} /> Filters</button>
          <button className="btn-primary !py-1.5 !text-xs gap-1.5"><ShoppingCart size={14} /> Create PO (${formatNumber(totalOrderCost, 0)})</button>
        </div>
      </div>

      <div className="flex gap-3 mb-4 flex-wrap">
        <div className="px-3 py-2 bg-red-50 border border-red-100 rounded-lg">
          <div className="text-[10px] uppercase tracking-wide text-red-600 font-semibold">At Risk</div>
          <div className="font-bold text-red-700">{critical} SKUs</div>
        </div>
        <div className="px-3 py-2 bg-amber-50 border border-amber-100 rounded-lg">
          <div className="text-[10px] uppercase tracking-wide text-amber-600 font-semibold">Reorder Qty</div>
          <div className="font-bold text-amber-700">{formatNumber(data.reduce((a, b) => a + b.recommended_order, 0))} units</div>
        </div>
        <div className="px-3 py-2 bg-emerald-50 border border-emerald-100 rounded-lg">
          <div className="text-[10px] uppercase tracking-wide text-emerald-600 font-semibold">Est. PO Cost</div>
          <div className="font-bold text-emerald-700">{formatCurrency(totalOrderCost)}</div>
        </div>
        <div className="px-3 py-2 bg-purple-50 border border-purple-100 rounded-lg">
          <div className="text-[10px] uppercase tracking-wide text-purple-600 font-semibold">Overstocked</div>
          <div className="font-bold text-purple-700">{data.filter((d) => d.stockout_risk === 'overstocked').length} SKUs</div>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-gray-100">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-100 text-left">
              <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide">
                <span className="inline-flex items-center gap-1">Product <ArrowUpDown size={12} /></span>
              </th>
              <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">On Hand</th>
              <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">Reorder Pt</th>
              <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">Safety</th>
              <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">EOQ</th>
              <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">Rec. Order</th>
              <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-right">Mo. Cost</th>
              <th className="px-4 py-2.5 text-xs font-semibold text-gray-600 uppercase tracking-wide text-center">Risk</th>
            </tr>
          </thead>
          <tbody>
            {data.slice(0, 12).map((item, i) => (
              <tr key={i} className="border-b border-gray-50 hover:bg-gray-50/70 transition-colors">
                <td className="px-4 py-3">
                  <div className="font-medium text-gray-900">{item.product_name}</div>
                  <div className="text-[11px] text-gray-500">SKU #{item.product_id.toString().padStart(5, '0')}</div>
                </td>
                <td className="px-4 py-3 text-right">
                  <span className={`font-semibold ${item.current_stock < item.reorder_point ? 'text-red-600' : 'text-gray-900'}`}>
                    {formatNumber(item.current_stock)}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-gray-600">{formatNumber(item.reorder_point)}</td>
                <td className="px-4 py-3 text-right text-gray-600">{formatNumber(item.safety_stock)}</td>
                <td className="px-4 py-3 text-right text-gray-600">{formatNumber(item.eoq)}</td>
                <td className="px-4 py-3 text-right">
                  <span className={`font-bold ${item.recommended_order > 0 ? 'text-brand-600' : 'text-gray-400'}`}>
                    {item.recommended_order > 0 ? formatNumber(item.recommended_order) : '—'}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-gray-700 font-medium">{formatCurrency(item.total_cost)}</td>
                <td className="px-4 py-3 text-center">
                  <span className={`tag ${getRiskBadgeColor(item.stockout_risk)}`}>
                    {item.stockout_risk}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
