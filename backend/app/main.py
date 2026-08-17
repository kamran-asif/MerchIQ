from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import (
    products,
    inventory,
    sales,
    regions,
    stores,
    promotions,
    weather,
    competitors,
    forecasting,
    inventory_opt,
    pricing,
    promotion_analytics,
    bi,
    copilot,
)
from app.core.database import engine, Base
import os

if not os.getenv("TESTING"):
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Retail Planning Intelligence Platform integrating demand forecasting, inventory optimization, pricing intelligence, and promotion analytics with LLM-powered retail copilot.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix=settings.API_V1_PREFIX, tags=["Products & Categories"])
app.include_router(inventory.router, prefix=settings.API_V1_PREFIX, tags=["Inventory"])
app.include_router(sales.router, prefix=settings.API_V1_PREFIX, tags=["Sales"])
app.include_router(regions.router, prefix=settings.API_V1_PREFIX, tags=["Regions & Weather"])
app.include_router(stores.router, prefix=settings.API_V1_PREFIX, tags=["Stores"])
app.include_router(promotions.router, prefix=settings.API_V1_PREFIX, tags=["Promotions"])
app.include_router(weather.router, prefix=settings.API_V1_PREFIX, tags=["Weather"])
app.include_router(competitors.router, prefix=settings.API_V1_PREFIX, tags=["Competitors"])
app.include_router(forecasting.router, prefix=settings.API_V1_PREFIX, tags=["Demand Forecasting"])
app.include_router(inventory_opt.router, prefix=settings.API_V1_PREFIX, tags=["Inventory Optimization"])
app.include_router(pricing.router, prefix=settings.API_V1_PREFIX, tags=["Pricing Intelligence"])
app.include_router(promotion_analytics.router, prefix=settings.API_V1_PREFIX, tags=["Promotion Analytics"])
app.include_router(bi.router, prefix=settings.API_V1_PREFIX, tags=["Business Intelligence & RCA"])
app.include_router(copilot.router, prefix=settings.API_V1_PREFIX, tags=["AI Retail Copilot"])


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "modules": [
            "Demand Forecasting (Prophet + XGBoost)",
            "Inventory Optimization",
            "Pricing Intelligence",
            "Promotion Analytics",
            "Business Intelligence & Root Cause Analysis Engine",
            "AI Retail Copilot (LangGraph + RAG)"
        ],
        "api_docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
