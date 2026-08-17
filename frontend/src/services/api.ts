import axios from 'axios'

const API_BASE = '/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const kpiApi = {
  getDashboard: (regionId?: number, storeId?: number) =>
    api.get('/kpis', { params: { region_id: regionId, store_id: storeId } }).then(r => r.data),
  getSalesTrend: (granularity = 'daily', days = 90) =>
    api.get('/sales-trend', { params: { granularity, days } }).then(r => r.data),
  getExecutiveReport: (period = 'monthly', regionId?: number) =>
    api.get('/executive-report', { params: { period, region_id: regionId } }).then(r => r.data),
  runRCA: (metric: string, regionId?: number, storeId?: number) =>
    api.post('/root-cause-analysis', null, { params: { metric, region_id: regionId, store_id: storeId } }).then(r => r.data),
  getMultiDimAnalysis: (metric = 'revenue', startDate?: string, endDate?: string) =>
    api.get('/multi-dimension-analysis', { params: { metric, start_date: startDate, end_date: endDate } }).then(r => r.data),
}

export const productApi = {
  list: (skip = 0, limit = 100) =>
    api.get('/products', { params: { skip, limit } }).then(r => r.data),
  get: (id: number) => api.get(`/products/${id}`).then(r => r.data),
  create: (data: any) => api.post('/products', data).then(r => r.data),
  listCategories: () => api.get('/categories').then(r => r.data),
}

export const forecastApi = {
  create: (productId: number, horizonDays = 30, modelType = 'prophet', regionId?: number) =>
    api.post('/forecast', {
      product_id: productId,
      horizon_days: horizonDays,
      model_type: modelType,
      region_id: regionId,
    }).then(r => r.data),
  explainability: (productId: number, modelType = 'prophet') =>
    api.get(`/products/${productId}/forecast-explainability`, { params: { model_type: modelType } }).then(r => r.data),
  history: (productId: number) =>
    api.get(`/forecasts/${productId}/history`).then(r => r.data),
}

export const inventoryApi = {
  list: (skip = 0, limit = 100) =>
    api.get('/inventory', { params: { skip, limit } }).then(r => r.data),
  optimize: (storeId?: number) =>
    api.get('/inventory/optimize', { params: { store_id: storeId } }).then(r => r.data),
  purchaseSuggestions: (storeId?: number) =>
    api.get('/inventory/purchase-suggestions', { params: { store_id: storeId } }).then(r => r.data),
  kpis: (storeId?: number) =>
    api.get('/inventory/kpis', { params: { store_id: storeId } }).then(r => r.data),
  abcAnalysis: (storeId?: number) =>
    api.get('/inventory/abc-analysis', { params: { store_id: storeId } }).then(r => r.data),
}

export const pricingApi = {
  getRecommendation: (productId: number, objective = 'profit') =>
    api.get(`/pricing/recommendation/${productId}`, { params: { objective } }).then(r => r.data),
  bulkRecommendations: (productIds?: number[], categoryId?: number) =>
    api.get('/pricing/recommendations/bulk', {
      params: {
        product_ids: productIds?.join(','),
        category_id: categoryId,
      },
    }).then(r => r.data),
  elasticity: (productId: number) =>
    api.get(`/pricing/elasticity/${productId}`).then(r => r.data),
  competitorBenchmark: (productId: number) =>
    api.get(`/pricing/competitor-benchmark/${productId}`).then(r => r.data),
}

export const promotionApi = {
  list: () => api.get('/promotions').then(r => r.data),
  getEffectiveness: (promotionId: number) =>
    api.get(`/promotions/${promotionId}/effectiveness`).then(r => r.data),
  deepAnalysis: (promotionId: number) =>
    api.get(`/promotions/${promotionId}/deep-analysis`).then(r => r.data),
  compare: (promotionIds: number[]) =>
    api.get('/promotions/compare', { params: { promotion_ids: promotionIds.join(',') } }).then(r => r.data),
  recommendations: (productId?: number, categoryId?: number) =>
    api.get('/promotions/recommendations', { params: { product_id: productId, category_id: categoryId } }).then(r => r.data),
}

export const salesApi = {
  list: (params?: any) => api.get('/sales', { params }).then(r => r.data),
  summary: (startDate?: string, endDate?: string) =>
    api.get('/sales/summary', { params: { start_date: startDate, end_date: endDate } }).then(r => r.data),
}

export const copilotApi = {
  query: (query: string, contextFilters?: Record<string, any>) =>
    api.post('/copilot/query', {
      query,
      context_filters: contextFilters,
    }).then(r => r.data),
  queryTypes: () => api.get('/copilot/query-types').then(r => r.data),
  knowledgeBase: () => api.get('/copilot/knowledge-base').then(r => r.data),
}
