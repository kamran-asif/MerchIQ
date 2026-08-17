import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import models
from app.core.config import settings
from app.core.utils import get_logger
from app.services.forecasting.service import DemandForecastingService

logger = get_logger(__name__)


class InventoryOptimizationService:
    def __init__(self, db: Session):
        self.db = db
        self.forecast_service = DemandForecastingService(db)

    def _get_usage_history(self, product_id: int, store_id: int, days: int = 90) -> pd.Series:
        cutoff = datetime.utcnow().date() - timedelta(days=days)
        sales = self.db.query(
            models.Sale.sale_date,
            models.Sale.quantity_sold
        ).filter(
            models.Sale.product_id == product_id,
            models.Sale.store_id == store_id,
            models.Sale.sale_date >= cutoff
        ).order_by(models.Sale.sale_date).all()

        if not sales:
            return pd.Series(dtype=float)

        df = pd.DataFrame(sales, columns=["sale_date", "quantity"])
        daily = df.groupby("sale_date")["quantity"].sum()
        idx = pd.date_range(start=cutoff, end=datetime.utcnow().date(), freq="D")
        daily = daily.reindex(idx, fill_value=0)
        return daily

    def calculate_safety_stock(
        self,
        avg_daily_demand: float,
        demand_std: float,
        lead_time_days: int,
        z_score: Optional[float] = None
    ) -> float:
        z = z_score if z_score else settings.SAFETY_STOCK_Z_SCORE
        return round(z * demand_std * np.sqrt(lead_time_days), 2)

    def calculate_eoq(
        self,
        annual_demand: float,
        ordering_cost: float,
        holding_cost_per_unit: float
    ) -> int:
        if holding_cost_per_unit <= 0:
            return 0
        eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit)
        return int(round(eoq))

    def calculate_reorder_point(
        self,
        avg_daily_demand: float,
        lead_time_days: int,
        safety_stock: float
    ) -> int:
        return int(round(avg_daily_demand * lead_time_days + safety_stock))

    def analyze_inventory_item(
        self,
        inv_record: models.Inventory,
        ordering_cost: float = 50.0,
        holding_cost_pct: float = 0.25
    ) -> Dict:
        product = self.db.query(models.Product).filter(
            models.Product.id == inv_record.product_id
        ).first()
        if not product:
            return {}

        usage = self._get_usage_history(inv_record.product_id, inv_record.store_id, days=90)
        if len(usage) == 0:
            avg_daily_demand = 5.0
            demand_std = 2.0
        else:
            avg_daily_demand = usage.mean()
            demand_std = usage.std() if usage.std() > 0 else avg_daily_demand * 0.3

        annual_demand = avg_daily_demand * 365
        holding_cost_per_unit = product.cost_price * holding_cost_pct

        safety_stock = self.calculate_safety_stock(
            avg_daily_demand, demand_std, inv_record.lead_time_days
        )
        eoq = self.calculate_eoq(annual_demand, ordering_cost, holding_cost_per_unit)
        reorder_point = self.calculate_reorder_point(
            avg_daily_demand, inv_record.lead_time_days, safety_stock
        )

        current_stock = inv_record.quantity_on_hand - inv_record.quantity_reserved
        days_of_supply = current_stock / avg_daily_demand if avg_daily_demand > 0 else 999

        if current_stock <= 0:
            stockout_risk = "critical"
        elif current_stock < safety_stock:
            stockout_risk = "high"
        elif current_stock < reorder_point:
            stockout_risk = "medium"
        elif days_of_supply > 60:
            stockout_risk = "overstocked"
        else:
            stockout_risk = "low"

        if current_stock < reorder_point:
            recommended_order = max(eoq, reorder_point - current_stock + inv_record.quantity_on_order)
        else:
            recommended_order = 0

        holding_cost = current_stock * holding_cost_per_unit / 12
        num_orders = annual_demand / eoq if eoq > 0 else 12
        ordering_cost_monthly = (num_orders * ordering_cost) / 12

        return {
            "product_id": inv_record.product_id,
            "product_name": product.name,
            "store_id": inv_record.store_id,
            "current_stock": current_stock,
            "reorder_point": reorder_point,
            "recommended_order": int(round(recommended_order)),
            "safety_stock": int(round(safety_stock)),
            "eoq": eoq,
            "stockout_risk": stockout_risk,
            "days_of_supply": round(days_of_supply, 1),
            "avg_daily_demand": round(avg_daily_demand, 2),
            "holding_cost": round(holding_cost, 2),
            "ordering_cost": round(ordering_cost_monthly, 2),
            "total_cost": round(holding_cost + ordering_cost_monthly, 2),
            "lead_time_days": inv_record.lead_time_days,
            "quantity_on_order": inv_record.quantity_on_order,
        }

    def optimize_all_inventory(self, store_id: Optional[int] = None) -> List[Dict]:
        query = self.db.query(models.Inventory)
        if store_id:
            query = query.filter(models.Inventory.store_id == store_id)
        inv_records = query.all()

        results = []
        for inv in inv_records:
            analysis = self.analyze_inventory_item(inv)
            if analysis:
                results.append(analysis)
        return sorted(results, key=lambda x: x["stockout_risk"])

    def generate_purchase_order_suggestions(self, store_id: Optional[int] = None) -> List[Dict]:
        optimizations = self.optimize_all_inventory(store_id)
        orders = [o for o in optimizations if o["recommended_order"] > 0]

        product_ids = [o["product_id"] for o in orders]
        products = self.db.query(models.Product).filter(
            models.Product.id.in_(product_ids)
        ).all() if product_ids else []
        product_map = {p.id: p for p in products}

        suggestions = []
        for order in orders:
            p = product_map.get(order["product_id"])
            if not p:
                continue
            suggestions.append({
                **order,
                "cost_price": p.cost_price,
                "estimated_cost": round(order["recommended_order"] * p.cost_price, 2),
                "sku": p.sku,
                "category_id": p.category_id,
                "priority": 1 if order["stockout_risk"] in ["critical", "high"] else 2
            })

        suggestions.sort(key=lambda x: (x["priority"], -x["recommended_order"]))
        return suggestions

    def get_inventory_kpis(self, store_id: Optional[int] = None) -> Dict:
        query = self.db.query(models.Inventory)
        if store_id:
            query = query.filter(models.Inventory.store_id == store_id)
        inv_records = query.all()

        if not inv_records:
            return {
                "total_sku_count": 0,
                "total_inventory_value": 0,
                "stockout_sku_count": 0,
                "stockout_rate": 0,
                "overstocked_sku_count": 0,
                "avg_days_of_supply": 0,
                "inventory_turnover": 0
            }

        product_ids = [i.product_id for i in inv_records]
        products = self.db.query(models.Product).filter(models.Product.id.in_(product_ids)).all()
        product_map = {p.id: p for p in products}

        optimizations = self.optimize_all_inventory(store_id)
        opt_map = {(o["product_id"], o["store_id"]): o for o in optimizations}

        total_value = 0
        stockout_count = 0
        overstocked_count = 0
        days_list = []

        for inv in inv_records:
            p = product_map.get(inv.product_id)
            if p:
                total_value += inv.quantity_on_hand * p.cost_price
            opt = opt_map.get((inv.product_id, inv.store_id))
            if opt:
                if opt["stockout_risk"] in ["critical", "high"]:
                    stockout_count += 1
                if opt["stockout_risk"] == "overstocked":
                    overstocked_count += 1
                days_list.append(opt["days_of_supply"])

        cutoff = datetime.utcnow().date() - timedelta(days=90)
        sales_query = self.db.query(
            func.sum(models.Sale.cost_amount)
        ).filter(models.Sale.sale_date >= cutoff)
        if store_id:
            sales_query = sales_query.filter(models.Sale.store_id == store_id)
        cogs_90 = sales_query.scalar() or 0

        avg_inventory_value = total_value
        inventory_turnover = (cogs_90 * 4) / avg_inventory_value if avg_inventory_value > 0 else 0

        return {
            "total_sku_count": len(inv_records),
            "total_inventory_value": round(total_value, 2),
            "stockout_sku_count": stockout_count,
            "stockout_rate": round(stockout_count / len(inv_records) * 100, 2),
            "overstocked_sku_count": overstocked_count,
            "overstocked_rate": round(overstocked_count / len(inv_records) * 100, 2),
            "avg_days_of_supply": round(np.mean(days_list), 1) if days_list else 0,
            "inventory_turnover": round(inventory_turnover, 2)
        }
