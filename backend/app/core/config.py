from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    APP_NAME: str = "MerchIq - Retail Analytics Platform"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/merchiq"
    TEST_DATABASE_URL: str = "sqlite:///./test.db"

    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_SALES_TOPIC: str = "sales-events"
    KAFKA_INVENTORY_TOPIC: str = "inventory-events"
    KAFKA_PRICING_TOPIC: str = "pricing-events"
    KAFKA_PROMOTION_TOPIC: str = "promotion-events"
    KAFKA_ENABLED: bool = False

    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    FORECAST_DEFAULT_DAYS: int = 30
    SAFETY_STOCK_Z_SCORE: float = 1.65
    PRICE_ELASTICITY_THRESHOLD: float = -0.5


settings = Settings()
