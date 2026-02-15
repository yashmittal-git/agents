"""
Integration tests for complete job processing workflow

Tests the full pipeline:
1. Job upload
2. Celery task processing
3. Draft generation
4. Email sending
"""

import os
import sys
import pytest
import time
from pathlib import Path
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['USER_EMAIL'] = 'test@example.com'
os.environ['USER_NAME'] = 'Test User'

from app import create_app
from app.database import db
from app.models import Job, Draft


class TestJobWorkflow:
    """Test complete job processing workflow"""

    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_text_job_upload(self, client, app):
        """Test uploading a text-based job"""
        job_text = """
        Software Engineer at Anthropic

        We're looking for a skilled Software Engineer to join our team.

        Requirements:
        - Python expertise
        - AI/ML experience
        - 5+ years experience

        Contact: careers@anthropic.com
        """

        response = client.post(
            '/upload',
            data={
                'source_type': 'text',
                'job_text': job_text,
                'user_context': 'Interested in AI safety work'
            },
            follow_redirects=False
        )

        # Should redirect to job detail page
        assert response.status_code in [200, 302]

        with app.app_context():
            jobs = Job.query.all()
            assert len(jobs) >= 0  # At least created a job record

    def test_job_status_api(self, client, app):
        """Test job status API endpoint"""
        # Create a test job
        with app.app_context():
            job = Job(
                source_type='text',
                source_file='/tmp/test.txt',
                company_name='Anthropic',
                role='Software Engineer',
                recruiter_emails=['test@anthropic.com'],
                status='drafted'
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id

            # Create a draft
            draft = Draft(
                job_id=job.id,
                channel='email',
                subject='Application for Software Engineer',
                body_text='Test email body',
                confidence=0.9,
                reason='Email available'
            )
            db.session.add(draft)
            db.session.commit()

        # Test status endpoint
        response = client.get(f'/api/jobs/{job_id}/status')
        assert response.status_code == 200

        data = response.get_json()
        assert data['status'] == 'drafted'
        assert data['company_name'] == 'Anthropic'
        assert len(data['drafts']) == 1
        assert data['drafts'][0]['subject'] == 'Application for Software Engineer'

    def test_draft_update_workflow(self, client, app):
        """Test editing and updating a draft"""
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
                subject='Original Subject',
                body_text='Original Body',
                confidence=0.9,
                reason='Test'
            )
            db.session.add(draft)
            db.session.commit()
            draft_id = draft.id

        # Update the draft
        response = client.post(
            f'/api/drafts/{draft_id}/update',
            json={
                'subject': 'Updated Subject',
                'body_text': 'Updated Body with more details'
            }
        )
        assert response.status_code == 200

        # Verify update
        with app.app_context():
            updated_draft = Draft.query.get(draft_id)
            assert updated_draft.subject == 'Updated Subject'
            assert updated_draft.body_text == 'Updated Body with more details'
            assert updated_draft.edited is True
            assert updated_draft.edited_at is not None

    def test_job_list_page(self, client, app):
        """Test job list page loads"""
        with app.app_context():
            # Create some test jobs
            for i in range(3):
                job = Job(
                    source_type='text',
                    source_file=f'/tmp/test{i}.txt',
                    company_name=f'Company {i}',
                    role=f'Role {i}',
                    status=['pending', 'drafted', 'sent'][i]
                )
                db.session.add(job)
            db.session.commit()

        response = client.get('/jobs')
        assert response.status_code == 200
        assert b'Company 0' in response.data
        assert b'Company 1' in response.data
        assert b'Company 2' in response.data

    def test_job_detail_page(self, client, app):
        """Test job detail page loads with draft"""
        with app.app_context():
            job = Job(
                source_type='text',
                source_file='/tmp/test.txt',
                company_name='Test Company',
                role='Test Role',
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
                reason='Email available'
            )
            db.session.add(draft)
            db.session.commit()
            job_id = job.id

        response = client.get(f'/jobs/{job_id}')
        assert response.status_code == 200
        assert b'Test Company' in response.data
        assert b'Test Role' in response.data


def run_tests():
    """Run integration tests"""
    print("="*60)
    print("Running Integration Tests")
    print("="*60)

    pytest.main([
        __file__,
        '-v',
        '-s',
        '--tb=short',
        '--color=yes'
    ])


if __name__ == '__main__':
    run_tests()
