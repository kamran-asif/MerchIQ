from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas import schemas
from app.services.promotions.service import PromotionAnalyticsService
from app.models import models

router = APIRouter()


@router.get("/promotions/{promotion_id}/effectiveness", response_model=schemas.PromotionEffectiveness)
def get_promotion_effectiveness(promotion_id: int, db: Session = Depends(get_db)):
    promotion = db.query(models.Promotion).filter(models.Promotion.id == promotion_id).first()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")

    service = PromotionAnalyticsService(db)
    analysis = service.analyze_promotion_effectiveness(promotion_id)
    if not analysis:
        raise HTTPException(status_code=500, detail="Failed to analyze promotion")

    return schemas.PromotionEffectiveness(
        promotion_id=promotion_id,
        promotion_name=analysis["promotion_name"],
        incremental_revenue=analysis["incremental_revenue"],
        lift_percentage=analysis["lift_percentage"],
        roi=analysis["roi"],
        total_units_sold=analysis["total_units_sold"],
        total_revenue=analysis["total_revenue"],
        cost_of_promotion=analysis["cost_of_promotion"]
    )


@router.get("/promotions/{promotion_id}/deep-analysis")
def get_promotion_deep_analysis(promotion_id: int, db: Session = Depends(get_db)):
    service = PromotionAnalyticsService(db)
    return service.analyze_promotion_effectiveness(promotion_id)


@router.get("/promotions/compare")
def compare_promotions(
    promotion_ids: str = Query(..., description="Comma-separated promotion IDs"),
    db: Session = Depends(get_db)
):
    ids = [int(pid) for pid in promotion_ids.split(",")]
    service = PromotionAnalyticsService(db)
    return service.compare_promotions(ids)


@router.get("/promotions/recommendations")
def get_promotion_recommendations(
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    service = PromotionAnalyticsService(db)
    return service.generate_promotion_recommendation(product_id, category_id)


@router.get("/promotions/calendar")
def get_promotion_calendar(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    service = PromotionAnalyticsService(db)
    return service.get_promotion_calendar(start_date, end_date)
