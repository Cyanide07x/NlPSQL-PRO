# config.py
class Config:
    APP_DB_HOST = "localhost"
    APP_DB_PORT = 3306
    APP_DB_USER = "root"
    APP_DB_PASSWORD = "DEATH0724"
    APP_DB_NAME = "audex_app"

    SECRET_KEY = "some_random_secret"
    DEBUG = True

    GROQ_API_KEY = "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"  # or your key
    GROQ_MODEL = "llama-3.1-8b-instant"