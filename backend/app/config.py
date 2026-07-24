from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    environment: str = "development"

    # --- PostgreSQL ---
    postgres_user: str
    postgres_password: str
    postgres_db: str
    database_url: str

    # --- Redis ---
    redis_url: str

    # --- JWT ---
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # --- Google OAuth ---
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""

    # --- GitHub OAuth ---
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = ""

    # --- Email (Gmail SMTP) ---
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # --- Currency API ---
    exchange_rate_api_key: str = ""
    exchange_rate_api_base_url: str = "https://v6.exchangerate-api.com/v6"
    currency_refresh_interval_minutes: int = 60

    # --- Frontend ---
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file="../.env",       # шлях до спільного .env в корені проєкту
        env_file_encoding="utf-8",
        case_sensitive=False,     # POSTGRES_USER в .env == postgres_user в класі
        extra="ignore",           # ігнорувати змінні з .env, яких немає в цьому класі (напр. VITE_API_URL)
    )


# Єдиний екземпляр налаштувань — імпортуємо його скрізь, де потрібен доступ до конфігу
settings = Settings()