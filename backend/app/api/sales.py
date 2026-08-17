from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()


@router.post("/sales/", response_model=schemas.Sale)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    db_sale = models.Sale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.post("/sales/bulk")
def create_sales_bulk(sales: List[schemas.SaleCreate], db: Session = Depends(get_db)):
    db_sales = [models.Sale(**s.model_dump()) for s in sales]
    db.bulk_save_objects(db_sales)
    db.commit()
    return {"created": len(db_sales)}


@router.get("/sales/", response_model=List[schemas.Sale])
def list_sales(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    store_id: Optional[int] = None,
    region_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Sale)
    if product_id:
        query = query.filter(models.Sale.product_id == product_id)
    if store_id:
        query = query.filter(models.Sale.store_id == store_id)
    if region_id:
        query = query.filter(models.Sale.region_id == region_id)
    if start_date:
        query = query.filter(models.Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(models.Sale.sale_date <= end_date)
    return query.order_by(models.Sale.sale_date.desc()).offset(skip).limit(limit).all()


@router.get("/sales/summary")
def get_sales_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    group_by: str = Query("day", pattern="^(day|week|month|category|product|region|store)$"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Sale)
    if start_date:
        query = query.filter(models.Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(models.Sale.sale_date <= end_date)

    result = query.with_entities(
        func.sum(models.Sale.total_amount).label("total_revenue"),
        func.sum(models.Sale.quantity_sold).label("total_units"),
        func.sum(models.Sale.cost_amount).label("total_cost"),
        func.count(models.Sale.id).label("num_transactions")
    ).first()

    return {
        "total_revenue": float(result.total_revenue or 0),
        "total_units": int(result.total_units or 0),
        "total_cost": float(result.total_cost or 0),
        "gross_profit": float((result.total_revenue or 0) - (result.total_cost or 0)),
        "gross_margin": float(
            ((result.total_revenue or 0) - (result.total_cost or 0)) / (result.total_revenue or 1) * 100
        ),
        "num_transactions": int(result.num_transactions or 0),
        "avg_order_value": float((result.total_revenue or 0) / (result.num_transactions or 1))
    }
