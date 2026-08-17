import re
import json
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.utils import get_logger
from app.services.bi.service import BusinessIntelligenceService
from app.services.forecasting.service import DemandForecastingService
from app.services.inventory.service import InventoryOptimizationService
from app.services.pricing.service import PricingIntelligenceService
from app.services.promotions.service import PromotionAnalyticsService

logger = get_logger(__name__)


class QueryType(str, Enum):
    FORECAST_EXPLAIN = "forecast_explainability"
    FORECAST_REQUEST = "forecast_request"
    KPI_ANALYSIS = "kpi_analysis"
    KPI_TREND = "kpi_trend"
    RCA = "root_cause_analysis"
    EXECUTIVE_REPORT = "executive_report"
    INVENTORY_RECOMMENDATION = "inventory_recommendation"
    PRICING_RECOMMENDATION = "pricing_recommendation"
    PROMOTION_EVALUATION = "promotion_evaluation"
    PROMOTION_RECOMMENDATION = "promotion_recommendation"
    SALES_PERFORMANCE = "sales_performance"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    ASSISTED_PLANNING = "assisted_planning"
    GENERAL_INFO = "general_info"


QUERY_PATTERNS = {
    QueryType.FORECAST_EXPLAIN: [
        r"explain.*forecast",
        r"why.*forecast",
        r"forecast.*driver",
        r"driving.*forecast",
        r"demand.*explain",
    ],
    QueryType.FORECAST_REQUEST: [
        r"forecast.*demand",
        r"demand.*forecast",
        r"predict.*sale",
        r"how many.*will sell",
        r"forecast.*(next|future)",
        r"sales.*projection",
    ],
    QueryType.KPI_ANALYSIS: [
        r"(kpi|performance).*overview",
        r"dashboard.*summary",
        r"key.*metric",
        r"how.*(doing|perform)",
        r"current.*(revenue|margin|profit)",
        r"total.*(revenue|sale|profit)",
    ],
    QueryType.KPI_TREND: [
        r"trend.*(revenue|sale|kpi)",
        r"(growing|declining|increasing|decreasing).*(revenue|sale|profit)",
        r"compare.*period",
        r"vs.*last",
        r"year.*over.*year",
        r"month.*over.*month",
    ],
    QueryType.RCA: [
        r"root cause",
        r"why.*(drop|decline|decrease|fall)",
        r"what.*causing",
        r"reason.*(low|poor|bad)",
        r"diagnose",
        r"investigate",
    ],
    QueryType.EXECUTIVE_REPORT: [
        r"executive.*report",
        r"management.*report",
        r"monthly.*report",
        r"quarterly.*report",
        r"generate.*report",
        r"business.*summary",
    ],
    QueryType.INVENTORY_RECOMMENDATION: [
        r"reorder.*(product|item|sku)",
        r"when.*order",
        r"how much.*inventory",
        r"purchase.*order",
        r"stock.*(level|optimize)",
        r"inventory.*recommend",
        r"low.*stock",
        r"stockout",
    ],
    QueryType.PRICING_RECOMMENDATION: [
        r"price.*recommend",
        r"should.*(increase|decrease|change|raise|lower).*price",
        r"optimal.*price",
        r"reprice",
        r"pricing.*strategy",
        r"elasticity",
    ],
    QueryType.PROMOTION_EVALUATION: [
        r"promotion.*(effect|perform|roi|work|success)",
        r"did.*promotion.*(work|help)",
        r"roi.*promotion",
        r"promotion.*result",
    ],
    QueryType.PROMOTION_RECOMMENDATION: [
        r"what.*promotion.*(run|do|launch)",
        r"recommend.*promotion",
        r"promotion.*idea",
        r"how.*(promote|discount)",
        r"best.*promotion",
    ],
    QueryType.SALES_PERFORMANCE: [
        r"(top|best).*(selling|performer|product)",
        r"(worst|bottom|underperform).*(performer|product|selling)",
        r"sales.*(by|per).*(category|region|store|product)",
        r"which.*(sell|perform).*(best|most|worst|least)",
        r"ranking.*sale",
    ],
    QueryType.COMPETITOR_ANALYSIS: [
        r"competitor.*price",
        r"price.*(compare|vs|versus).*competitor",
        r"market.*position",
        r"competitive.*(landscape|analysis)",
        r"how.*(we|our).*compare",
    ],
    QueryType.ASSISTED_PLANNING: [
        r"plan.*(next|quarter|month|season|year)",
        r"planning.*(assist|help|suggest|recommend)",
        r"strategy.*(suggest|recommend)",
        r"what.*should.*(we|i).*do",
        r"action.*(plan|item)",
        r"(improve|grow).*business",
    ]
}


