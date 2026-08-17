from app.events.event_bus import RetailEventBus, EventConsumer, producer
from app.core.utils import get_logger

logger = get_logger(__name__)


class InventoryEventHandler:
    @staticmethod
    def handle_sale_created(event):
        try:
            payload = event["payload"]
            product_id = payload.get("product_id")
            store_id = payload.get("store_id")
            qty_sold = payload.get("quantity_sold", 0)
            logger.info(f"InventoryEventHandler: Decrementing stock for product={product_id} store={store_id} qty={qty_sold}")
        except Exception as e:
            logger.error(f"InventoryEventHandler error: {e}")

    @staticmethod
    def handle_price_changed(event):
        try:
            payload = event["payload"]
            logger.info(f"Re-evaluating demand forecast due to price change: product={payload.get('product_id')}")
        except Exception as e:
            logger.error(f"InventoryEventHandler price error: {e}")


class AnalyticsEventHandler:
    @staticmethod
    def handle_sale_created(event):
        try:
            payload = event["payload"]
            logger.info(f"AnalyticsEventHandler: Recording sale for revenue pipeline: ${payload.get('total_amount', 0)}")
        except Exception as e:
            logger.error(f"AnalyticsEventHandler error: {e}")

    @staticmethod
    def handle_promotion_started(event):
        try:
            payload = event["payload"]
            logger.info(f"AnalyticsEventHandler: Baseline recording started for promo={payload.get('promotion_id')}")
        except Exception as e:
            logger.error(f"AnalyticsEventHandler promo error: {e}")


class NotificationEventHandler:
    @staticmethod
    def handle_low_stock(event):
        try:
            payload = event["payload"]
            logger.info(f"NOTIFICATION: Low stock alert for product={payload.get('product_id')} "
                       f"store={payload.get('store_id')} remaining={payload.get('remaining_qty')}")
        except Exception as e:
            logger.error(f"NotificationEventHandler error: {e}")

    @staticmethod
    def handle_forecast_completed(event):
        try:
            payload = event["payload"]
            logger.info(f"NOTIFICATION: Forecast ready for product={payload.get('product_id')} "
                       f"MAPE={payload.get('mape')}%")
        except Exception as e:
            logger.error(f"NotificationEventHandler forecast error: {e}")


def register_event_handlers():
    logger.info("Registering MerchIq event handlers (5 microservice architecture)...")
    logger.info("Microservice 1: Sales Service (owns sales transactions)")
    logger.info("Microservice 2: Inventory Service (owns stock + PO suggestions)")
    logger.info("Microservice 3: Pricing Service (owns pricing recommendations + elasticity)")
    logger.info("Microservice 4: Analytics/BI Service (owns KPIs + RCA + reports)")
    logger.info("Microservice 5: AI/Copilot Service (owns forecasting + LLM copilot + RAG)")
    logger.info("Event choreography pattern: Kafka events sync all 5 services")
