from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=[".env", ".env.local"],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # App Settings
    PROJECT_NAME: str = "Synthesize.io API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://synthesize:synthesize@postgres:5432/synthesizedb"
    
    # MongoDB (for utility data: logs, analytics, usage tracking)
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DATABASE: str = "synthesize_utility"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Security
    JWT_SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_SECRET: str = ""
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # OAuth
    GOOGLE_OAUTH_CLIENT_ID: str = ""
    GOOGLE_OAUTH_CLIENT_SECRET: str = ""
    GOOGLE_OAUTH_REDIRECT_URI: str = "http://localhost:3000/api/auth/google/callback"
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    
    # Anthropic (Claude) - Optional
    ANTHROPIC_API_KEY: str = ""
    
    # Groq API (Free Alternative)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Dodo Payments (Primary Payment Provider)
    DODO_PAYMENTS_API_KEY: str = ""
    DODO_WEBHOOK_SECRET: str = ""
    DODO_ENVIRONMENT: str = "test_mode"  # "test_mode" or "live_mode"
    
    # Stripe (Legacy/Alternative Payment Provider)
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # Dodo Product IDs (configured in Dodo Dashboard)
    DODO_PRODUCT_BEGINNER: str = "pdt_0NWWpOaPzyUbJ0qQ0aN7q"
    DODO_PRODUCT_PRO: str = "pdt_0NWT8Nb1Zzv6dOJHrhzps"
    DODO_PRODUCT_BUSINESS: str = "pdt_0NWT9B7XQo63GB3dbjPME"
    
    # Email (Nodemailer)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_SECURE: bool = False
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@synthesize.io"
    SMTP_FROM_NAME: str = "Synthesize.io"
    EMAIL_FROM: str = ""
    
    # Storage
    STORAGE_PATH: str = "./data/generated"  # Relative path for local development
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB
    
    # Data Factory Directories
    DATA_DIR: str = "./data"
    DATA_UPLOAD_DIR: str = "./data/uploads"
    DATA_OUTPUT_DIR: str = "./data/generated"
    DATA_MODELS_DIR: str = "./data/models"
    
    # Data Factory Limits
    FAKER_MAX_ROWS: int = 100000
    FAKER_MAX_COLUMNS: int = 100
    SYNTHCITY_MAX_TRAINING_ROWS: int = 100000
    SYNTHCITY_MAX_EPOCHS: int = 1000
    LLM_MAX_ROWS: int = 1000
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Application URLs
    API_URL: str = "http://localhost:8000"
    WEB_URL: str = "http://localhost:3000"
    ADMIN_URL: str = "http://localhost:3001"
    FRONTEND_URL: str = "http://localhost:3000"  # Main frontend URL for OAuth redirects
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://web:3000",
        "http://admin:3000"
    ]
    
    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # Google Analytics
    GA_MEASUREMENT_ID: str = ""


settings = Settings()
