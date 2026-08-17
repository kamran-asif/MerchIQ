import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import models
from app.core.utils import get_logger

logger = get_logger(__name__)

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logger.warning("Prophet not installed, using fallback forecasting")

try:
    import xgboost as xgb
    from sklearn.preprocessing import StandardScaler
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost not installed, using fallback forecasting")


class DemandForecastingService:
    def __init__(self, db: Session):
        self.db = db

    def _get_sales_timeseries(
        self,
        product_id: int,
        region_id: Optional[int] = None,
        days_history: int = 365
    ) -> pd.DataFrame:
        cutoff_date = datetime.utcnow().date() - timedelta(days=days_history)
        query = self.db.query(
            models.Sale.sale_date,
            models.Sale.quantity_sold,
            models.Sale.unit_price,
            models.Sale.promotion_id,
            models.Sale.region_id
        ).filter(
            models.Sale.product_id == product_id,
            models.Sale.sale_date >= cutoff_date
        )
        if region_id:
            query = query.filter(models.Sale.region_id == region_id)

        results = query.order_by(models.Sale.sale_date).all()
        if not results:
            return pd.DataFrame(columns=["ds", "y", "price", "is_promotion"])

        df = pd.DataFrame([{
            "sale_date": r.sale_date,
            "quantity": r.quantity_sold,
            "price": r.unit_price,
            "promotion_id": r.promotion_id,
            "region_id": r.region_id
        } for r in results])

        daily = df.groupby("sale_date").agg({
            "quantity": "sum",
            "price": "mean",
            "promotion_id": "max"
        }).reset_index()

        daily.rename(columns={"sale_date": "ds", "quantity": "y"}, inplace=True)
        daily["is_promotion"] = daily["promotion_id"].notna().astype(int)
        daily["ds"] = pd.to_datetime(daily["ds"])

        full_range = pd.date_range(start=daily["ds"].min(), end=daily["ds"].max(), freq="D")
        daily = daily.set_index("ds").reindex(full_range).reset_index()
        daily.rename(columns={"index": "ds"}, inplace=True)
        daily["y"] = daily["y"].fillna(0)
        daily["price"] = daily["price"].ffill().bfill()
        daily["is_promotion"] = daily["is_promotion"].fillna(0)

        return daily

    def forecast_prophet(
        self,
        product_id: int,
        horizon_days: int = 30,
        region_id: Optional[int] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        ts_data = self._get_sales_timeseries(product_id, region_id)
        if len(ts_data) < 14:
            return self._fallback_forecast(ts_data, horizon_days)

        if not PROPHET_AVAILABLE:
            return self._fallback_forecast(ts_data, horizon_days)

        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,
            interval_width=0.95
        )
        model.add_regressor("price")
        model.add_regressor("is_promotion")

        model.fit(ts_data[["ds", "y", "price", "is_promotion"]])

        future = model.make_future_dataframe(periods=horizon_days)
        last_price = ts_data["price"].iloc[-1]
        future["price"] = last_price
        future["is_promotion"] = 0

        for i in range(len(ts_data), len(future)):
            date = future["ds"].iloc[i]
            promos = self.db.query(models.Promotion).filter(
                models.Promotion.start_date <= date.date(),
                models.Promotion.end_date >= date.date()
            ).join(models.PromotionProduct).filter(
                models.PromotionProduct.product_id == product_id
            ).first()
            if promos:
                future.loc[i, "is_promotion"] = 1

        forecast = model.predict(future)

        preds = forecast.tail(horizon_days)[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        preds["yhat"] = preds["yhat"].clip(lower=0)
        preds["yhat_lower"] = preds["yhat_lower"].clip(lower=0)

        historical = ts_data["y"].values
        fitted = forecast["yhat"].head(len(ts_data)).values
        mask = historical > 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((historical[mask] - fitted[mask]) / historical[mask])) * 100
            rmse = np.sqrt(np.mean((historical - fitted) ** 2))
        else:
            mape = 0.0
            rmse = 0.0

        metrics = {"mape": round(mape, 2), "rmse": round(rmse, 2)}
        return preds, metrics

    def forecast_xgboost(
        self,
        product_id: int,
        horizon_days: int = 30,
        region_id: Optional[int] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        ts_data = self._get_sales_timeseries(product_id, region_id)
        if len(ts_data) < 30 or not XGBOOST_AVAILABLE:
            return self.forecast_prophet(product_id, horizon_days, region_id)

        df = ts_data.copy()
        df["day_of_week"] = df["ds"].dt.dayofweek
        df["day_of_month"] = df["ds"].dt.day
        df["month"] = df["ds"].dt.month
        df["week_of_year"] = df["ds"].dt.isocalendar().week.astype(int)
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

        for lag in [1, 7, 14, 28]:
            df[f"lag_{lag}"] = df["y"].shift(lag)
        for win in [7, 14, 28]:
            df[f"rolling_mean_{win}"] = df["y"].rolling(win).mean()

        df = df.dropna()

        feature_cols = [c for c in df.columns if c not in ["ds", "y", "promotion_id"]]
        X = df[feature_cols].values
        y = df["y"].values

        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        model.fit(X_train, y_train)

        preds_test = model.predict(X_test)
        mask = y_test > 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_test[mask] - preds_test[mask]) / y_test[mask])) * 100
            rmse = np.sqrt(np.mean((y_test - preds_test) ** 2))
        else:
            mape = 0.0
            rmse = 0.0

        future_dates = pd.date_range(
            start=ts_data["ds"].max() + timedelta(days=1),
            periods=horizon_days,
            freq="D"
        )

        last_row = df.iloc[-1].copy()
        predictions = []
        current_y = df["y"].iloc[-1]
        y_history = list(df["y"].values[-28:])

        for future_date in future_dates:
            row = {
                "day_of_week": future_date.dayofweek,
                "day_of_month": future_date.day,
                "month": future_date.month,
                "week_of_year": future_date.isocalendar()[1],
                "is_weekend": 1 if future_date.dayofweek >= 5 else 0,
                "price": last_row["price"],
                "is_promotion": last_row["is_promotion"],
                "lag_1": y_history[-1] if len(y_history) >= 1 else 0,
                "lag_7": y_history[-7] if len(y_history) >= 7 else 0,
                "lag_14": y_history[-14] if len(y_history) >= 14 else 0,
                "lag_28": y_history[-28] if len(y_history) >= 28 else 0,
            }
            recent = y_history[-7:]
            row["rolling_mean_7"] = np.mean(recent) if recent else 0
            recent14 = y_history[-14:]
            row["rolling_mean_14"] = np.mean(recent14) if recent14 else 0
            recent28 = y_history[-28:]
            row["rolling_mean_28"] = np.mean(recent28) if recent28 else 0

            X_pred = np.array([[row[c] for c in feature_cols]])
            pred_val = max(0, model.predict(X_pred)[0])
            predictions.append({
                "ds": future_date,
                "yhat": round(pred_val, 2),
                "yhat_lower": round(pred_val * 0.7, 2),
                "yhat_upper": round(pred_val * 1.3, 2)
            })
            y_history.append(pred_val)

        preds_df = pd.DataFrame(predictions)
        metrics = {"mape": round(mape, 2), "rmse": round(rmse, 2)}
        return preds_df, metrics

    def _fallback_forecast(
        self,
        ts_data: pd.DataFrame,
        horizon_days: int
    ) -> Tuple[pd.DataFrame, Dict]:
        if len(ts_data) == 0:
            start = datetime.utcnow().date()
            base = 10.0
        else:
            start = ts_data["ds"].max().date() + timedelta(days=1)
            base = ts_data["y"].mean() if len(ts_data) > 0 else 10.0

        future_dates = [start + timedelta(days=i) for i in range(horizon_days)]
        seasonal_factor = np.array([1.0 + 0.1 * np.sin(i * 2 * np.pi / 7) for i in range(horizon_days)])
        trend_factor = np.array([1.0 + 0.001 * i for i in range(horizon_days)])

        preds = []
        for i, d in enumerate(future_dates):
            val = max(0, base * seasonal_factor[i] * trend_factor[i])
            preds.append({
                "ds": pd.Timestamp(d),
                "yhat": round(val, 2),
                "yhat_lower": round(val * 0.7, 2),
                "yhat_upper": round(val * 1.3, 2)
            })

        return pd.DataFrame(preds), {"mape": 25.0, "rmse": round(base * 0.3, 2)}

    def generate_forecast_explanation(
        self,
        product_id: int,
        model_type: str,
        region_id: Optional[int] = None
    ) -> Dict:
        ts_data = self._get_sales_timeseries(product_id, region_id)
        if len(ts_data) == 0:
            return {
                "key_drivers": [{"driver": "No historical data", "impact": "N/A"}],
                "seasonal_patterns": [],
                "trend_direction": "insufficient_data",
                "confidence_level": 0.0,
                "risk_factors": ["Insufficient historical data for reliable forecast"]
            }

        weekly_avg = ts_data.groupby(ts_data["ds"].dt.dayofweek)["y"].mean()
        peak_days = weekly_avg.nlargest(2).index.tolist()
        low_days = weekly_avg.nsmallest(2).index.tolist()
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        monthly_avg = ts_data.groupby(ts_data["ds"].dt.month)["y"].mean()
        peak_months = monthly_avg.nlargest(2).index.tolist()

        y = ts_data["y"].values
        if len(y) >= 14:
            first_half = y[:len(y)//2].mean()
            second_half = y[len(y)//2:].mean()
            if second_half > first_half * 1.05:
                trend = "increasing"
            elif second_half < first_half * 0.95:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"

        promotion_days = ts_data[ts_data["is_promotion"] == 1]["y"].mean() if (ts_data["is_promotion"] == 1).sum() > 0 else 0
        regular_days = ts_data[ts_data["is_promotion"] == 0]["y"].mean() if (ts_data["is_promotion"] == 0).sum() > 0 else 1
        promo_lift = ((promotion_days - regular_days) / regular_days * 100) if regular_days > 0 else 0

        confidence = min(0.95, 0.5 + (len(ts_data) / 730) * 0.45)

        return {
            "key_drivers": [
                {"driver": "Seasonality (weekly pattern)", "impact_percent": round(weekly_avg.std() / weekly_avg.mean() * 100, 1) if weekly_avg.mean() > 0 else 0},
                {"driver": f"Promotions (lift on promo days)", "impact_percent": round(promo_lift, 1)},
                {"driver": "Price sensitivity", "impact_percent": round(abs(ts_data["price"].corr(ts_data["y"])) * 100 if len(ts_data) > 1 else 0, 1)},
            ],
            "seasonal_patterns": [
                {"pattern": f"Peak days: {', '.join([day_names[d] for d in peak_days])}", "type": "weekly"},
                {"pattern": f"Low days: {', '.join([day_names[d] for d in low_days])}", "type": "weekly"},
                {"pattern": f"Peak months: {', '.join([str(m) for m in peak_months])}", "type": "monthly"},
            ],
            "trend_direction": trend,
            "confidence_level": round(confidence, 2),
            "risk_factors": [
                "Promotion calendar changes could significantly impact demand" if promo_lift > 10 else "Low promotion impact expected",
                "Weather events may affect foot traffic",
                "Competitor pricing actions could shift demand"
            ]
        }
