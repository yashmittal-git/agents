"""Flask application factory"""
import os
from flask import Flask
from redis import Redis
from config import config
from app.database import init_db


def create_app(config_name=None):
    """Create and configure Flask application"""

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    init_db(app)

    # Setup Redis for sessions
    app.config['SESSION_REDIS'] = Redis.from_url(app.config['REDIS_URL'])

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.routes import main, jobs, api
    app.register_blueprint(main)
    app.register_blueprint(jobs)
    app.register_blueprint(api)

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500

    # Template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        """Format datetime for templates"""
        if value is None:
            return ''
        return value.strftime(format)

    return app
