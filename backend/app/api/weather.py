from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()


@router.post("/weather/", response_model=schemas.Weather)
def create_weather_record(w: schemas.WeatherCreate, db: Session = Depends(get_db)):
    db_w = models.Weather(**w.model_dump())
    db.add(db_w)
    db.commit()
    db.refresh(db_w)
    return db_w


@router.post("/weather/bulk")
def create_weather_bulk(records: List[schemas.WeatherCreate], db: Session = Depends(get_db)):
    db_records = [models.Weather(**r.model_dump()) for r in records]
    db.bulk_save_objects(db_records)
    db.commit()
    return {"created": len(db_records)}


@router.get("/weather/", response_model=List[schemas.Weather])
def list_weather(
    skip: int = 0,
    limit: int = 100,
    region_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Weather)
    if region_id:
        query = query.filter(models.Weather.region_id == region_id)
    if start_date:
        query = query.filter(models.Weather.record_date >= start_date)
    if end_date:
        query = query.filter(models.Weather.record_date <= end_date)
    return query.order_by(models.Weather.record_date.desc()).offset(skip).limit(limit).all()
