from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()


@router.post("/regions/", response_model=schemas.Region)
def create_region(region: schemas.RegionCreate, db: Session = Depends(get_db)):
    db_region = models.Region(**region.model_dump())
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region


@router.get("/regions/", response_model=List[schemas.Region])
def list_regions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Region).offset(skip).limit(limit).all()


@router.get("/regions/{region_id}", response_model=schemas.Region)
def get_region(region_id: int, db: Session = Depends(get_db)):
    region = db.query(models.Region).filter(models.Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region
