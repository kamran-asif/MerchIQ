from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime


class RegionBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = None
    population: Optional[int] = None
    avg_income: Optional[float] = None
    climate_zone: Optional[str] = None


class RegionCreate(RegionBase):
    pass


class Region(RegionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class StoreBase(BaseModel):
    name: str = Field(..., max_length=200)
    store_code: Optional[str] = Field(None, max_length=20)
    region_id: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    size_sqft: Optional[float] = None
    opening_date: Optional[date] = None
    is_active: bool = True


class StoreCreate(StoreBase):
    pass


class Store(StoreBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    margin_target: float = 0.30


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    sku: str = Field(..., max_length=50)
    name: str = Field(..., max_length=300)
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    unit: str = "unit"
    cost_price: float
    base_price: float
    weight_kg: Optional[float] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    base_price: Optional[float] = None
    cost_price: Optional[float] = None
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InventoryBase(BaseModel):
    product_id: int
    store_id: int
    quantity_on_hand: int = 0
    quantity_reserved: int = 0
    quantity_on_order: int = 0
    reorder_point: int = 10
    reorder_quantity: int = 50
    lead_time_days: int = 7
    expiry_date: Optional[date] = None


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity_on_hand: Optional[int] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None
    lead_time_days: Optional[int] = None


class Inventory(InventoryBase):
    id: int
    last_restock_date: Optional[datetime] = None
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InventoryOptimization(BaseModel):
    product_id: int
    product_name: str
    store_id: int
    current_stock: int
    reorder_point: int
    recommended_order: int
    safety_stock: int
    eoq: int
    stockout_risk: str
    holding_cost: float
    ordering_cost: float
    total_cost: float


class SaleBase(BaseModel):
    sale_date: date
    product_id: int
    store_id: int
    region_id: Optional[int] = None
    quantity_sold: int
    unit_price: float
    discount_amount: float = 0.0
    total_amount: float
    cost_amount: float
    promotion_id: Optional[int] = None
    transaction_id: Optional[str] = None


class SaleCreate(SaleBase):
    pass


class Sale(SaleBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PriceHistoryBase(BaseModel):
    product_id: int
    price: float
    price_type: str = "retail"
    effective_date: date
    end_date: Optional[date] = None
    reason: Optional[str] = None


class PriceHistoryCreate(PriceHistoryBase):
    pass


class PriceHistory(PriceHistoryBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PromotionBase(BaseModel):
    name: str
    description: Optional[str] = None
    promotion_type: str
    start_date: date
    end_date: date
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    min_quantity: int = 1
    max_discount: Optional[float] = None
    budget: Optional[float] = None
    is_active: bool = True


class PromotionCreate(PromotionBase):
    product_ids: List[int] = []


class Promotion(PromotionBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PromotionEffectiveness(BaseModel):
    promotion_id: int
    promotion_name: str
    incremental_revenue: float
    lift_percentage: float
    roi: float
    total_units_sold: int
    total_revenue: float
    cost_of_promotion: float


class WeatherBase(BaseModel):
    record_date: date
    region_id: int
    temperature_avg: Optional[float] = None
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    precipitation_mm: float = 0.0
    snowfall_cm: float = 0.0
    humidity: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    weather_type: Optional[str] = None


class WeatherCreate(WeatherBase):
    pass


class Weather(WeatherBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CompetitorBase(BaseModel):
    name: str
    market_share: Optional[float] = None
    website: Optional[str] = None
    is_online: bool = False
    regions_present: Optional[str] = None


class CompetitorCreate(CompetitorBase):
    pass


class Competitor(CompetitorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CompetitorPriceBase(BaseModel):
    product_id: int
    competitor_id: int
    price: float
    record_date: date
    in_stock: bool = True
    shipping_cost: float = 0.0


class CompetitorPriceCreate(CompetitorPriceBase):
    pass


class CompetitorPrice(CompetitorPriceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ForecastRequest(BaseModel):
    product_id: int
    region_id: Optional[int] = None
    horizon_days: int = 30
    model_type: str = "prophet"


class ForecastItemData(BaseModel):
    date: date
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None


class ForecastResponse(BaseModel):
    product_id: int
    product_name: str
    model_type: str
    horizon_days: int
    mape: Optional[float] = None
    rmse: Optional[float] = None
    predictions: List[ForecastItemData]
    explanation: Optional[str] = None


class PricingRecommendation(BaseModel):
    product_id: int
    product_name: str
    current_price: float
    recommended_price: float
    price_elasticity: float
    expected_demand_change: float
    expected_revenue_change: float
    competitor_avg_price: Optional[float] = None
    margin_impact: float
    reasoning: str


class ForecastExplainability(BaseModel):
    product_id: int
    key_drivers: List[dict]
    seasonal_patterns: List[dict]
    trend_direction: str
    confidence_level: float
    risk_factors: List[str]


class KPIData(BaseModel):
    total_revenue: float
    revenue_growth: float
    total_units_sold: int
    units_growth: float
    gross_margin: float
    margin_growth: float
    avg_order_value: float
    inventory_turnover: float
    stockout_rate: float
    promotion_roi: float


class RootCauseAnalysis(BaseModel):
    metric_name: str
    current_value: float
    expected_value: float
    deviation: float
    primary_causes: List[dict]
    contributing_factors: List[dict]
    recommendations: List[str]
    confidence_score: float


class ExecutiveReport(BaseModel):
    report_period: str
    generated_at: datetime
    summary: str
    kpi_summary: KPIData
    top_performers: List[dict]
    underperformers: List[dict]
    key_insights: List[str]
    recommendations: List[str]
    risk_alerts: List[str]


class CopilotQueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[dict]] = None
    context_filters: Optional[dict] = None


class CopilotQueryResponse(BaseModel):
    query_type: str
    answer: str
    data_points: Optional[List[dict]] = None
    chart_spec: Optional[dict] = None
    related_insights: Optional[List[str]] = None
    confidence_score: float
    sources_used: List[str]
