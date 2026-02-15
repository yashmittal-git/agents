"""Celery tasks for async job processing"""
import os
import json
from datetime import datetime, timedelta
from celery_app import celery_app
from app.database import db
from app.models import Job, Draft, CompanyResearch

# Import agent services
from extraction_agent import ExtractionService
from job_outreach_agent import JobOrchestrator
from email_agent import EmailService


@celery_app.task(bind=True, max_retries=3)
def process_job_task(self, job_id):
    """
    Process job application asynchronously using JobOrchestrator

    Workflow:
    1. Extract job information from source
    2. Check relevancy
    3. Use orchestrator to process job (research, match, generate, recommend channel)
    4. Create draft for user review
    """
    from app import create_app
    app = create_app()

    with app.app_context():
        job = Job.query.get(job_id)
        if not job:
            return {'error': f'Job {job_id} not found'}

        try:
            # Step 1: Extract job information
            job.status = 'extracting'
            db.session.commit()

            extractor = ExtractionService(api_key=os.getenv('OPENAI_API_KEY'))

            # Determine content type and read file
            if job.source_type == 'image':
                content = job.source_file
                content_type = 'image'
            elif job.source_type == 'text':
                with open(job.source_file, 'r') as f:
                    content = f.read()
                content_type = 'text'
            elif job.source_type == 'url':
                content = job.source_file
                content_type = 'url'
            else:
                raise ValueError(f"Unknown source type: {job.source_type}")

            # Extract structured job information
            extraction_schema = {
                "is_job_related": "boolean - true if this is a job posting/opportunity, false otherwise",
                "company_name": "string or null",
                "role": "string or null",
                "recruiter_name": "string or null",
                "recruiter_emails": "array of email addresses or empty array",
                "recruiter_linkedin": "string URL or null",
                "requirements": "string summary or null",
                "source_platform": "string (linkedin/email/whatsapp/other) or null"
            }

            extraction_instructions = """
            First, determine if this content is job-related (a job posting, opportunity, or career-related content).
            If NOT job-related, set is_job_related to false and leave other fields null/empty.

            If it IS job-related, extract:
            - Company name
            - Role/position title
            - Recruiter name (if mentioned)
            - Recruiter email addresses (extract ALL found)
            - Recruiter LinkedIn profile URL (if mentioned)
            - Key requirements summary
            - Source platform (LinkedIn, email, WhatsApp, etc.)
            """

            extracted = extractor.extract(
                content=content,
                content_type=content_type,
                schema=extraction_schema,
                instructions=extraction_instructions
            )

            # Check if content is job-related
            is_relevant = extracted.get('is_job_related', True)

            if not is_relevant or not extracted.get('company_name') or not extracted.get('role'):
                job.status = 'irrelevant'
                job.is_relevant = False
                job.error_message = "Content does not appear to be a job posting or opportunity"
                db.session.commit()

                return {
                    'status': 'irrelevant',
                    'job_id': job_id,
                    'message': 'This content does not appear to be job-related'
                }

            # Update job with extracted information
            job.company_name = extracted.get('company_name')
            job.role = extracted.get('role')
            job.recruiter_name = extracted.get('recruiter_name')
            job.recruiter_emails = extracted.get('recruiter_emails', [])
            job.recruiter_linkedin = extracted.get('recruiter_linkedin')
            job.requirements = extracted.get('requirements')
            job.source_platform = extracted.get('source_platform', 'unknown')
            job.is_relevant = True
            job.status = 'extracted'
            db.session.commit()

            # Step 2-4: Use orchestrator to process job (research, match, generate, recommend)
            job.status = 'processing'
            db.session.commit()

            # Load user profile
            from app.utils import load_user_profile
            user_profile = load_user_profile()

            # Initialize orchestrator
            orchestrator = JobOrchestrator(
                openai_api_key=os.getenv('OPENAI_API_KEY'),
                gmail_credentials_path='credentials.json',
                user_profile=user_profile
            )

            # Prepare job info for orchestrator (match CLI format)
            job_info = {
                'company_name': job.company_name,
                'role': job.role,
                'recruiter_name': job.recruiter_name,
                'recruiter_email': job.recruiter_emails[0] if job.recruiter_emails else None,
                'all_emails': job.recruiter_emails,
                'recruiter_linkedin': job.recruiter_linkedin,
                'requirements': job.requirements,
                'user_context': job.user_context
            }

            # Process job (returns strategy with channel recommendation)
            result = orchestrator.process_job(
                job_info=job_info,
                auto_send=False  # Never auto-send from web app
            )

            # Load draft file to get all information
            draft_file = result.get('draft_file')
            with open(draft_file, 'r') as f:
                draft_data = json.load(f)

            # Extract strategy information from draft file
            strategy_data = draft_data.get('strategy', {})
            channel_rec = draft_data.get('channel_recommendation', {})

            channel = channel_rec.get('primary_channel', 'email').lower()
            confidence = channel_rec.get('confidence', 0.5)
            reasoning = channel_rec.get('reason', 'Channel recommendation based on available contact information')

            # Extract content from strategy section
            content_data = strategy_data.get('content', {})

            # Create draft in database
            draft = Draft(
                job_id=job.id,
                channel=channel,
                subject=content_data.get('subject', f"Application for {job.role} at {job.company_name}"),
                body_html=content_data.get('body_html', content_data.get('body', '')),
                body_text=content_data.get('body', ''),
                confidence=confidence,
                reason=reasoning
            )
            db.session.add(draft)

            job.status = 'drafted'
            db.session.commit()

            return {
                'status': 'success',
                'job_id': job_id,
                'draft_id': draft.id,
                'channel': channel,
                'confidence': confidence
            }

        except Exception as e:
            job.status = 'failed'
            job.is_relevant = True  # Assume relevant unless proven otherwise
            job.error_message = str(e)
            db.session.commit()

            # Retry with exponential backoff
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=2)
def send_email_task(self, draft_id):
    """Send email via email-agent"""
    from app import create_app
    app = create_app()

    with app.app_context():
        draft = Draft.query.get(draft_id)
        if not draft:
            return {'error': f'Draft {draft_id} not found'}

        job = draft.job

        try:
            # Initialize email service
            email_service = EmailService(
                credentials_path='credentials.json',
                sender_email=os.getenv('USER_EMAIL'),
                sender_name=os.getenv('USER_NAME')
            )

            # Send email with BCC to user
            success = email_service.send(
                to=job.recruiter_emails,
                subject=draft.subject,
                body=draft.body_html,
                bcc=[os.getenv('USER_EMAIL')],
                is_html=True
            )

            if success:
                draft.sent = True
                draft.sent_at = datetime.utcnow()
                job.status = 'sent'
                db.session.commit()

                return {
                    'status': 'success',
                    'draft_id': draft_id,
                    'job_id': job.id
                }
            else:
                raise Exception("Email sending failed")

        except Exception as e:
            # Retry with exponential backoff
            raise self.retry(exc=e, countdown=30 * (2 ** self.request.retries))
