from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()


@router.post("/inventory/", response_model=schemas.Inventory)
def create_inventory_record(inv: schemas.InventoryCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Inventory).filter(
        models.Inventory.product_id == inv.product_id,
        models.Inventory.store_id == inv.store_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Inventory record already exists for this product-store pair")
    db_inv = models.Inventory(**inv.model_dump())
    db.add(db_inv)
    db.commit()
    db.refresh(db_inv)
    return db_inv


@router.get("/inventory/", response_model=List[schemas.Inventory])
def list_inventory(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    store_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Inventory)
    if product_id:
        query = query.filter(models.Inventory.product_id == product_id)
    if store_id:
        query = query.filter(models.Inventory.store_id == store_id)
    return query.offset(skip).limit(limit).all()


@router.put("/inventory/{inv_id}", response_model=schemas.Inventory)
def update_inventory(inv_id: int, inv: schemas.InventoryUpdate, db: Session = Depends(get_db)):
    db_inv = db.query(models.Inventory).filter(models.Inventory.id == inv_id).first()
    if not db_inv:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    for key, value in inv.model_dump(exclude_unset=True).items():
        setattr(db_inv, key, value)
    db.commit()
    db.refresh(db_inv)
    return db_inv


@router.get("/inventory/low-stock")
def get_low_stock(threshold: int = 10, db: Session = Depends(get_db)):
    results = db.query(models.Inventory).filter(
        models.Inventory.quantity_on_hand <= models.Inventory.reorder_point
    ).all()
    return {"count": len(results), "items": results}
