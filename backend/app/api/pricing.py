from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas import schemas
from app.services.pricing.service import PricingIntelligenceService
from app.models import models

router = APIRouter()


@router.get("/pricing/recommendation/{product_id}", response_model=schemas.PricingRecommendation)
def get_pricing_recommendation(
    product_id: int,
    objective: str = Query("profit", pattern="^(profit|revenue|market_share)$"),
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    service = PricingIntelligenceService(db)
    rec = service.generate_pricing_recommendation(product_id, objective)
    if not rec:
        raise HTTPException(status_code=500, detail="Failed to generate recommendation")

    return schemas.PricingRecommendation(**rec)


@router.get("/pricing/recommendations/bulk")
def get_bulk_pricing_recommendations(
    product_ids: Optional[str] = Query(None, description="Comma-separated product IDs"),
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    service = PricingIntelligenceService(db)
    ids = [int(pid) for pid in product_ids.split(",")] if product_ids else None
    results = service.bulk_pricing_recommendations(ids, category_id)
    return {"count": len(results), "recommendations": results}


@router.get("/pricing/elasticity/{product_id}")
def get_price_elasticity(product_id: int, db: Session = Depends(get_db)):
    service = PricingIntelligenceService(db)
    return service.get_price_elasticity_report(product_id)


@router.get("/pricing/competitor-benchmark/{product_id}")
def get_competitor_benchmark(product_id: int, db: Session = Depends(get_db)):
    service = PricingIntelligenceService(db)
    return service.get_competitor_benchmark(product_id)


@router.post("/pricing/apply-recommendation/{product_id}")
def apply_pricing_recommendation(
    product_id: int,
    new_price: float,
    reason: str = "AI-generated recommendation",
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if new_price <= product.cost_price:
        raise HTTPException(status_code=400, detail="Price cannot be below cost")

    old_price = product.base_price
    product.base_price = new_price

    ph = models.PriceHistory(
        product_id=product_id,
        price=new_price,
        price_type="retail",
        effective_date=datetime.utcnow().date(),
        reason=reason
    )
    db.add(ph)
    db.commit()
    db.refresh(product)

    return {
        "success": True,
        "product_id": product_id,
        "old_price": old_price,
        "new_price": new_price,
        "change_pct": round((new_price - old_price) / old_price * 100, 2)
    }


from datetime import datetime
