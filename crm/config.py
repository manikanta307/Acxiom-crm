import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load .env from project root if present
load_dotenv(dotenv_path=BASE_DIR / '.env')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change_this_secret_for_production')
    # Debug flag (use FLASK_DEBUG=True in .env for development)
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or (
        'sqlite:///' + str(BASE_DIR / 'database' / 'crm.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Security settings
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCK_MINUTES = 15
    # Session / cookie security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    # Set SESSION_COOKIE_SECURE=True in production (requires HTTPS)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('1', 'true', 'yes')
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'http')
