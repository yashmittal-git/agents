"""Celery application initialization"""
from celery import Celery


def make_celery(app=None):
    """Create Celery app with Flask config"""
    celery = Celery(
        'job_outreach',
        broker=None if app is None else app.config['CELERY_BROKER_URL'],
        backend=None if app is None else app.config['CELERY_RESULT_BACKEND']
    )

    if app:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context"""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery


# Create celery instance for worker
celery_app = make_celery()
