from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import schemas
from app.services.copilot.service import RetailCopilotService, QueryType

router = APIRouter()


@router.post("/copilot/query", response_model=schemas.CopilotQueryResponse)
def copilot_query(
    request: schemas.CopilotQueryRequest,
    db: Session = Depends(get_db)
):
    service = RetailCopilotService(db)
    result = service.process_query(request.query, request.context_filters)
    return schemas.CopilotQueryResponse(**result)


@router.get("/copilot/query-types")
def get_available_query_types():
    return {
        "query_types": [
            {"id": qt.value, "description": qt.value.replace("_", " ").title(),
             "examples": _get_examples(qt)}
            for qt in QueryType
        ]
    }


def _get_examples(qtype: QueryType) -> list:
    examples = {
        QueryType.FORECAST_EXPLAIN: ["Explain the forecast drivers for product 1", "Why is the forecast trending up?"],
        QueryType.FORECAST_REQUEST: ["Forecast demand for product 1 next 30 days", "Predict sales for next month"],
        QueryType.KPI_ANALYSIS: ["Show me the KPI dashboard", "What is our total revenue?", "Current gross margin"],
        QueryType.KPI_TREND: ["Revenue trend vs last month", "Are sales growing or declining?"],
        QueryType.RCA: ["Why did revenue drop?", "Root cause analysis for margin decline"],
        QueryType.EXECUTIVE_REPORT: ["Generate executive report", "Monthly business summary"],
        QueryType.INVENTORY_RECOMMENDATION: ["What should we reorder?", "PO suggestions for store 1", "Low stock items"],
        QueryType.PRICING_RECOMMENDATION: ["Recommend price for product 1", "Should we raise prices?", "Pricing strategy"],
        QueryType.PROMOTION_EVALUATION: ["Evaluate promotion 1 ROI", "Did the last promotion work?"],
        QueryType.PROMOTION_RECOMMENDATION: ["What promotion should we run?", "Promotion ideas for summer"],
        QueryType.SALES_PERFORMANCE: ["Top 10 products", "Worst performing SKUs", "Sales by category"],
        QueryType.COMPETITOR_ANALYSIS: ["Competitor pricing for product 1", "Market position analysis"],
        QueryType.ASSISTED_PLANNING: ["Plan next quarter strategy", "What should we do to grow?"],
        QueryType.GENERAL_INFO: ["What can you do?", "Help"]
    }
    return examples.get(qtype, [])


@router.get("/copilot/knowledge-base")
def get_knowledge_base():
    from app.services.copilot.service import RAG_KNOWLEDGE_BASE
    return {
        "count": len(RAG_KNOWLEDGE_BASE),
        "documents": [
            {"id": d["id"], "topic": d["topic"], "keywords": d["keywords"], "content_preview": d["content"][:100] + "..."}
            for d in RAG_KNOWLEDGE_BASE
        ]
    }
