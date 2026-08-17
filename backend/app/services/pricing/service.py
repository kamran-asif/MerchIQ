import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import models
from app.core.config import settings
from app.core.utils import get_logger

logger = get_logger(__name__)


class PricingIntelligenceService:
    def __init__(self, db: Session):
        self.db = db

    def _get_price_sales_data(
        self,
        product_id: int,
        days: int = 180
    ) -> pd.DataFrame:
        cutoff = datetime.utcnow().date() - timedelta(days=days)
        sales = self.db.query(
            models.Sale.sale_date,
            models.Sale.quantity_sold,
            models.Sale.unit_price,
            models.Sale.discount_amount,
            models.Sale.promotion_id
        ).filter(
            models.Sale.product_id == product_id,
            models.Sale.sale_date >= cutoff
        ).all()

        if not sales:
            return pd.DataFrame(columns=["date", "price", "quantity", "revenue", "is_promo"])

        rows = []
        for s in sales:
            effective_price = s.unit_price - (s.discount_amount or 0)
            rows.append({
                "date": s.sale_date,
                "price": effective_price,
                "quantity": s.quantity_sold,
                "revenue": s.total_amount,
                "is_promo": 1 if s.promotion_id else 0
            })

        df = pd.DataFrame(rows)
        daily = df.groupby("date").agg({
            "price": "mean",
            "quantity": "sum",
            "revenue": "sum",
            "is_promo": "max"
        }).reset_index()
        return daily

    def calculate_price_elasticity(
        self,
        product_id: int
    ) -> Tuple[float, Dict]:
        data = self._get_price_sales_data(product_id, days=180)
        product = self.db.query(models.Product).filter(models.Product.id == product_id).first()

        if len(data) < 5 or not product:
            return settings.PRICE_ELASTICITY_THRESHOLD, {
                "elasticity": settings.PRICE_ELASTICITY_THRESHOLD,
                "data_points": len(data),
                "method": "industry_default",
                "category": "elastic" if abs(settings.PRICE_ELASTICITY_THRESHOLD) > 1 else "inelastic"
            }

        price_changes = []
        qty_changes = []
        for i in range(1, len(data)):
            if data["price"].iloc[i-1] > 0 and data["quantity"].iloc[i-1] > 0:
                p_change = (data["price"].iloc[i] - data["price"].iloc[i-1]) / data["price"].iloc[i-1]
                q_change = (data["quantity"].iloc[i] - data["quantity"].iloc[i-1]) / data["quantity"].iloc[i-1]
                if abs(p_change) > 0.01:
                    price_changes.append(p_change)
                    qty_changes.append(q_change)

        if len(price_changes) < 3:
            promo_data = data[data["is_promo"] == 1]
            regular_data = data[data["is_promo"] == 0]
            if len(promo_data) >= 2 and len(regular_data) >= 2:
                avg_promo_price = promo_data["price"].mean()
                avg_reg_price = regular_data["price"].mean()
                avg_promo_qty = promo_data["quantity"].mean()
                avg_reg_qty = regular_data["quantity"].mean()
                if avg_reg_price > 0 and avg_reg_qty > 0 and avg_promo_price != avg_reg_price:
                    pct_p = (avg_promo_price - avg_reg_price) / avg_reg_price
                    pct_q = (avg_promo_qty - avg_reg_qty) / avg_reg_qty
                    elasticity = pct_q / pct_p if pct_p != 0 else -1.0
                    method = "promo_vs_regular"
                else:
                    elasticity = settings.PRICE_ELASTICITY_THRESHOLD
                    method = "industry_default"
            else:
                elasticity = settings.PRICE_ELASTICITY_THRESHOLD
                method = "industry_default"
        else:
            valid_pairs = [(p, q) for p, q in zip(price_changes, qty_changes) if abs(p) > 0.01]
            if valid_pairs:
                elasticities = [q / p for p, q in valid_pairs if p != 0]
                elasticity = float(np.median(elasticities))
            else:
                elasticity = settings.PRICE_ELASTICITY_THRESHOLD
            method = "regression_based"

        elasticity = float(np.clip(elasticity, -5.0, 0.1))
        category = "elastic" if abs(elasticity) > 1 else "inelastic"

        return elasticity, {
            "elasticity": round(elasticity, 4),
            "data_points": len(data),
            "method": method,
            "category": category,
            "intercept_price": product.base_price,
            "base_quantity": data["quantity"].mean() if len(data) > 0 else 0
        }

    def get_competitor_benchmark(self, product_id: int) -> Dict:
        cutoff = datetime.utcnow().date() - timedelta(days=30)
        comp_prices = self.db.query(models.CompetitorPrice).filter(
            models.CompetitorPrice.product_id == product_id,
            models.CompetitorPrice.record_date >= cutoff
        ).all()

        product = self.db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            return {}

        if not comp_prices:
            return {
                "current_price": product.base_price,
                "competitor_avg": None,
                "competitor_min": None,
                "competitor_max": None,
                "price_index": None,
                "position": "no_competitor_data",
                "competitors_count": 0
            }

        prices = [cp.price + cp.shipping_cost for cp in comp_prices]
        avg_price = np.mean(prices)
        min_price = np.min(prices)
        max_price = np.max(prices)
        price_index = product.base_price / avg_price if avg_price > 0 else None

        if price_index is None:
            position = "unknown"
        elif price_index < 0.9:
            position = "price_leader"
        elif price_index <= 1.1:
            position = "at_market"
        else:
            position = "premium_priced"

        comp_ids = set(cp.competitor_id for cp in comp_prices)
        return {
            "current_price": product.base_price,
            "competitor_avg": round(avg_price, 2),
            "competitor_min": round(min_price, 2),
            "competitor_max": round(max_price, 2),
            "price_index": round(price_index, 3) if price_index else None,
            "position": position,
            "competitors_count": len(comp_ids)
        }

    def generate_pricing_recommendation(
        self,
        product_id: int,
        objective: str = "profit"
    ) -> Dict:
        product = self.db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            return {}

        elasticity, elastic_info = self.calculate_price_elasticity(product_id)
        benchmark = self.get_competitor_benchmark(product_id)

        data = self._get_price_sales_data(product_id, days=90)
        base_qty = data["quantity"].mean() if len(data) > 0 else 10
        base_rev = data["revenue"].mean() if len(data) > 0 else base_qty * product.base_price

        current_margin = (product.base_price - product.cost_price) / product.base_price if product.base_price > 0 else 0

        candidates = []
        for pct in np.arange(-0.20, 0.21, 0.02):
            new_price = round(product.base_price * (1 + pct), 2)
            if new_price <= product.cost_price:
                continue

            pct_change_p = (new_price - product.base_price) / product.base_price if product.base_price > 0 else 0
            expected_qty = base_qty * (1 + elasticity * pct_change_p)
            expected_qty = max(0, expected_qty)

            expected_rev = new_price * expected_qty
            expected_margin = (new_price - product.cost_price) / new_price
            expected_profit = (new_price - product.cost_price) * expected_qty

            competitor_penalty = 0
            if benchmark.get("competitor_avg"):
                if new_price > benchmark["competitor_max"]:
                    competitor_penalty = -5
                elif new_price < benchmark["competitor_min"]:
                    competitor_penalty = -2

            margin_penalty = 0
            if expected_margin < (product.cost_price * 0.15) / max(new_price, 0.01):
                margin_penalty = -10

            score = expected_profit + competitor_penalty * 100 + margin_penalty * 500
            if objective == "revenue":
                score = expected_rev + competitor_penalty * 100 + margin_penalty * 200
            elif objective == "market_share":
                score = expected_qty + competitor_penalty * 50 + margin_penalty * 100

            candidates.append({
                "price": new_price,
                "price_change_pct": round(pct * 100, 1),
                "expected_daily_qty": round(expected_qty, 2),
                "expected_daily_revenue": round(expected_rev, 2),
                "expected_margin_pct": round(expected_margin * 100, 2),
                "expected_daily_profit": round(expected_profit, 2),
                "score": round(score, 2)
            })

        candidates.sort(key=lambda x: x["score"], reverse=True)
        best = candidates[0] if candidates else {"price": product.base_price, "price_change_pct": 0}

        reasoning_parts = []
        reasoning_parts.append(f"Price elasticity is {elasticity:.2f} ({elastic_info['category']})")
        if benchmark.get("position"):
            reasoning_parts.append(f"Current pricing position: {benchmark['position']}")
        if benchmark.get("competitor_avg"):
            reasoning_parts.append(f"Competitor average: ${benchmark['competitor_avg']:.2f}")
        reasoning_parts.append(f"Objective: maximize {objective}")

        return {
            "product_id": product.id,
            "product_name": product.name,
            "current_price": product.base_price,
            "recommended_price": best["price"],
            "price_elasticity": round(elasticity, 4),
            "expected_demand_change_pct": round((best["expected_daily_qty"] - base_qty) / base_qty * 100 if base_qty > 0 else 0, 2),
            "expected_revenue_change_pct": round((best["expected_daily_revenue"] - base_rev) / base_rev * 100 if base_rev > 0 else 0, 2),
            "competitor_avg_price": benchmark.get("competitor_avg"),
            "margin_impact_pct": round((best["expected_margin_pct"] - current_margin * 100), 2),
            "reasoning": ". ".join(reasoning_parts) + ".",
            "alternative_prices": candidates[:5]
        }

    def bulk_pricing_recommendations(
        self,
        product_ids: Optional[List[int]] = None,
        category_id: Optional[int] = None
    ) -> List[Dict]:
        query = self.db.query(models.Product)
        if product_ids:
            query = query.filter(models.Product.id.in_(product_ids))
        if category_id:
            query = query.filter(models.Product.category_id == category_id)
        products = query.filter(models.Product.is_active == True).limit(50).all()

        recommendations = []
        for p in products:
            rec = self.generate_pricing_recommendation(p.id)
            if rec:
                recommendations.append(rec)
        return recommendations

    def get_price_elasticity_report(self, product_id: int) -> Dict:
        elasticity, info = self.calculate_price_elasticity(product_id)
        product = self.db.query(models.Product).filter(models.Product.id == product_id).first()

        price_points = []
        for pct in [-20, -15, -10, -5, 0, 5, 10, 15, 20]:
            new_price = product.base_price * (1 + pct / 100) if product else 0
            base_qty = 10
            if info.get("base_quantity"):
                base_qty = info["base_quantity"]
            pct_change = pct / 100
            new_qty = base_qty * (1 + elasticity * pct_change)
            new_rev = new_price * new_qty
            profit_per_unit = new_price - product.cost_price if product else 0
            new_profit = profit_per_unit * new_qty
            price_points.append({
                "price_change_pct": pct,
                "new_price": round(new_price, 2),
                "expected_qty": round(new_qty, 1),
                "expected_revenue": round(new_rev, 2),
                "expected_profit": round(new_profit, 2)
            })

        return {
            "product_id": product_id,
            "product_name": product.name if product else "",
            "current_price": product.base_price if product else 0,
            "elasticity": round(elasticity, 4),
            "elasticity_category": info["category"],
            "calculation_method": info["method"],
            "curve": price_points
        }
