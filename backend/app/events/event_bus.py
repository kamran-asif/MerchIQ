import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from app.core.config import settings
from app.core.utils import get_logger

logger = get_logger(__name__)

KAFKA_ENABLED = False

try:
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.errors import KafkaError
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logger.warning("kafka-python not installed, using in-memory event bus fallback")

_in_memory_bus: Dict[str, list] = {}


class EventProducer:
    def __init__(self):
        self.producer = None
        self.enabled = settings.KAFKA_ENABLED and KAFKA_AVAILABLE
        self._init_producer()

    def _init_producer(self):
        if self.enabled:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                    acks="all",
                    retries=3
                )
                logger.info("Kafka producer initialized")
            except Exception as e:
                logger.warning(f"Kafka producer init failed: {e}, using in-memory bus")
                self.enabled = False

    def publish(self, topic: str, event_type: str, payload: Dict[str, Any], key: Optional[str] = None):
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload,
            "key": key
        }
        if self.enabled and self.producer:
            try:
                key_bytes = key.encode("utf-8") if key else None
                self.producer.send(topic, value=event, key=key_bytes)
                self.producer.flush(timeout=5)
                logger.info(f"Kafka event sent: {topic}/{event_type} key={key}")
            except KafkaError as e:
                logger.error(f"Kafka send error: {e}")
                self._fallback_publish(topic, event)
        else:
            self._fallback_publish(topic, event)

    def _fallback_publish(self, topic: str, event: Dict):
        if topic not in _in_memory_bus:
            _in_memory_bus[topic] = []
        _in_memory_bus[topic].append(event)
        logger.info(f"In-memory event: {topic}/{event['event_type']} (queue size: {len(_in_memory_bus[topic])})")


class EventConsumer:
    def __init__(self):
        self.enabled = settings.KAFKA_ENABLED and KAFKA_AVAILABLE
        self.consumer = None

    def consume(self, topic: str, handler: Callable[[Dict], None], group_id: str = "merchiq-group"):
        if self.enabled:
            try:
                self.consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id=group_id,
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                    auto_offset_reset="earliest",
                    enable_auto_commit=True
                )
                logger.info(f"Kafka consumer started on topic: {topic}")
                for message in self.consumer:
                    try:
                        handler(message.value)
                    except Exception as e:
                        logger.error(f"Consumer handler error: {e}")
            except Exception as e:
                logger.error(f"Kafka consumer error: {e}")
        else:
            logger.info(f"In-memory consumer registered for topic: {topic}")
            events = _in_memory_bus.get(topic, [])
            for event in events:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"In-memory handler error: {e}")
            _in_memory_bus[topic] = []


producer = EventProducer()


class RetailEventBus:
    SALES_TOPIC = settings.KAFKA_SALES_TOPIC
    INVENTORY_TOPIC = settings.KAFKA_INVENTORY_TOPIC
    PRICING_TOPIC = settings.KAFKA_PRICING_TOPIC
    PROMOTION_TOPIC = settings.KAFKA_PROMOTION_TOPIC

    @staticmethod
    def publish_sale_created(sale_data: Dict):
        producer.publish(
            RetailEventBus.SALES_TOPIC,
            "sale.created",
            sale_data,
            key=str(sale_data.get("product_id"))
        )

    @staticmethod
    def publish_inventory_updated(inventory_data: Dict):
        producer.publish(
            RetailEventBus.INVENTORY_TOPIC,
            "inventory.updated",
            inventory_data,
            key=f"{inventory_data.get('product_id')}_{inventory_data.get('store_id')}"
        )

    @staticmethod
    def publish_price_changed(price_data: Dict):
        producer.publish(
            RetailEventBus.PRICING_TOPIC,
            "price.changed",
            price_data,
            key=str(price_data.get("product_id"))
        )

    @staticmethod
    def publish_promotion_started(promotion_data: Dict):
        producer.publish(
            RetailEventBus.PROMOTION_TOPIC,
            "promotion.started",
            promotion_data,
            key=str(promotion_data.get("promotion_id"))
        )

    @staticmethod
    def publish_promotion_ended(promotion_data: Dict):
        producer.publish(
            RetailEventBus.PROMOTION_TOPIC,
            "promotion.ended",
            promotion_data,
            key=str(promotion_data.get("promotion_id"))
        )

    @staticmethod
    def publish_forecast_completed(forecast_data: Dict):
        producer.publish(
            "forecast-events",
            "forecast.completed",
            forecast_data,
            key=str(forecast_data.get("product_id"))
        )

    @staticmethod
    def publish_low_stock_alert(alert_data: Dict):
        producer.publish(
            "alert-events",
            "inventory.low_stock",
            alert_data,
            key=str(alert_data.get("product_id"))
        )

    @staticmethod
    def publish_rca_completed(rca_data: Dict):
        producer.publish(
            "analytics-events",
            "rca.completed",
            rca_data
        )

    @staticmethod
    def publish_copilot_query(query_data: Dict):
        producer.publish(
            "copilot-events",
            "copilot.query",
            query_data
        )
