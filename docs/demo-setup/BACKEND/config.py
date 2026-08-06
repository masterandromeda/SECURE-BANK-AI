import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production-abc123xyz")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'bank.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

DEBUG = True

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
