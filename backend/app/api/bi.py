from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas import schemas
from app.services.bi.service import BusinessIntelligenceService

router = APIRouter()


@router.get("/kpis", response_model=schemas.KPIData)
def get_kpi_dashboard(
    region_id: Optional[int] = None,
    store_id: Optional[int] = None,
    compare: bool = True,
    db: Session = Depends(get_db)
):
    service = BusinessIntelligenceService(db)
    return service.get_kpi_dashboard(region_id, store_id, compare)


@router.post("/root-cause-analysis", response_model=schemas.RootCauseAnalysis)
def run_root_cause_analysis(
    metric: str = Query(..., pattern="^(revenue|gross_margin|units_sold|inventory_turnover|stockout_rate|avg_order_value)$"),
    region_id: Optional[int] = None,
    store_id: Optional[int] = None,
    threshold: float = 0.85,
    db: Session = Depends(get_db)
):
    service = BusinessIntelligenceService(db)
    return service.run_root_cause_analysis(metric, region_id, store_id, threshold)


@router.get("/executive-report", response_model=schemas.ExecutiveReport)
def generate_executive_report(
    region_id: Optional[int] = None,
    period: str = Query("monthly", pattern="^(weekly|monthly|quarterly)$"),
    db: Session = Depends(get_db)
):
    service = BusinessIntelligenceService(db)
    return service.generate_executive_report(region_id, period)


@router.get("/multi-dimension-analysis")
def multi_dimension_analysis(
    metric: str = Query("revenue", pattern="^(revenue|units|profit)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    service = BusinessIntelligenceService(db)
    return service.get_multi_dimension_analysis(metric, start_date, end_date, region_id)


@router.get("/sales-trend")
def get_sales_trend(
    granularity: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    days: int = Query(90, ge=7, le=365),
    region_id: Optional[int] = None,
    store_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    from datetime import datetime, timedelta
    from sqlalchemy import func

    end = datetime.utcnow().date()
    start = end - timedelta(days=days - 1)

    query = db.query(
        models.Sale.sale_date,
        func.sum(models.Sale.total_amount).label("revenue"),
        func.sum(models.Sale.quantity_sold).label("units"),
        func.sum(models.Sale.cost_amount).label("cost"),
        func.count(models.Sale.transaction_id.distinct()).label("orders")
    ).filter(
        models.Sale.sale_date >= start,
        models.Sale.sale_date <= end
    )
    if region_id:
        query = query.filter(models.Sale.region_id == region_id)
    if store_id:
        query = query.filter(models.Sale.store_id == store_id)

    results = query.group_by(models.Sale.sale_date).order_by(models.Sale.sale_date).all()
    daily_data = [{
        "date": str(r.sale_date),
        "revenue": round(float(r.revenue or 0), 2),
        "units": int(r.units or 0),
        "cost": round(float(r.cost or 0), 2),
        "profit": round(float((r.revenue or 0) - (r.cost or 0)), 2),
        "orders": int(r.orders or 0)
    } for r in results]

    if granularity == "weekly":
        weekly = {}
        for d in daily_data:
            dt = datetime.strptime(d["date"], "%Y-%m-%d")
            week_start = (dt - timedelta(days=dt.weekday())).date()
            key = str(week_start)
            if key not in weekly:
                weekly[key] = {"date": key, "revenue": 0, "units": 0, "cost": 0, "profit": 0, "orders": 0}
            weekly[key]["revenue"] += d["revenue"]
            weekly[key]["units"] += d["units"]
            weekly[key]["cost"] += d["cost"]
            weekly[key]["profit"] += d["profit"]
            weekly[key]["orders"] += d["orders"]
        return {"granularity": granularity, "data": list(weekly.values())}

    if granularity == "monthly":
        monthly = {}
        for d in daily_data:
            key = d["date"][:7]
            if key not in monthly:
                monthly[key] = {"date": key, "revenue": 0, "units": 0, "cost": 0, "profit": 0, "orders": 0}
            monthly[key]["revenue"] += d["revenue"]
            monthly[key]["units"] += d["units"]
            monthly[key]["cost"] += d["cost"]
            monthly[key]["profit"] += d["profit"]
            monthly[key]["orders"] += d["orders"]
        return {"granularity": granularity, "data": list(monthly.values())}

    return {"granularity": granularity, "data": daily_data}


from app.models import models
