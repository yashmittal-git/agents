#!/usr/bin/env python
"""
Initialize database and create initial migration

Run this script to set up Flask-Migrate (Alembic) for the first time.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.database import db
from flask_migrate import init, migrate, upgrade

if __name__ == '__main__':
    app = create_app('development')

    with app.app_context():
        # Check if migrations directory exists
        if not os.path.exists('migrations'):
            print("Initializing migrations directory...")
            init()

        # Create initial migration
        print("Creating initial migration...")
        migrate(message='Initial schema')

        # Apply migrations
        print("Applying migrations...")
        upgrade()

        print("\nDatabase initialized successfully!")
        print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
