"""Flask configuration"""
import os
from datetime import timedelta


class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://joboutreach:password@localhost:5432/joboutreach'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # Celery
    CELERY_BROKER_URL = os.getenv(
        'CELERY_BROKER_URL',
        'amqp://guest:guest@localhost:5672//'
    )
    CELERY_RESULT_BACKEND = os.getenv(
        'REDIS_URL',
        'redis://localhost:6379/0'
    )
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True

    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # User info
    USER_EMAIL = os.getenv('USER_EMAIL')
    USER_NAME = os.getenv('USER_NAME')

    # Upload settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}

    # Session
    SESSION_TYPE = 'redis'
    SESSION_REDIS = None  # Set in app factory
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Company research cache TTL
    COMPANY_RESEARCH_CACHE_DAYS = 7


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}  # SQLite doesn't support pool settings


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
