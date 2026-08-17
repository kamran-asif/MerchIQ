import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["TESTING"] = "true"

from fastapi.testclient import TestClient
from app.core.database import Base, engine, SessionLocal
from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "name" in data
    assert "modules" in data
    assert len(data["modules"]) == 6


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_create_and_list_products():
    # Create category first
    cat = client.post("/api/v1/categories/", json={"name": "TestCat", "margin_target": 0.3})
    assert cat.status_code == 200
    cat_id = cat.json()["id"]

    payload = {"sku": "TST-001", "name": "Test Product", "cost_price": 2.50, "base_price": 4.99, "category_id": cat_id}
    p = client.post("/api/v1/products/", json=payload)
    assert p.status_code == 200
    assert p.json()["sku"] == "TST-001"

    lst = client.get("/api/v1/products/")
    assert lst.status_code == 200
    assert len(lst.json()) >= 1


def test_sales_endpoints():
    lst = client.get("/api/v1/sales/summary")
    assert lst.status_code == 200
    summary = lst.json()
    for key in ["total_revenue", "total_units", "gross_margin"]:
        assert key in summary


def test_kpi_endpoint():
    r = client.get("/api/v1/kpis")
    assert r.status_code == 200
    data = r.json()
    for key in ["total_revenue", "gross_margin", "inventory_turnover"]:
        assert key in data


def test_forecast_endpoint():
    # Create product for forecast
    cat = client.post("/api/v1/categories/", json={"name": "ForecastCat", "margin_target": 0.3})
    cat_id = cat.json()["id"]
    product = client.post("/api/v1/products/", json={
        "sku": "FR-001", "name": "Forecast Product",
        "cost_price": 1.0, "base_price": 2.99, "category_id": cat_id
    })
    pid = product.json()["id"]

    r = client.post("/api/v1/forecast", json={
        "product_id": pid, "horizon_days": 14, "model_type": "prophet"
    })
    assert r.status_code == 200
    data = r.json()
    assert "predictions" in data
    assert len(data["predictions"]) == 14


def test_inventory_optimization_endpoint():
    r = client.get("/api/v1/inventory/optimize")
    assert r.status_code == 200


def test_pricing_recommendation_fallback():
    # First create a product if none exists
    cat = client.post("/api/v1/categories/", json={"name": "PricingCat2", "margin_target": 0.3})
    cat_id = cat.json()["id"]
    p = client.post("/api/v1/products/", json={
        "sku": "PR-001", "name": "Pricing Test",
        "cost_price": 2.0, "base_price": 5.99, "category_id": cat_id
    })
    pid = p.json()["id"]

    r = client.get(f"/api/v1/pricing/recommendation/{pid}")
    assert r.status_code == 200
    data = r.json()
    for key in ["current_price", "recommended_price", "reasoning"]:
        assert key in data


def test_promotion_recommendation():
    r = client.get("/api/v1/promotions/recommendations")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 5


def test_rca_endpoint():
    r = client.post("/api/v1/root-cause-analysis", params={"metric": "revenue"})
    assert r.status_code == 200
    data = r.json()
    for key in ["primary_causes", "recommendations", "confidence_score"]:
        assert key in data


def test_executive_report():
    r = client.get("/api/v1/executive-report", params={"period": "monthly"})
    assert r.status_code == 200
    data = r.json()
    for key in ["summary", "top_performers", "key_insights", "recommendations"]:
        assert key in data


def test_copilot_query():
    queries = [
        "Show me the KPI dashboard",
        "Forecast demand for product 1 next 30 days",
        "Why did revenue drop?",
        "What should we reorder?",
        "Recommend price for product 1",
        "Generate monthly executive report",
        "Plan next quarter strategy",
    ]
    for q in queries:
        r = client.post("/api/v1/copilot/query", json={"query": q})
        assert r.status_code == 200, f"Query failed: {q}"
        data = r.json()
        assert "answer" in data
        assert "confidence_score" in data


def test_copilot_query_types():
    r = client.get("/api/v1/copilot/query-types")
    assert r.status_code == 200
    assert isinstance(r.json(), dict)
    assert "query_types" in r.json()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    pytest.main([__file__, "-v"])
