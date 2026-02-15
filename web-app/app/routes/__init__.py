"""Route blueprints"""
from app.routes.main import bp as main
from app.routes.jobs import bp as jobs
from app.routes.api import bp as api

__all__ = ['main', 'jobs', 'api']
