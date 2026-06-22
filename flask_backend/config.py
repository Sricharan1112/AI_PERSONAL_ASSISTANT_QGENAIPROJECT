"""
Centralized configuration for the Flask app.
Reads from environment variables (loaded from .env via python-dotenv).
"""

import os
from dotenv import load_dotenv

load_dotenv()  # reads .env file in this directory, if present


class Config:
    # OpenAI
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    # Where the Django REST API lives
    DJANGO_API_BASE_URL = os.environ.get(
        "DJANGO_API_BASE_URL", "http://127.0.0.1:8000/api"
    )

    # Flask
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"
    FLASK_PORT = int(os.environ.get("FLASK_PORT", "5000"))

    # CORS - allow the frontend (served separately or via Flask static)
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS", "http://127.0.0.1:5000,http://localhost:5000"
    ).split(",")
