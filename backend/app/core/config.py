from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Postgres
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "jobai"
    postgres_user: str = "jobai"
    postgres_password: str = "secret"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 дней

    # Telegram
    telegram_bot_token: str = ""
    telegram_bot_username: str = ""

    # AI
    gigachat_api_key: str = ""
    yandex_gpt_api_key: str = ""
    yandex_folder_id: str = ""

    # Billing
    yukassa_shop_id: str = ""
    yukassa_secret_key: str = ""

    # App
    debug: bool = False
    sentry_dsn: str = ""

    # Rate limits
    free_requests_per_day: int = 5


settings = Settings()