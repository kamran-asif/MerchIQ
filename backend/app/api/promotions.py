from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()


@router.post("/promotions/", response_model=schemas.Promotion)
def create_promotion(promotion: schemas.PromotionCreate, db: Session = Depends(get_db)):
    product_ids = promotion.product_ids
    promo_data = promotion.model_dump(exclude={"product_ids"})
    db_promo = models.Promotion(**promo_data)
    db.add(db_promo)
    db.flush()
    for pid in product_ids:
        pp = models.PromotionProduct(promotion_id=db_promo.id, product_id=pid)
        db.add(pp)
    db.commit()
    db.refresh(db_promo)
    return db_promo


@router.get("/promotions/", response_model=List[schemas.Promotion])
def list_promotions(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    promotion_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Promotion)
    if is_active is not None:
        query = query.filter(models.Promotion.is_active == is_active)
    if promotion_type:
        query = query.filter(models.Promotion.promotion_type == promotion_type)
    return query.offset(skip).limit(limit).all()


@router.get("/promotions/{promo_id}", response_model=schemas.Promotion)
def get_promotion(promo_id: int, db: Session = Depends(get_db)):
    promo = db.query(models.Promotion).filter(models.Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return promo


@router.post("/price-history/", response_model=schemas.PriceHistory)
def create_price_history(ph: schemas.PriceHistoryCreate, db: Session = Depends(get_db)):
    db_ph = models.PriceHistory(**ph.model_dump())
    db.add(db_ph)
    db.commit()
    db.refresh(db_ph)
    return db_ph


@router.get("/products/{product_id}/price-history", response_model=List[schemas.PriceHistory])
def get_product_price_history(product_id: int, db: Session = Depends(get_db)):
    return db.query(models.PriceHistory).filter(
        models.PriceHistory.product_id == product_id
    ).order_by(models.PriceHistory.effective_date.desc()).all()
