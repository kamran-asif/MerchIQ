from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import schemas
from app.services.forecasting.service import DemandForecastingService
from app.models import models

router = APIRouter()


@router.post("/forecast", response_model=schemas.ForecastResponse)
def create_forecast(
    request: schemas.ForecastRequest,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    service = DemandForecastingService(db)

    if request.model_type.lower() == "xgboost":
        preds_df, metrics = service.forecast_xgboost(
            request.product_id, request.horizon_days, request.region_id
        )
        explanation = service.generate_forecast_explanation(
            request.product_id, "xgboost", request.region_id
        )
    else:
        preds_df, metrics = service.forecast_prophet(
            request.product_id, request.horizon_days, request.region_id
        )
        explanation = service.generate_forecast_explanation(
            request.product_id, "prophet", request.region_id
        )

    forecast_record = models.Forecast(
        product_id=request.product_id,
        region_id=request.region_id,
        model_type=request.model_type,
        forecast_date=preds_df["ds"].min().date(),
        horizon_days=request.horizon_days,
        mape=metrics["mape"],
        rmse=metrics["rmse"]
    )
    db.add(forecast_record)
    db.flush()

    for _, row in preds_df.iterrows():
        item = models.ForecastItem(
            forecast_id=forecast_record.id,
            date=row["ds"].date(),
            predicted_value=row["yhat"],
            lower_bound=row["yhat_lower"],
            upper_bound=row["yhat_upper"]
        )
        db.add(item)
    db.commit()

    predictions = [
        schemas.ForecastItemData(
            date=row["ds"].date(),
            predicted_value=row["yhat"],
            lower_bound=row["yhat_lower"],
            upper_bound=row["yhat_upper"]
        )
        for _, row in preds_df.iterrows()
    ]

    exp_str = (
        f"Trend: {explanation['trend_direction'].upper()}. "
        f"Key drivers: {', '.join([d['driver'] for d in explanation['key_drivers']])}. "
        f"Confidence: {explanation['confidence_level']*100:.0f}%."
    )

    return schemas.ForecastResponse(
        product_id=product.id,
        product_name=product.name,
        model_type=request.model_type,
        horizon_days=request.horizon_days,
        mape=metrics["mape"],
        rmse=metrics["rmse"],
        predictions=predictions,
        explanation=exp_str
    )


@router.get("/products/{product_id}/forecast-explainability", response_model=schemas.ForecastExplainability)
def get_forecast_explainability(
    product_id: int,
    model_type: str = "prophet",
    region_id: int = None,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    service = DemandForecastingService(db)
    explanation = service.generate_forecast_explanation(product_id, model_type, region_id)
    return schemas.ForecastExplainability(
        product_id=product_id,
        key_drivers=explanation["key_drivers"],
        seasonal_patterns=explanation["seasonal_patterns"],
        trend_direction=explanation["trend_direction"],
        confidence_level=explanation["confidence_level"],
        risk_factors=explanation["risk_factors"]
    )


@router.get("/forecasts/{product_id}/history")
def get_forecast_history(
    product_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    forecasts = db.query(models.Forecast).filter(
        models.Forecast.product_id == product_id
    ).order_by(models.Forecast.created_at.desc()).limit(limit).all()

    result = []
    for f in forecasts:
        items = db.query(models.ForecastItem).filter(models.ForecastItem.forecast_id == f.id).all()
        result.append({
            "forecast_id": f.id,
            "model_type": f.model_type,
            "forecast_date": f.forecast_date,
            "horizon_days": f.horizon_days,
            "mape": f.mape,
            "rmse": f.rmse,
            "created_at": f.created_at,
            "items_count": len(items)
        })
    return result
