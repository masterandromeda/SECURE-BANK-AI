import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'securebankai-secret-key-2024-dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///securebank_ai.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    DEBUG = True
