import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import models
from app.core.utils import get_logger

logger = get_logger(__name__)


class PromotionAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def analyze_promotion_effectiveness(self, promotion_id: int) -> Dict:
        promotion = self.db.query(models.Promotion).filter(
            models.Promotion.id == promotion_id
        ).first()
        if not promotion:
            return {}

        promo_product_ids = [
            pp.product_id for pp in self.db.query(models.PromotionProduct).filter(
                models.PromotionProduct.promotion_id == promotion_id
            ).all()
        ]

        promo_sales = self.db.query(
            models.Sale.sale_date,
            models.Sale.product_id,
            models.Sale.quantity_sold,
            models.Sale.total_amount,
            models.Sale.cost_amount,
            models.Sale.discount_amount
        ).filter(
            models.Sale.promotion_id == promotion_id
        ).all()

        promo_start = promotion.start_date
        promo_end = promotion.end_date
        promo_duration = max(1, (promo_end - promo_start).days + 1)

        pre_start = promo_start - timedelta(days=promo_duration * 2)
        pre_end = promo_start - timedelta(days=1)

        pre_sales = self.db.query(
            models.Sale.sale_date,
            models.Sale.product_id,
            models.Sale.quantity_sold,
            models.Sale.total_amount,
            models.Sale.cost_amount
        ).filter(
            models.Sale.product_id.in_(promo_product_ids) if promo_product_ids else True,
            models.Sale.sale_date >= pre_start,
            models.Sale.sale_date <= pre_end,
            models.Sale.promotion_id.is_(None)
        ).all()

        promo_total_revenue = sum(s.total_amount for s in promo_sales)
        promo_total_units = sum(s.quantity_sold for s in promo_sales)
        promo_total_cost = sum(s.cost_amount for s in promo_sales)
        promo_total_discount = sum(s.discount_amount or 0 for s in promo_sales)

        pre_total_revenue = sum(s.total_amount for s in pre_sales)
        pre_total_units = sum(s.quantity_sold for s in pre_sales)

        daily_promo_revenue = promo_total_revenue / promo_duration if promo_duration > 0 else 0
        pre_duration = max(1, (pre_end - pre_start).days + 1)
        daily_pre_revenue = pre_total_revenue / pre_duration if pre_duration > 0 else 0

        expected_revenue_without_promo = daily_pre_revenue * promo_duration
        incremental_revenue = promo_total_revenue - expected_revenue_without_promo

        daily_pre_units = pre_total_units / pre_duration if pre_duration > 0 else 0
        expected_units_without_promo = daily_pre_units * promo_duration
        incremental_units = promo_total_units - expected_units_without_promo

        lift_pct = (incremental_units / expected_units_without_promo * 100) if expected_units_without_promo > 0 else 0

        gross_profit_promo = promo_total_revenue - promo_total_cost
        promo_cost = promo_total_discount + (promotion.budget or 0)
        net_profit = gross_profit_promo - promo_cost
        roi = (net_profit / promo_cost * 100) if promo_cost > 0 else float('inf')

        cannibalization = self._estimate_cannibalization(
            promo_product_ids, promo_start, promo_end, pre_start, pre_end
        )

        return {
            "promotion_id": promotion_id,
            "promotion_name": promotion.name,
            "promotion_type": promotion.promotion_type,
            "promotion_period": f"{promo_start} to {promo_end}",
            "promo_duration_days": promo_duration,
            "budget": promotion.budget or 0,
            "discount_percent": promotion.discount_percent,
            "discount_amount": promotion.discount_amount,
            "total_revenue": round(promo_total_revenue, 2),
            "total_units_sold": promo_total_units,
            "total_discount_given": round(promo_total_discount, 2),
            "gross_profit": round(gross_profit_promo, 2),
            "cost_of_promotion": round(promo_cost, 2),
            "net_profit": round(net_profit, 2),
            "incremental_revenue": round(incremental_revenue, 2),
            "incremental_units": int(round(incremental_units)),
            "lift_percentage": round(lift_pct, 2),
            "roi": round(roi if isinstance(roi, float) and roi < 1e9 else 999.9, 2),
            "cannibalization_estimate_pct": round(cannibalization, 2),
            "baseline_daily_revenue": round(daily_pre_revenue, 2),
            "promo_daily_revenue": round(daily_promo_revenue, 2),
            "products_in_promotion": len(promo_product_ids)
        }

    def _estimate_cannibalization(
        self,
        promo_product_ids: List[int],
        promo_start, promo_end, pre_start, pre_end
    ) -> float:
        if not promo_product_ids:
            return 0.0

        category_ids = self.db.query(models.Product.category_id).filter(
            models.Product.id.in_(promo_product_ids)
        ).distinct().all()
        category_ids = [c[0] for c in category_ids if c[0]]

        if not category_ids:
            return 0.0

        same_category_product_ids = self.db.query(models.Product.id).filter(
            models.Product.category_id.in_(category_ids),
            ~models.Product.id.in_(promo_product_ids)
        ).all()
        same_category_product_ids = [p[0] for p in same_category_product_ids]

        if not same_category_product_ids:
            return 0.0

        def _sum_sales(start, end, product_ids):
            return self.db.query(func.sum(models.Sale.quantity_sold)).filter(
                models.Sale.product_id.in_(product_ids),
                models.Sale.sale_date >= start,
                models.Sale.sale_date <= end
            ).scalar() or 0

        promo_duration_days = (promo_end - promo_start).days + 1
        pre_duration_days = max(1, (pre_end - pre_start).days + 1)

        promo_sales_non_promo = _sum_sales(promo_start, promo_end, same_category_product_ids)
        pre_sales_non_promo = _sum_sales(pre_start, pre_end, same_category_product_ids)

        daily_promo = promo_sales_non_promo / max(1, promo_duration_days)
        daily_pre = pre_sales_non_promo / pre_duration_days

        if daily_pre > 0:
            cannibal_pct = (daily_pre - daily_promo) / daily_pre * 100
            return max(0, cannibal_pct)
        return 0.0

    def compare_promotions(self, promotion_ids: List[int]) -> Dict:
        results = []
        for pid in promotion_ids:
            analysis = self.analyze_promotion_effectiveness(pid)
            if analysis:
                results.append(analysis)

        if not results:
            return {"comparison": [], "summary": {}}

        best_roi = max(results, key=lambda x: x["roi"])
        best_lift = max(results, key=lambda x: x["lift_percentage"])
        highest_rev = max(results, key=lambda x: x["total_revenue"])

        return {
            "comparison": results,
            "summary": {
                "count": len(results),
                "best_roi_promotion": best_roi["promotion_name"],
                "best_roi": best_roi["roi"],
                "best_lift_promotion": best_lift["promotion_name"],
                "best_lift_pct": best_lift["lift_percentage"],
                "highest_revenue_promotion": highest_rev["promotion_name"],
                "highest_revenue": highest_rev["total_revenue"],
                "avg_lift_pct": round(np.mean([r["lift_percentage"] for r in results]), 2),
                "avg_roi": round(np.mean([r["roi"] for r in results if r["roi"] < 999]), 2)
            }
        }

    def generate_promotion_recommendation(
        self,
        product_id: Optional[int] = None,
        category_id: Optional[int] = None
    ) -> List[Dict]:
        recommendations = []
        rec_types = [
            {
                "type": "FLASH_SALE",
                "name": "Flash Sale",
                "discount_pct_range": (15, 30),
                "duration_days": 3,
                "expected_lift_range": (30, 80),
                "description": "Short-duration, high-discount event for quick inventory clearance or traffic spike",
                "best_for": ["Overstocked items", "Seasonal products", "Slow-moving SKUs"]
            },
            {
                "type": "BOGO",
                "name": "Buy One Get One",
                "discount_pct_range": (25, 50),
                "duration_days": 7,
                "expected_lift_range": (50, 120),
                "description": "BOGO promotions drive higher unit volume and clear inventory faster",
                "best_for": ["Complementary products", "High-margin items", "Consumer goods"]
            },
            {
                "type": "PERCENT_OFF",
                "name": "Percentage Discount",
                "discount_pct_range": (10, 25),
                "duration_days": 14,
                "expected_lift_range": (15, 50),
                "description": "Standard tiered discount for sustained sales uplift",
                "best_for": ["Category-wide promotions", "Regular items", "Customer retention"]
            },
            {
                "type": "BUNDLE",
                "name": "Bundle Deal",
                "discount_pct_range": (10, 20),
                "duration_days": 21,
                "expected_lift_range": (20, 60),
                "description": "Bundled pricing encourages larger basket sizes",
                "best_for": ["Complementary goods", "Slow-moving combos", "Gift sets"]
            },
            {
                "type": "LOYALTY_EXCLUSIVE",
                "name": "Loyalty Member Exclusive",
                "discount_pct_range": (5, 15),
                "duration_days": 7,
                "expected_lift_range": (10, 35),
                "description": "Rewards program promotions for customer retention and engagement",
                "best_for": ["High-value customers", "Repeat purchase items", "Premium SKUs"]
            }
        ]

        for rt in rec_types:
            discount = int(np.mean(rt["discount_pct_range"]))
            lift = int(np.mean(rt["expected_lift_range"]))
            recommendations.append({
                "type": rt["type"],
                "name": rt["name"],
                "suggested_discount_percent": discount,
                "recommended_duration_days": rt["duration_days"],
                "expected_lift_pct": lift,
                "expected_roi_range": f"{max(0, lift - discount - 10)}-{lift + 20}",
                "description": rt["description"],
                "best_for_categories": rt["best_for"],
                "risk_level": "low" if rt["discount_pct_range"][1] < 25 else ("medium" if rt["discount_pct_range"][1] < 40 else "high")
            })

        return recommendations

    def get_promotion_calendar(self, start_date: str, end_date: str) -> List[Dict]:
        sd = datetime.strptime(start_date, "%Y-%m-%d").date()
        ed = datetime.strptime(end_date, "%Y-%m-%d").date()

        promotions = self.db.query(models.Promotion).filter(
            models.Promotion.start_date <= ed,
            models.Promotion.end_date >= sd
        ).all()

        events = []
        for p in promotions:
            overlap_start = max(p.start_date, sd)
            overlap_end = min(p.end_date, ed)
            duration = (overlap_end - overlap_start).days + 1
            total_duration = (p.end_date - p.start_date).days + 1
            events.append({
                "promotion_id": p.id,
                "name": p.name,
                "type": p.promotion_type,
                "start_date": str(overlap_start),
                "end_date": str(overlap_end),
                "overlap_days": duration,
                "total_duration_days": total_duration,
                "discount_percent": p.discount_percent,
                "is_active": p.is_active
            })
        return events
