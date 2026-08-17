from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Date
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(20), unique=True, index=True)
    country = Column(String(100))
    population = Column(Integer)
    avg_income = Column(Float)
    climate_zone = Column(String(50))

    stores = relationship("Store", back_populates="region")
    weather_records = relationship("Weather", back_populates="region")
    sales = relationship("Sale", back_populates="region")


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    store_code = Column(String(20), unique=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    size_sqft = Column(Float)
    opening_date = Column(Date)
    is_active = Column(Boolean, default=True)

    region = relationship("Region", back_populates="stores")
    inventory_records = relationship("Inventory", back_populates="store")
    sales = relationship("Sale", back_populates="store")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text)
    margin_target = Column(Float, default=0.30)

    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id])


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(300), nullable=False, index=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"))
    brand = Column(String(100))
    unit = Column(String(20), default="unit")
    cost_price = Column(Float, nullable=False)
    base_price = Column(Float, nullable=False)
    weight_kg = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    inventory_records = relationship("Inventory", back_populates="product")
    sales = relationship("Sale", back_populates="product")
    price_history = relationship("PriceHistory", back_populates="product")
    promotions = relationship("PromotionProduct", back_populates="product")
    forecasts = relationship("Forecast", back_populates="product")
    competitor_prices = relationship("CompetitorPrice", back_populates="product")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    quantity_on_order = Column(Integer, default=0)
    reorder_point = Column(Integer, default=10)
    reorder_quantity = Column(Integer, default=50)
    lead_time_days = Column(Integer, default=7)
    last_restock_date = Column(DateTime)
    expiry_date = Column(Date, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="inventory_records")
    store = relationship("Store", back_populates="inventory_records")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    sale_date = Column(Date, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    quantity_sold = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    cost_amount = Column(Float, nullable=False)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=True)
    transaction_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="sales")
    store = relationship("Store", back_populates="sales")
    region = relationship("Region", back_populates="sales")
    promotion = relationship("Promotion", back_populates="sales")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    price_type = Column(String(20), default="retail")
    effective_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    reason = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="price_history")


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    promotion_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    discount_percent = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    min_quantity = Column(Integer, default=1)
    max_discount = Column(Float, nullable=True)
    budget = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("PromotionProduct", back_populates="promotion")
    sales = relationship("Sale", back_populates="promotion")


class PromotionProduct(Base):
    __tablename__ = "promotion_products"

    id = Column(Integer, primary_key=True, index=True)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    promotion = relationship("Promotion", back_populates="products")
    product = relationship("Product", back_populates="promotions")


class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, index=True)
    record_date = Column(Date, nullable=False, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    temperature_avg = Column(Float)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    precipitation_mm = Column(Float, default=0.0)
    snowfall_cm = Column(Float, default=0.0)
    humidity = Column(Float)
    wind_speed_kmh = Column(Float)
    weather_type = Column(String(50))

    region = relationship("Region", back_populates="weather_records")


class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    market_share = Column(Float)
    website = Column(String(500))
    is_online = Column(Boolean, default=False)
    regions_present = Column(String(500))

    prices = relationship("CompetitorPrice", back_populates="competitor")


class CompetitorPrice(Base):
    __tablename__ = "competitor_prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=False)
    price = Column(Float, nullable=False)
    record_date = Column(Date, nullable=False, index=True)
    in_stock = Column(Boolean, default=True)
    shipping_cost = Column(Float, default=0.0)

    product = relationship("Product", back_populates="competitor_prices")
    competitor = relationship("Competitor", back_populates="prices")


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    model_type = Column(String(50), nullable=False)
    forecast_date = Column(Date, nullable=False, index=True)
    horizon_days = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    mape = Column(Float)
    rmse = Column(Float)

    product = relationship("Product", back_populates="forecasts")
    items = relationship("ForecastItem", back_populates="forecast")


class ForecastItem(Base):
    __tablename__ = "forecast_items"

    id = Column(Integer, primary_key=True, index=True)
    forecast_id = Column(Integer, ForeignKey("forecasts.id"), nullable=False)
    date = Column(Date, nullable=False)
    predicted_value = Column(Float, nullable=False)
    lower_bound = Column(Float)
    upper_bound = Column(Float)

    forecast = relationship("Forecast", back_populates="items")
