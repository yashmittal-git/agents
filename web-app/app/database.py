"""Database configuration and utilities"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import models so they're registered with SQLAlchemy
        from app import models

        # Create tables (for development)
        # In production, use migrations: flask db upgrade
        if app.config.get('TESTING'):
            db.create_all()
