export interface KPIData {
  total_revenue: number
  revenue_growth: number
  total_units_sold: number
  units_growth: number
  gross_margin: number
  margin_growth: number
  avg_order_value: number
  inventory_turnover: number
  stockout_rate: number
  promotion_roi: number
}

export interface Product {
  id: number
  sku: string
  name: string
  description?: string
  category_id?: number
  brand?: string
  unit: string
  cost_price: number
  base_price: number
  weight_kg?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface InventoryItem {
  id: number
  product_id: number
  store_id: number
  quantity_on_hand: number
  quantity_reserved: number
  quantity_on_order: number
  reorder_point: number
  reorder_quantity: number
  lead_time_days: number
  last_restock_date?: string
  expiry_date?: string
  updated_at: string
}

export interface InventoryOptimization {
  product_id: number
  product_name: string
  store_id: number
  current_stock: number
  reorder_point: number
  recommended_order: number
  safety_stock: number
  eoq: number
  stockout_risk: string
  holding_cost: number
  ordering_cost: number
  total_cost: number
}

export interface ForecastItemData {
  date: string
  predicted_value: number
  lower_bound?: number
  upper_bound?: number
}

export interface ForecastResponse {
  product_id: number
  product_name: string
  model_type: string
  horizon_days: number
  mape?: number
  rmse?: number
  predictions: ForecastItemData[]
  explanation?: string
}

export interface PricingRecommendation {
  product_id: number
  product_name: string
  current_price: number
  recommended_price: number
  price_elasticity: number
  expected_demand_change: number
  expected_revenue_change: number
  competitor_avg_price?: number
  margin_impact: number
  reasoning: string
}

export interface PromotionEffectiveness {
  promotion_id: number
  promotion_name: string
  incremental_revenue: number
  lift_percentage: number
  roi: number
  total_units_sold: number
  total_revenue: number
  cost_of_promotion: number
}

export interface RootCauseAnalysis {
  metric_name: string
  current_value: number
  expected_value: number
  deviation: number
  primary_causes: Array<{
    dimension: string
    factor: string
    contribution_pct: number
    evidence: string
    severity: string
  }>
  contributing_factors: Array<{
    dimension: string
    factor: string
    contribution_pct: number
    evidence: string
  }>
  recommendations: string[]
  confidence_score: number
}

export interface ExecutiveReport {
  report_period: string
  generated_at: string
  summary: string
  kpi_summary: KPIData
  top_performers: Array<{
    product_id: number
    product_name: string
    sku: string
    revenue: number
    units: number
    profit: number
    margin_pct: number
  }>
  underperformers: Array<{
    product_id: number
    product_name: string
    sku: string
    revenue: number
    units: number
    profit: number
    margin_pct: number
  }>
  key_insights: string[]
  recommendations: string[]
  risk_alerts: string[]
}

export interface CopilotQueryResponse {
  query_type: string
  answer: string
  data_points?: Array<Record<string, any>>
  chart_spec?: Record<string, any>
  related_insights?: string[]
  confidence_score: number
  sources_used: string[]
}

export interface ForecastExplainability {
  product_id: number
  key_drivers: Array<{ driver: string; impact_percent?: number; impact?: string }>
  seasonal_patterns: Array<{ pattern: string; type: string }>
  trend_direction: string
  confidence_level: number
  risk_factors: string[]
}
