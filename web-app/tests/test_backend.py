"""
Comprehensive backend tests for web app

Tests cover:
1. Models - Job, Draft, CompanyResearch
2. Database operations - CRUD, relationships
3. Celery tasks - process_job_task, send_email_task
4. API endpoints - status, update, send
5. User profile loading
6. Integration with agents
"""

import os
import sys
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['CELERY_BROKER_URL'] = 'memory://'
os.environ['REDIS_URL'] = 'redis://localhost:6379/1'
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['USER_EMAIL'] = 'test@example.com'
os.environ['USER_NAME'] = 'Test User'

from app import create_app
from app.database import db
from app.models import Job, Draft, CompanyResearch


class TestModels:
    """Test SQLAlchemy models"""

    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_job_creation(self, app):
        """Test creating a Job"""
        with app.app_context():
            job = Job(
                source_type='image',
                source_file='/tmp/test.png',
                company_name='Test Corp',
                role='Software Engineer',
                status='pending'
            )
            db.session.add(job)
            db.session.commit()

            assert job.id is not None
            assert job.company_name == 'Test Corp'
            assert job.status == 'pending'
            assert job.created_at is not None

    def test_draft_relationship(self, app):
        """Test Job-Draft relationship"""
        with app.app_context():
            job = Job(
                source_type='text',
                source_file='/tmp/job.txt',
                company_name='Anthropic',
                role='Engineer',
                status='drafted'
            )
            db.session.add(job)
            db.session.commit()

            draft = Draft(
                job_id=job.id,
                channel='email',
                subject='Test Subject',
                body_text='Test Body',
                confidence=0.9,
                reason='Test'
            )
            db.session.add(draft)
            db.session.commit()

            # Test relationship
            assert len(job.drafts) == 1
            assert job.drafts[0].subject == 'Test Subject'
            assert draft.job.company_name == 'Anthropic'

    def test_company_research_cache(self, app):
        """Test CompanyResearch caching"""
        with app.app_context():
            research = CompanyResearch(
                company_name='TestCo',
                data={'info': 'test data'},
                cache_days=7
            )
            db.session.add(research)
            db.session.commit()

            # Test cache retrieval
            cached = CompanyResearch.get_cached('TestCo')
            assert cached is not None
            assert cached['info'] == 'test data'

    def test_company_research_expiry(self, app):
        """Test CompanyResearch expiration"""
        with app.app_context():
            # Create expired research
            research = CompanyResearch(
                company_name='ExpiredCo',
                data={'info': 'old data'},
                cache_days=7
            )
            # Manually set to expired
            research.expires_at = datetime.utcnow() - timedelta(days=1)
            db.session.add(research)
            db.session.commit()

            # Should return None for expired
            cached = CompanyResearch.get_cached('ExpiredCo')
            assert cached is None


class TestUserProfile:
    """Test user profile loading"""

    def test_user_profile_structure(self):
        """Test that user profile has required fields"""
        # This is what we need to implement
        from app.utils import load_user_profile

        profile = load_user_profile()

        assert 'name' in profile
        assert 'email' in profile
        assert 'highlights' in profile
        assert isinstance(profile['highlights'], list)
        assert 'skills' in profile
        assert isinstance(profile['skills'], list)


class TestTasks:
    """Test Celery tasks (mock external services)"""

    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    def test_process_job_task_structure(self, app):
        """Test process_job_task can be imported"""
        from app.tasks import process_job_task

        assert process_job_task is not None
        assert callable(process_job_task)

    def test_send_email_task_structure(self, app):
        """Test send_email_task can be imported"""
        from app.tasks import send_email_task

        assert send_email_task is not None
        assert callable(send_email_task)

    def test_job_status_progression(self, app):
        """Test job status updates correctly"""
        with app.app_context():
            job = Job(
                source_type='text',
                source_file='/tmp/test.txt',
                status='pending'
            )
            db.session.add(job)
            db.session.commit()

            # Simulate status progression
            statuses = ['extracting', 'extracted', 'researching',
                       'researched', 'generating', 'drafted']

            for status in statuses:
                job.status = status
                db.session.commit()

                fetched_job = Job.query.get(job.id)
                assert fetched_job.status == status


class TestAPIEndpoints:
    """Test Flask API endpoints"""

    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_job_status_endpoint(self, client, app):
        """Test /api/jobs/<id>/status endpoint"""
        with app.app_context():
            job = Job(
                source_type='text',
                source_file='/tmp/test.txt',
                company_name='Test',
                role='Engineer',
                status='drafted'
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id

        response = client.get(f'/api/jobs/{job_id}/status')
        assert response.status_code == 200

        data = response.get_json()
        assert data['status'] == 'drafted'
        assert data['company_name'] == 'Test'

    def test_draft_update_endpoint(self, client, app):
        """Test /api/drafts/<id>/update endpoint"""
        with app.app_context():
            job = Job(
                source_type='text',
                source_file='/tmp/test.txt',
                status='drafted'
            )
            db.session.add(job)
            db.session.commit()

            draft = Draft(
                job_id=job.id,
                channel='email',
                subject='Old Subject',
                body_text='Old Body',
                confidence=0.9,
                reason='Test'
            )
            db.session.add(draft)
            db.session.commit()
            draft_id = draft.id

        response = client.post(
            f'/api/drafts/{draft_id}/update',
            json={
                'subject': 'New Subject',
                'body_text': 'New Body'
            }
        )
        assert response.status_code == 200

        with app.app_context():
            updated_draft = Draft.query.get(draft_id)
            assert updated_draft.subject == 'New Subject'
            assert updated_draft.body_text == 'New Body'
            assert updated_draft.edited is True


class TestFileUpload:
    """Test file upload handling"""

    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_upload_endpoint_exists(self, client):
        """Test upload endpoint exists"""
        response = client.get('/upload')
        # Should redirect or show form
        assert response.status_code in [200, 302, 405]


def run_tests():
    """Run all tests"""
    print("="*60)
    print("Running Backend Tests")
    print("="*60)

    # Run pytest
    pytest.main([
        __file__,
        '-v',  # Verbose
        '-s',  # Show print statements
        '--tb=short',  # Short traceback
        '--color=yes'  # Colored output
    ])


if __name__ == '__main__':
    run_tests()
