from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas import schemas
from app.services.inventory.service import InventoryOptimizationService
from app.models import models

router = APIRouter()


@router.get("/inventory/optimize", response_model=List[schemas.InventoryOptimization])
def get_inventory_optimizations(
    store_id: Optional[int] = None,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    service = InventoryOptimizationService(db)
    results = service.optimize_all_inventory(store_id)
    if product_id:
        results = [r for r in results if r["product_id"] == product_id]
    return [schemas.InventoryOptimization(**r) for r in results]


@router.get("/inventory/{inv_id}/optimize")
def get_single_inventory_optimization(inv_id: int, db: Session = Depends(get_db)):
    inv = db.query(models.Inventory).filter(models.Inventory.id == inv_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    service = InventoryOptimizationService(db)
    result = service.analyze_inventory_item(inv)
    return result


@router.get("/inventory/purchase-suggestions")
def get_purchase_order_suggestions(
    store_id: Optional[int] = None,
    min_order: int = 0,
    db: Session = Depends(get_db)
):
    service = InventoryOptimizationService(db)
    suggestions = service.generate_purchase_order_suggestions(store_id)
    suggestions = [s for s in suggestions if s["recommended_order"] >= min_order]
    total_cost = sum(s["estimated_cost"] for s in suggestions)
    return {
        "count": len(suggestions),
        "total_estimated_cost": round(total_cost, 2),
        "items": suggestions
    }


@router.get("/inventory/kpis")
def get_inventory_kpis(store_id: Optional[int] = None, db: Session = Depends(get_db)):
    service = InventoryOptimizationService(db)
    return service.get_inventory_kpis(store_id)


@router.get("/inventory/abc-analysis")
def abc_analysis(
    store_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    cutoff_days = 90
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow().date() - timedelta(days=cutoff_days)

    query = db.query(
        models.Sale.product_id,
        func.sum(models.Sale.total_amount).label("revenue"),
        func.sum(models.Sale.quantity_sold).label("units")
    ).filter(models.Sale.sale_date >= cutoff)
    if store_id:
        query = query.filter(models.Sale.store_id == store_id)

    results = query.group_by(models.Sale.product_id).all()
    if not results:
        return {"classification": [], "summary": {}}

    rows = []
    for r in results:
        product = db.query(models.Product).filter(models.Product.id == r.product_id).first()
        rows.append({
            "product_id": r.product_id,
            "product_name": product.name if product else f"Product {r.product_id}",
            "sku": product.sku if product else "",
            "revenue": float(r.revenue or 0),
            "units": int(r.units or 0)
        })

    rows.sort(key=lambda x: x["revenue"], reverse=True)
    total_rev = sum(r["revenue"] for r in rows)

    cum_rev = 0
    for row in rows:
        cum_rev += row["revenue"]
        pct = cum_rev / total_rev * 100 if total_rev > 0 else 0
        row["cumulative_pct"] = round(pct, 2)
        if pct <= 80:
            row["class"] = "A"
        elif pct <= 95:
            row["class"] = "B"
        else:
            row["class"] = "C"

    class_counts = {"A": 0, "B": 0, "C": 0}
    class_rev = {"A": 0, "B": 0, "C": 0}
    for row in rows:
        class_counts[row["class"]] += 1
        class_rev[row["class"]] += row["revenue"]

    summary = {}
    for cls in ["A", "B", "C"]:
        summary[cls] = {
            "item_count": class_counts[cls],
            "item_pct": round(class_counts[cls] / len(rows) * 100, 2),
            "revenue": round(class_rev[cls], 2),
            "revenue_pct": round(class_rev[cls] / total_rev * 100, 2) if total_rev > 0 else 0
        }

    return {
        "classification": rows,
        "summary": summary,
        "total_products": len(rows),
        "total_revenue": round(total_rev, 2)
    }
