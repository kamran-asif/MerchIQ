from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()


@router.post("/competitors/", response_model=schemas.Competitor)
def create_competitor(competitor: schemas.CompetitorCreate, db: Session = Depends(get_db)):
    db_comp = models.Competitor(**competitor.model_dump())
    db.add(db_comp)
    db.commit()
    db.refresh(db_comp)
    return db_comp


@router.get("/competitors/", response_model=List[schemas.Competitor])
def list_competitors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Competitor).offset(skip).limit(limit).all()


@router.post("/competitor-prices/", response_model=schemas.CompetitorPrice)
def create_competitor_price(cp: schemas.CompetitorPriceCreate, db: Session = Depends(get_db)):
    db_cp = models.CompetitorPrice(**cp.model_dump())
    db.add(db_cp)
    db.commit()
    db.refresh(db_cp)
    return db_cp


@router.post("/competitor-prices/bulk")
def create_competitor_prices_bulk(prices: List[schemas.CompetitorPriceCreate], db: Session = Depends(get_db)):
    db_prices = [models.CompetitorPrice(**p.model_dump()) for p in prices]
    db.bulk_save_objects(db_prices)
    db.commit()
    return {"created": len(db_prices)}


@router.get("/products/{product_id}/competitor-prices", response_model=List[schemas.CompetitorPrice])
def get_product_competitor_prices(
    product_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.CompetitorPrice).filter(models.CompetitorPrice.product_id == product_id)
    if start_date:
        query = query.filter(models.CompetitorPrice.record_date >= start_date)
    if end_date:
        query = query.filter(models.CompetitorPrice.record_date <= end_date)
    return query.order_by(models.CompetitorPrice.record_date.desc()).all()
