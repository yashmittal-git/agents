"""Celery worker entry point - imports tasks to register them"""
import os
from celery_app import celery_app

# Import tasks to register them with Celery
# This must happen AFTER celery_app is created but BEFORE worker starts
from app import tasks  # noqa: F401

# Set default config if not provided
if not celery_app.conf.broker_url:
    celery_app.conf.broker_url = os.getenv(
        'CELERY_BROKER_URL',
        'amqp://guest:guest@rabbitmq:5672//'
    )

if not celery_app.conf.result_backend:
    celery_app.conf.result_backend = os.getenv(
        'REDIS_URL',
        'redis://redis:6379/0'
    )

# Ensure serializers are set
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.timezone = 'UTC'
celery_app.conf.enable_utc = True

if __name__ == '__main__':
    celery_app.start()