RAG_KNOWLEDGE_BASE = [
    {
        "id": 1,
        "topic": "Inventory Optimization Best Practices",
        "content": "Effective inventory management uses EOQ (Economic Order Quantity) to balance holding costs vs ordering costs. Safety stock should cover 1.65 standard deviations of demand during lead time for 95% service level. ABC analysis categorizes SKUs: A-class (top 20% SKUs = 80% revenue) need tight control, C-class can use automated reordering.",
        "keywords": ["inventory", "eoq", "safety stock", "abc analysis", "stockout", "holding cost"]
    },
    {
        "id": 2,
        "topic": "Pricing Strategy Framework",
        "content": "Price elasticity < -1 means elastic (lower price = more revenue), > -1 means inelastic. Use competitive pricing for commodities, value-based for differentiated products. Psychological pricing at $X.99 increases perceived value. Price skimming works for innovations, penetration pricing for market entry.",
        "keywords": ["pricing", "elasticity", "competitive", "margin", "discount", "skimming", "penetration"]
    },
    {
        "id": 3,
        "topic": "Promotion ROI Optimization",
        "content": "Promotions should target specific goals: Flash Sales (3-day, 20-30% off) for urgency, BOGO for volume, Loyalty Exclusives for retention. Measure incremental lift vs baseline (not just promo period sales). Target 150%+ ROI. Cannibalization above 10% signals promotion design issues.",
        "keywords": ["promotion", "roi", "lift", "bogo", "flash sale", "discount", "cannibalization"]
    },
    {
        "id": 4,
        "topic": "Demand Forecasting Methods",
        "content": "Use Prophet for seasonal patterns and holiday effects, XGBoost for complex feature interactions including promotions/weather/price. Combine forecasts with weighted ensemble (MAPE-based weights). Always evaluate holdout period MAPE. Re-calibrate models monthly. Typical retail MAPE targets: 10-15% for stable categories, 20-30% for volatile.",
        "keywords": ["forecast", "prophet", "xgboost", "mape", "seasonality", "ensemble", "demand"]
    },
    {
        "id": 5,
        "topic": "Retail KPI Benchmarks",
        "content": "Healthy retail benchmarks: Gross Margin 30-45%, Inventory Turnover 4-8x/year, Stockout Rate <3%, Average Order Value growth >CPI, Promotion ROI >150%, Customer Retention >60%. Compare performance to industry segment and historical trends.",
        "keywords": ["kpi", "benchmark", "margin", "turnover", "stockout", "aov", "roi"]
    },
    {
        "id": 6,
        "topic": "Weather Impact on Retail",
        "content": "Temperature changes of 5°C+ shift category demand: cold = outerwear, hot = cooling/beach items. Rain reduces foot traffic 15-30% but boosts online. Severe weather requires emergency markdowns on seasonal goods. Always include weather features in forecasting models for regions with variable climate.",
        "keywords": ["weather", "temperature", "rain", "seasonal", "foot traffic", "demand"]
    },
    {
        "id": 7,
        "topic": "Competitive Intelligence Playbook",
        "content": "Track competitor pricing weekly on A-class SKUs. Price index <0.9 = price leader (good for traffic), >1.1 = premium (must justify). Match competitor promotions only on traffic-driving items. Competitor stockouts are opportunities to capture market share.",
        "keywords": ["competitor", "price index", "benchmark", "market share", "pricing war"]
    },
    {
        "id": 8,
        "topic": "Root Cause Analysis Methodology",
        "content": "When KPIs deviate >5% from expected: 1) Validate data integrity across 6 dimensions, 2) Check timing (holidays, promotions, seasonality), 3) Isolate by dimension (region/store/category), 4) Correlate with external factors (weather, competitor), 5) Quantify impact before acting. Always run RCA before large strategy changes.",
        "keywords": ["rca", "root cause", "deviation", "methodology", "diagnostic", "6 dimensions"]
    }
]


class RetailCopilotService:
    def __init__(self, db: Session):
        self.db = db
        self.bi = BusinessIntelligenceService(db)
        self.forecasting = DemandForecastingService(db)
        self.inventory = InventoryOptimizationService(db)
        self.pricing = PricingIntelligenceService(db)
        self.promotions = PromotionAnalyticsService(db)

    def classify_query(self, query: str) -> Tuple[QueryType, float]:
        q = query.lower()
        best_type = QueryType.GENERAL_INFO
        best_score = 0.0

        for qtype, patterns in QUERY_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, q)
                if match:
                    score = len(match.group()) / max(1, len(q)) * 2
                    score = min(1.0, score + 0.5)
                    if score > best_score:
                        best_score = score
                        best_type = qtype

        return best_type, round(best_score, 2)

    def retrieve_rag_context(self, query: str, top_k: int = 3) -> List[Dict]:
        q_words = set(re.findall(r'\w+', query.lower()))
        scored_docs = []
        for doc in RAG_KNOWLEDGE_BASE:
            doc_words = set(doc["keywords"])
            overlap = len(q_words & doc_words)
            topic_words = set(re.findall(r'\w+', doc["topic"].lower()))
            overlap += len(q_words & topic_words)
            score = overlap / max(1, len(q_words))
            scored_docs.append((score, doc))
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k] if score > 0]

    def extract_entities(self, query: str) -> Dict:
        entities = {}
        q = query.lower()

        product_match = re.search(r"(product|sku|item)\s*(#?\d+)", q)
        if product_match:
            try:
                entities["product_id"] = int(product_match.group(2))
            except Exception:
                pass

        store_match = re.search(r"store\s*(#?\d+)", q)
        if store_match:
            try:
                entities["store_id"] = int(store_match.group(2))
            except Exception:
                pass

        region_match = re.search(r"region\s*(#?\d+)", q)
        if region_match:
            try:
                entities["region_id"] = int(region_match.group(2))
            except Exception:
                pass

        promo_match = re.search(r"(promotion|promo)\s*(#?\d+)", q)
        if promo_match:
            try:
                entities["promotion_id"] = int(promo_match.group(2))
            except Exception:
                pass

        day_match = re.search(r"(\d+)\s*(day|days)", q)
        if day_match:
            entities["days"] = int(day_match.group(1))

        if "next week" in q or "7 day" in q:
            entities["horizon_days"] = 7
        elif "next month" in q or "30 day" in q:
            entities["horizon_days"] = 30
        elif "quarter" in q or "90 day" in q:
            entities["horizon_days"] = 90

        if re.search(r"(xgboost|gradient.*boost|tree.*based)", q):
            entities["model_type"] = "xgboost"
        else:
            entities["model_type"] = "prophet"

        if re.search(r"(profit|margin)", q):
            entities["objective"] = "profit"
        elif re.search(r"(revenue|sale|top.*line)", q):
            entities["objective"] = "revenue"
        elif re.search(r"(market.*share|volume|unit)", q):
            entities["objective"] = "market_share"

        period = None
        if "weekly" in q or "week" in q and "last" in q:
            period = "weekly"
        elif "quarterly" in q or "quarter" in q:
            period = "quarterly"
        else:
            period = "monthly"
        entities["period"] = period

        metric = None
        if "revenue" in q or "sale" in q:
            metric = "revenue"
        elif "margin" in q or "profit" in q and not re.search(r"gross.*margin", q):
            metric = "gross_margin"
        elif "unit" in q or "volume" in q:
            metric = "units_sold"
        elif "turnover" in q:
            metric = "inventory_turnover"
        elif "stockout" in q:
            metric = "stockout_rate"
        elif "aov" in q or "order value" in q:
            metric = "avg_order_value"
        if metric:
            entities["metric"] = metric

        return entities

    def process_query(self, query: str, context_filters: Optional[Dict] = None) -> Dict:
        query_type, confidence = self.classify_query(query)
        entities = self.extract_entities(query)
        if context_filters:
            entities.update(context_filters)
        rag_context = self.retrieve_rag_context(query)

        try:
            result = self._route_and_execute(query_type, entities, query)
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            result = self._fallback_response(query, entities)

        sources = self._build_sources_list(query_type, entities)
        if rag_context:
            sources.extend([f"KB: {doc['topic']}" for doc in rag_context])

        return {
            "query_type": query_type.value,
            "answer": result.get("answer", ""),
            "data_points": result.get("data_points"),
            "chart_spec": result.get("chart_spec"),
            "related_insights": result.get("related_insights"),
            "confidence_score": round(min(1.0, confidence * 0.6 + result.get("confidence", 0.4)), 2),
            "sources_used": sources
        }

    def _route_and_execute(self, query_type: QueryType, entities: Dict, query: str) -> Dict:
        handlers = {
            QueryType.FORECAST_EXPLAIN: self._handle_forecast_explain,
            QueryType.FORECAST_REQUEST: self._handle_forecast_request,
            QueryType.KPI_ANALYSIS: self._handle_kpi_analysis,
            QueryType.KPI_TREND: self._handle_kpi_trend,
            QueryType.RCA: self._handle_rca,
            QueryType.EXECUTIVE_REPORT: self._handle_executive_report,
            QueryType.INVENTORY_RECOMMENDATION: self._handle_inventory,
            QueryType.PRICING_RECOMMENDATION: self._handle_pricing,
            QueryType.PROMOTION_EVALUATION: self._handle_promo_eval,
            QueryType.PROMOTION_RECOMMENDATION: self._handle_promo_rec,
            QueryType.SALES_PERFORMANCE: self._handle_sales_perf,
            QueryType.COMPETITOR_ANALYSIS: self._handle_competitor,
            QueryType.ASSISTED_PLANNING: self._handle_planning,
            QueryType.GENERAL_INFO: self._handle_general,
        }
        handler = handlers.get(query_type, self._handle_general)
        return handler(entities, query)

    def _handle_forecast_explain(self, entities, query) -> Dict:
        product_id = entities.get("product_id") or 1
        exp = self.forecasting.generate_forecast_explanation(
            product_id, entities.get("model_type", "prophet"), entities.get("region_id")
        )
        drivers = "\n".join([f"- {d['driver']}: {d['impact_percent']}% impact" for d in exp["key_drivers"]])
        answer = (
            f"**Forecast Explanation for Product #{product_id}**\n\n"
            f"Overall trend is **{exp['trend_direction']}** with {exp['confidence_level']*100:.0f}% confidence.\n\n"
            f"**Key Demand Drivers:**\n{drivers}\n\n"
            f"**Seasonal Patterns:**\n" + "\n".join([f"- {p['pattern']}" for p in exp["seasonal_patterns"]]) + "\n\n"
            f"**Risk Factors:**\n" + "\n".join([f"- {r}" for r in exp["risk_factors"]])
        )
        return {
            "answer": answer,
            "data_points": exp["key_drivers"] + exp["seasonal_patterns"],
            "confidence": 0.85,
            "related_insights": [
                f"Model confidence: {exp['confidence_level']*100:.0f}%",
                f"Trend direction: {exp['trend_direction']}"
            ]
        }

    def _handle_forecast_request(self, entities, query) -> Dict:
        product_id = entities.get("product_id") or 1
        horizon = entities.get("horizon_days", 30)
        model = entities.get("model_type", "prophet")

        if model == "xgboost":
            preds, metrics = self.forecasting.forecast_xgboost(
                product_id, horizon, entities.get("region_id")
            )
        else:
            preds, metrics = self.forecasting.forecast_prophet(
                product_id, horizon, entities.get("region_id")
            )

        total_units = int(preds["yhat"].sum())
        lower_total = int(preds["yhat_lower"].sum())
        upper_total = int(preds["yhat_upper"].sum())
        avg_daily = round(preds["yhat"].mean(), 1)

        peak_row = preds.loc[preds["yhat"].idxmax()]
        low_row = preds.loc[preds["yhat"].idxmin()]

        answer = (
            f"**{horizon}-Day Demand Forecast (Product #{product_id}) - {model.upper()} Model**\n\n"
            f"**Summary:**\n"
            f"- Total predicted units: **{total_units:,}** (range: {lower_total:,} - {upper_total:,})\n"
            f"- Average daily demand: **{avg_daily} units**\n"
            f"- Model accuracy: MAPE {metrics['mape']}% | RMSE {metrics['rmse']}\n\n"
            f"**Peak demand:** {int(peak_row['yhat'])} units on {peak_row['ds'].date()}\n"
            f"**Lowest demand:** {int(low_row['yhat'])} units on {low_row['ds'].date()}\n\n"
            f"Recommendation: Plan inventory with 95% confidence upper bound ({upper_total:,} units) to prevent stockouts."
        )

        chart_data = [
            {"date": row["ds"].date().isoformat(), "predicted": row["yhat"],
             "lower": row["yhat_lower"], "upper": row["yhat_upper"]}
            for _, row in preds.iterrows()
        ]

        return {
            "answer": answer,
            "data_points": [
                {"metric": "Total predicted units", "value": total_units},
                {"metric": "Daily average", "value": avg_daily},
                {"metric": "MAPE", "value": f"{metrics['mape']}%"},
                {"metric": "Peak day", "value": str(peak_row['ds'].date())}
            ],
            "chart_spec": {"type": "line_chart", "data": chart_data, "title": f"{horizon}-Day Demand Forecast"},
            "confidence": 0.8,
            "related_insights": [
                f"Use upper bound ({upper_total:,}) for safety stock planning",
                f"Peak period may need promotional support to maximize revenue"
            ]
        }

    def _handle_kpi_analysis(self, entities, query) -> Dict:
        kpi = self.bi.get_kpi_dashboard(entities.get("region_id"), entities.get("store_id"))

        status_rev = "📈 Growing" if kpi.revenue_growth > 0 else "📉 Declining"
        status_margin = "📈 Improving" if kpi.margin_growth > 0 else "📉 Contracting"

        answer = (
            f"**KPI Dashboard Overview**\n\n"
            f"**Revenue:** ${kpi.total_revenue:,.2f} — {status_rev} ({kpi.revenue_growth:+.1f}% vs prior period)\n"
            f"**Units Sold:** {kpi.total_units_sold:,} — ({kpi.units_growth:+.1f}%)\n"
            f"**Gross Margin:** {kpi.gross_margin:.1f}% — {status_margin} ({kpi.margin_growth:+.1f}pp)\n\n"
            f"**Operational Efficiency:**\n"
            f"- Average Order Value: ${kpi.avg_order_value:.2f}\n"
            f"- Inventory Turnover: {kpi.inventory_turnover:.2f}x (target: 4-8x)\n"
            f"- Stockout Rate: {kpi.stockout_rate:.1f}% (target: <3%)\n"
            f"- Promotion ROI: {kpi.promotion_roi:.0f}% (target: >150%)\n\n"
            f"{'⚠️ Attention needed: Stockout rate exceeds 3% target.' if kpi.stockout_rate > 3 else '✅ Stockout rate within acceptable range.'}"
        )

        data_points = [
            {"metric": "Revenue", "value": f"${kpi.total_revenue:,.2f}", "growth": f"{kpi.revenue_growth:+.1f}%"},
            {"metric": "Gross Margin", "value": f"{kpi.gross_margin:.1f}%", "growth": f"{kpi.margin_growth:+.1f}pp"},
            {"metric": "Units Sold", "value": f"{kpi.total_units_sold:,}", "growth": f"{kpi.units_growth:+.1f}%"},
            {"metric": "Inventory Turnover", "value": f"{kpi.inventory_turnover:.2f}x"},
            {"metric": "Promotion ROI", "value": f"{kpi.promotion_roi:.0f}%"},
        ]

        return {
            "answer": answer,
            "data_points": data_points,
            "chart_spec": {"type": "kpi_cards", "data": data_points},
            "confidence": 0.95
        }

    def _handle_kpi_trend(self, entities, query) -> Dict:
        kpi = self.bi.get_kpi_dashboard(entities.get("region_id"), entities.get("store_id"))

        analysis = []
        if kpi.revenue_growth > 10:
            analysis.append("🚀 Strong revenue acceleration — double-digit growth detected")
        elif kpi.revenue_growth > 0:
            analysis.append("📈 Positive revenue trajectory consistent with seasonal expectations")
        elif kpi.revenue_growth > -5:
            analysis.append("⚠️ Mild revenue softening — investigate regional/category mix")
        else:
            analysis.append("🔴 Significant revenue decline — RUN ROOT CAUSE ANALYSIS immediately")

        if kpi.margin_growth > 1:
            analysis.append("💹 Margin expansion suggests effective pricing/cost optimization")
        elif kpi.margin_growth < -1:
            analysis.append("📉 Margin compression — review discount depth and COGS trends")

        answer = (
            f"**Performance Trend Analysis**\n\n"
            f"**Revenue Trajectory:** {kpi.revenue_growth:+.1f}% period-over-period\n"
            f"**Unit Volume Trend:** {kpi.units_growth:+.1f}%\n"
            f"**Margin Trajectory:** {kpi.margin_growth:+.1f} percentage points\n\n"
            f"**Analysis:**\n" + "\n".join([f"- {a}" for a in analysis])
        )

        return {
            "answer": answer,
            "data_points": [
                {"metric": "Revenue growth", "value": f"{kpi.revenue_growth:+.1f}%"},
                {"metric": "Units growth", "value": f"{kpi.units_growth:+.1f}%"},
                {"metric": "Margin change", "value": f"{kpi.margin_growth:+.1f}pp"}
            ],
            "confidence": 0.9,
            "related_insights": analysis
        }

    def _handle_rca(self, entities, query) -> Dict:
        metric = entities.get("metric", "revenue")
        rca = self.bi.run_root_cause_analysis(metric, entities.get("region_id"), entities.get("store_id"))

        causes_text = "\n".join([
            f"  {i+1}. [{c['severity'].upper()}] {c['dimension']} — {c['factor']} ({c['contribution_pct']}% contribution)"
            for i, c in enumerate(rca.primary_causes)
        ]) if rca.primary_causes else "  No primary causes identified."

        contrib_text = "\n".join([
            f"  {i+1}. {c['dimension']} — {c['factor']} ({c['contribution_pct']}% contribution)"
            for i, c in enumerate(rca.contributing_factors)
        ]) if rca.contributing_factors else "  No contributing factors identified."

        answer = (
            f"**🔍 Root Cause Analysis — {rca.metric_name.upper()}**\n\n"
            f"**Current Value:** {rca.current_value} | **Expected:** {rca.expected_value}\n"
            f"**Deviation:** {rca.deviation:+.1f}% | **Confidence:** {rca.confidence_score*100:.0f}%\n\n"
            f"**🎯 Primary Causes:**\n{causes_text}\n\n"
            f"**📊 Contributing Factors:**\n{contrib_text}\n\n"
            f"**✅ Recommended Actions:**\n" + "\n".join([f"  {i+1}. {r}" for i, r in enumerate(rca.recommendations)])
        )

        return {
            "answer": answer,
            "data_points": rca.primary_causes,
            "confidence": rca.confidence_score,
            "related_insights": rca.recommendations
        }

    def _handle_executive_report(self, entities, query) -> Dict:
        period = entities.get("period", "monthly")
        report = self.bi.generate_executive_report(entities.get("region_id"), period)

        top_5_names = [f"{i+1}. {t['product_name']} (${t['revenue']:,.0f})" for i, t in enumerate(report.top_performers[:5])]
        bot_5_names = [f"{i+1}. {t['product_name']} (${t['revenue']:,.0f})" for i, t in enumerate(report.underperformers[:5])]

        answer = (
            f"**📋 EXECUTIVE BUSINESS REPORT — {report.report_period.upper()}**\n"
            f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            f"**📝 Executive Summary:**\n{report.summary}\n\n"
            f"**🔑 Key Performance Indicators:**\n"
            f"- Revenue: ${report.kpi_summary.total_revenue:,.0f} ({report.kpi_summary.revenue_growth:+.1f}%)\n"
            f"- Gross Margin: {report.kpi_summary.gross_margin:.1f}% ({report.kpi_summary.margin_growth:+.1f}pp)\n"
            f"- Units Sold: {report.kpi_summary.total_units_sold:,} ({report.kpi_summary.units_growth:+.1f}%)\n"
            f"- Inventory Turnover: {report.kpi_summary.inventory_turnover:.1f}x\n\n"
            f"**⭐ Top 5 Performers:**\n" + "\n".join(top_5_names) + "\n\n"
            f"**⚠️ Underperformers (Action Required):**\n" + "\n".join(bot_5_names) + "\n\n"
            f"**💡 Key Insights:**\n" + "\n".join([f"- {x}" for x in report.key_insights]) + "\n\n"
            f"**🎯 Strategic Recommendations:**\n" + "\n".join([f"- {x}" for x in report.recommendations]) + "\n\n"
            f"**🚨 Risk Alerts:**\n" + "\n".join([f"- {x}" for x in report.risk_alerts])
        )

        return {
            "answer": answer,
            "data_points": report.top_performers + report.underperformers,
            "confidence": 0.92,
            "related_insights": report.key_insights + report.recommendations
        }

    def _handle_inventory(self, entities, query) -> Dict:
        store_id = entities.get("store_id")
        suggestions = self.inventory.generate_purchase_order_suggestions(store_id)

        if not suggestions:
            return {
                "answer": "✅ All inventory levels are currently optimal. No purchase orders recommended at this time. Continue monitoring reorder points daily.",
                "confidence": 0.85
            }

        total_cost = sum(s["estimated_cost"] for s in suggestions)
        critical = [s for s in suggestions if s.get("priority") == 1][:5]
        non_critical = [s for s in suggestions if s.get("priority") == 2][:5]

        answer = (
            f"**📦 Inventory Optimization Recommendations**\n"
            f"Total SKUs requiring action: **{len(suggestions)}**\n"
            f"Estimated PO cost: **${total_cost:,.2f}**\n\n"
        )

        if critical:
            answer += "**🔴 CRITICAL / HIGH PRIORITY (stockout risk):**\n"
            for s in critical:
                answer += f"- {s['product_name']}: Order {s['recommended_order']} units (${s['estimated_cost']:,.2f}) — risk: {s['stockout_risk']}\n"

        if non_critical:
            answer += "\n**🟡 STANDARD REORDER:**\n"
            for s in non_critical:
                answer += f"- {s['product_name']}: Order {s['recommended_order']} units (${s['estimated_cost']:,.2f})\n"

        kpis = self.inventory.get_inventory_kpis(store_id)
        answer += (
            f"\n**📊 Inventory Health:**\n"
            f"- Stockout rate: {kpis['stockout_rate']:.1f}% (target <3%)\n"
            f"- Inventory turnover: {kpis['inventory_turnover']:.2f}x\n"
            f"- Overstocked SKUs: {kpis['overstocked_sku_count']} ({kpis['overstocked_rate']:.1f}%)"
        )

        return {
            "answer": answer,
            "data_points": suggestions[:10],
            "confidence": 0.88,
            "related_insights": [
                f"Total PO value: ${total_cost:,.2f}",
                f"Stockout risk items: {len(critical)}",
                f"Aggregate stockout rate: {kpis['stockout_rate']:.1f}%"
            ]
        }

    def _handle_pricing(self, entities, query) -> Dict:
        product_id = entities.get("product_id") or 1
        objective = entities.get("objective", "profit")

        rec = self.pricing.generate_pricing_recommendation(product_id, objective)
        if not rec:
            return {"answer": "Unable to generate pricing recommendation at this time.", "confidence": 0.5}

        direction = "INCREASE" if rec["recommended_price"] > rec["current_price"] else ("DECREASE" if rec["recommended_price"] < rec["current_price"] else "HOLD")
        pct_change = rec["recommended_price"] - rec["current_price"]
        pct_change = pct_change / rec["current_price"] * 100 if rec["current_price"] > 0 else 0

        answer = (
            f"**💰 Pricing Recommendation — {rec['product_name']}**\n\n"
            f"**Current Price:** ${rec['current_price']:.2f}\n"
            f"**Recommended Price:** ${rec['recommended_price']:.2f} ({direction} {abs(pct_change):.1f}%)\n\n"
            f"**Impact Analysis:**\n"
            f"- Demand change: {rec['expected_demand_change_pct']:+.1f}% (elasticity: {rec['price_elasticity']:.3f})\n"
            f"- Revenue change: {rec['expected_revenue_change_pct']:+.1f}%\n"
            f"- Margin impact: {rec['margin_impact_pct']:+.1f}pp\n"
        )

        if rec.get("competitor_avg_price"):
            answer += f"- Competitor avg price: ${rec['competitor_avg_price']:.2f}\n"

        answer += f"\n**📋 Rationale:** {rec['reasoning']}\n\n"

        if rec.get("alternative_prices"):
            answer += "**Alternative Scenarios:**\n"
            for alt in rec["alternative_prices"][:3]:
                answer += (f"- ${alt['price']:.2f} ({alt['price_change_pct']:+.1f}%): "
                          f"Profit ${alt['expected_daily_profit']:.2f}/day | "
                          f"Margin {alt['expected_margin_pct']:.1f}%\n")

        return {
            "answer": answer,
            "data_points": [
                {"metric": "Current price", "value": f"${rec['current_price']:.2f}"},
                {"metric": "Recommended price", "value": f"${rec['recommended_price']:.2f}"},
                {"metric": "Price elasticity", "value": f"{rec['price_elasticity']:.3f}"},
                {"metric": "Expected demand impact", "value": f"{rec['expected_demand_change_pct']:+.1f}%"},
                {"metric": "Expected revenue impact", "value": f"{rec['expected_revenue_change_pct']:+.1f}%"}
            ],
            "confidence": 0.82
        }

    def _handle_promo_eval(self, entities, query) -> Dict:
        promo_id = entities.get("promotion_id")
        if not promo_id:
            return self._handle_promo_rec(entities, query)

        analysis = self.promotions.analyze_promotion_effectiveness(promo_id)
        if not analysis:
            return {"answer": "Promotion not found or insufficient data.", "confidence": 0.5}

        verdict = "✅ EXCELLENT" if analysis["roi"] >= 200 else ("👍 GOOD" if analysis["roi"] >= 100 else "⚠️ BELOW TARGET")

        answer = (
            f"**🎯 Promotion Performance: {analysis['promotion_name']}**\n"
            f"Overall Rating: **{verdict}** (ROI: {analysis['roi']:.0f}%)\n\n"
            f"**Promotion Details:**\n"
            f"- Type: {analysis['promotion_type']} | Duration: {analysis['promo_duration_days']} days\n"
            f"- Budget: ${analysis['budget']:,.2f} | Discount: {analysis['discount_percent']}% / ${analysis['discount_amount']:.2f}\n\n"
            f"**📈 Results:**\n"
            f"- Revenue: ${analysis['total_revenue']:,.2f} | Units: {analysis['total_units_sold']:,}\n"
            f"- Incremental revenue: ${analysis['incremental_revenue']:,.2f}\n"
            f"- Unit lift: {analysis['lift_percentage']:+.1f}% vs baseline\n"
            f"- Gross Profit: ${analysis['gross_profit']:,.2f} | Net Profit: ${analysis['net_profit']:,.2f}\n\n"
            f"**💸 Financials:**\n"
            f"- Cost of promotion: ${analysis['cost_of_promotion']:,.2f}\n"
            f"- Discount given: ${analysis['total_discount_given']:,.2f}\n"
            f"- Cannibalization estimate: {analysis['cannibalization_estimate_pct']:.1f}%\n\n"
            f"**Insight:** {'Promotion design is effective — consider similar mechanics for future campaigns' if analysis['roi'] >= 150 else 'Review discount depth and product selection — cannibalization or low lift detected.'}"
        )

        return {
            "answer": answer,
            "data_points": [
                {"metric": "ROI", "value": f"{analysis['roi']:.0f}%"},
                {"metric": "Revenue lift", "value": f"${analysis['incremental_revenue']:,.2f}"},
                {"metric": "Unit lift", "value": f"{analysis['lift_percentage']:+.1f}%"},
                {"metric": "Net profit", "value": f"${analysis['net_profit']:,.2f}"}
            ],
            "confidence": 0.85
        }

    def _handle_promo_rec(self, entities, query) -> Dict:
        recs = self.promotions.generate_promotion_recommendation(
            entities.get("product_id"), entities.get("category_id")
        )

        answer = (
            f"**🎁 Promotion Strategy Recommendations**\n\n"
            f"Based on retail analytics and historical promotion patterns, here are optimized promotion types:\n\n"
        )

        for rec in recs:
            answer += (
                f"**{rec['name']} [{rec['type']}]**  [Risk: {rec['risk_level'].upper()}]\n"
                f"- Suggested discount: {rec['suggested_discount_percent']}% off\n"
                f"- Duration: {rec['recommended_duration_days']} days\n"
                f"- Expected lift: ~{rec['expected_lift_pct']}% | ROI range: {rec['expected_roi_range']}%\n"
                f"- Best for: {', '.join(rec['best_for_categories'])}\n"
                f"- {rec['description']}\n\n"
            )

        answer += (
            "**💡 Planning Tip:**\n"
            "1. Run A/B tests on 2 promotion types for your target category\n"
            "2. Set minimum ROI target of 150% before launch\n"
            "3. Monitor cannibalization rate weekly during live promotions\n"
            "4. Post-promotion: Evaluate RCA-style on margin vs volume tradeoff"
        )

        return {
            "answer": answer,
            "data_points": [
                {"type": r["type"], "name": r["name"], "discount_pct": r["suggested_discount_percent"],
                 "lift_pct": r["expected_lift_pct"], "risk": r["risk_level"]}
                for r in recs
            ],
            "confidence": 0.8
        }

    def _handle_sales_perf(self, entities, query) -> Dict:
        days = 30
        region_id = entities.get("region_id")
        top = self.bi._get_top_products(region_id, days, 10, best=True)
        bottom = self.bi._get_top_products(region_id, days, 10, best=False)

        answer = "**🏆 Sales Performance Ranking**\n\n"

        if "worst" in query.lower() or "bottom" in query.lower() or "underperform" in query.lower():
            answer += "**⚠️ BOTTOM 10 Underperformers:**\n"
            for i, p in enumerate(bottom):
                answer += f"{i+1}. {p['product_name']} — Revenue: ${p['revenue']:,.2f} | Margin: {p['margin_pct']:.1f}% | Units: {p['units']:,}\n"
            data = bottom
        else:
            answer += "**⭐ TOP 10 Performers:**\n"
            for i, p in enumerate(top):
                answer += f"{i+1}. {p['product_name']} — Revenue: ${p['revenue']:,.2f} | Margin: {p['margin_pct']:.1f}% | Units: {p['units']:,}\n"
            data = top

        return {
            "answer": answer,
            "data_points": data,
            "chart_spec": {"type": "bar_chart", "data": [{"name": d["product_name"], "revenue": d["revenue"]} for d in data[:10]]},
            "confidence": 0.9
        }

    def _handle_competitor(self, entities, query) -> Dict:
        product_id = entities.get("product_id") or 1
        bench = self.pricing.get_competitor_benchmark(product_id)

        if not bench:
            return {"answer": "No competitor data available. Add competitor price tracking via the API.", "confidence": 0.5}

        position_emoji = {
            "price_leader": "🏆",
            "at_market": "✅",
            "premium_priced": "💎",
            "no_competitor_data": "❓"
        }

        answer = (
            f"**🏪 Competitive Landscape Analysis (Product #{product_id})**\n\n"
            f"Our Price: **${bench['current_price']:.2f}** {position_emoji.get(bench.get('position', ''), '')} [{bench.get('position', 'N/A').replace('_', ' ').title()}]\n"
        )

        if bench.get("competitor_avg"):
            answer += (
                f"**Competitor Benchmarks:**\n"
                f"- Competitors tracked: {bench['competitors_count']}\n"
                f"- Average price: ${bench['competitor_avg']:.2f}\n"
                f"- Lowest price: ${bench['competitor_min']:.2f}\n"
                f"- Highest price: ${bench['competitor_max']:.2f}\n"
                f"- Price Index: {bench['price_index']:.2f} (1.0 = at market)\n\n"
            )

            if bench["position"] == "premium_priced":
                answer += ("**Strategy Recommendation:** Premium positioning detected. "
                          "Ensure value prop (warranty, quality, service) justifies premium, OR match competitor pricing on traffic-driving items.\n")
            elif bench["position"] == "price_leader":
                answer += ("**Strategy Recommendation:** You are the price leader. "
                          "Consider gradual price increases on inelastic SKUs to capture margin while maintaining leadership.\n")
            else:
                answer += ("**Strategy Recommendation:** At-market position. Focus on differentiation "
                          "(promotions, bundles, loyalty) rather than pure price competition.\n")
        else:
            answer += "\n⚠️ No competitor data found. Add competitor price records via POST /api/v1/competitor-prices/\n"

        answer += "\n**Action Items:**\n1. Monitor A-class SKU competitors weekly\n2. Update competitive pricing rules monthly\n3. Run competitor-aware promotions during rivals' quiet periods"

        return {
            "answer": answer,
            "data_points": [bench],
            "confidence": 0.8 if bench.get("competitor_avg") else 0.5
        }

    def _handle_planning(self, entities, query) -> Dict:
        period = entities.get("period", "monthly")
        kpi = self.bi.get_kpi_dashboard(entities.get("region_id"))
        report = self.bi.generate_executive_report(entities.get("region_id"), period)

        answer = (
            f"**📈 AI-Assisted Business Planning — {period.title()} Strategy**\n\n"
            f"**Current Baseline:**\n"
            f"- Revenue: ${kpi.total_revenue:,.2f} ({kpi.revenue_growth:+.1f}%)\n"
            f"- Margin: {kpi.gross_margin:.1f}%\n"
            f"- Units: {kpi.total_units_sold:,}\n\n"
            f"**🎯 Priority Initiatives (Ranked by Impact):**\n\n"
        )

        initiatives = []
        if kpi.stockout_rate > 3:
            initiatives.append(("HIGH", "Reduce Stockouts",
                f"Deploy AI reorder recommendations immediately. Current stockout rate {kpi.stockout_rate:.1f}% costs ~${kpi.total_revenue * kpi.stockout_rate/100 * 0.5:,.0f}/period in revenue leakage. "
                f"Projected impact: +${kpi.total_revenue * 0.03:,.0f} revenue."))

        if kpi.inventory_turnover < 4:
            initiatives.append(("HIGH", "Optimize Working Capital",
                f"Low turnover ({kpi.inventory_turnover:.1f}x) ties up excess capital. Apply ABC analysis + EOQ to C-class items. "
                f"Projected impact: Free ${report.kpi_summary.total_revenue * 0.10:,.0f} in cash."))

        if kpi.promotion_roi < 150:
            initiatives.append(("MEDIUM", "Promotion Portfolio Optimization",
                f"Promotions below 150% ROI target. Eliminate bottom 20% performers and reallocate budget. "
                f"Projected impact: +{150 - kpi.promotion_roi:.0f}pp ROI improvement."))

        if kpi.revenue_growth < 5:
            initiatives.append(("MEDIUM", "Revenue Growth Acceleration",
                f"Sub-5% growth detected. Launch targeted pricing on elastic SKUs + top-category promotions. "
                f"Projected impact: +5-8% revenue growth in next period."))

        if kpi.gross_margin < 30:
            initiatives.append(("MEDIUM", "Margin Expansion Program",
                f"Margin below 30% threshold. Deploy pricing recommendations and reprice inelastic SKUs upward 3-5%. "
                f"Projected impact: +2-4pp margin improvement."))

        initiatives.append(("LOW", "Competitive Positioning Strengthening",
            "Weekly competitor price tracking on A-class SKUs + counter-promotion playbooks. Build sustainable moat."))

        for i, (priority, title, detail) in enumerate(initiatives):
            tag = "🔴" if priority == "HIGH" else ("🟡" if priority == "MEDIUM" else "🟢")
            answer += f"**{i+1}. [{priority}] {tag} {title}**\n{detail}\n\n"

        answer += (
            f"**📅 90-Day Execution Roadmap:**\n"
            f"- **Days 1-15:** Implement #{initiatives[0][1]} — quick win\n"
            f"- **Days 16-45:** Roll out #{initiatives[1][1]} if len(initiatives) > 1\n"
            f"- **Days 46-75:** Execute #{initiatives[2][1]} if len(initiatives) > 2 — measure A/B\n"
            f"- **Days 76-90:** Review metrics, run RCA, refine strategy for next cycle\n\n"
            f"**Key Risks to Monitor:**\n" + "\n".join([f"- {r}" for r in report.risk_alerts])
        )

        return {
            "answer": answer,
            "data_points": [
                {"initiative": title, "priority": priority, "impact": detail[:80] + "..."}
                for priority, title, detail in initiatives
            ],
            "confidence": 0.85,
            "related_insights": report.recommendations
        }

    def _handle_general(self, entities, query) -> Dict:
        answer = (
            f"**👋 Welcome to MerchIq AI Retail Copilot!**\n\n"
            f"I can help you with:\n\n"
            f"**📊 KPI & Analytics:**\n"
            f"- 'Show me the KPI dashboard' or 'How are we performing?'\n"
            f"- 'What is the sales trend?' or 'Revenue vs last month?'\n\n"
            f"**🔍 Diagnostics:**\n"
            f"- 'Why did revenue drop?' [Root Cause Analysis]\n"
            f"- 'Run a root cause analysis on margin'\n\n"
            f"**📈 Forecasting:**\n"
            f"- 'Forecast demand for product 1 next 30 days'\n"
            f"- 'Explain the forecast for product 5'\n\n"
            f"**💡 Recommendations:**\n"
            f"- 'What should we reorder?' [Inventory]\n"
            f"- 'Optimal price for product 3?' [Pricing]\n"
            f"- 'What promotion should we run?' [Promotions]\n\n"
            f"**📝 Reporting & Planning:**\n"
            f"- 'Generate monthly executive report'\n"
            f"- 'Help me plan next quarter strategy'\n\n"
            f"**🏆 Performance:**\n"
            f"- 'Top 10 selling products'\n"
            f"- 'Promotion 1 ROI evaluation'\n"
            f"- 'How do we compare to competitors?'\n\n"
            f"Try specifying product/store/region IDs for more precise answers!"
        )

        return {
            "answer": answer,
            "confidence": 0.95
        }

    def _build_sources_list(self, query_type, entities) -> List[str]:
        sources = []
        if query_type in [QueryType.KPI_ANALYSIS, QueryType.KPI_TREND, QueryType.EXECUTIVE_REPORT, QueryType.SALES_PERFORMANCE]:
            sources.extend(["SQL: sales table", "SQL: inventory table", "SQL: products table"])
        if query_type in [QueryType.FORECAST_EXPLAIN, QueryType.FORECAST_REQUEST]:
            sources.append("ML: Prophet/XGBoost forecasting model")
        if query_type == QueryType.RCA:
            sources.extend(["6-dimension correlation engine", "SQL: cross-table joins (inventory/pricing/promotions/region/weather/competitor)"])
        if query_type == QueryType.INVENTORY_RECOMMENDATION:
            sources.append("EOQ + Safety Stock optimization")
        if query_type == QueryType.PRICING_RECOMMENDATION:
            sources.extend(["Price elasticity model", "Competitor price benchmark"])
        if query_type in [QueryType.PROMOTION_EVALUATION, QueryType.PROMOTION_RECOMMENDATION]:
            sources.extend(["Promotion lift analysis", "Incremental vs baseline calc"])
        if query_type == QueryType.ASSISTED_PLANNING:
            sources.extend(["KPI baseline analysis", "Executive report insights", "RCA-derived priorities"])
        if query_type == QueryType.COMPETITOR_ANALYSIS:
            sources.append("SQL: competitor_prices table")
        return sources

    def _fallback_response(self, query, entities) -> Dict:
        return {
            "answer": f"I processed your query: '{query}'. I ran into an issue with the data backend. Please verify that sample data is loaded by running `python scripts/generate_sample_data.py`, then re-ask your question. In the meantime, I can show you the KPI dashboard, list products, or generate recommendations using default parameters.",
            "confidence": 0.5,
            "related_insights": [
                "Ensure database has sample data loaded",
                "Check backend service health at /health endpoint"
            ]
        }
