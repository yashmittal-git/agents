"""Celery tasks for async job processing"""
import os
from datetime import datetime, timedelta
from celery_app import celery_app
from app.database import db
from app.models import Job, Draft, CompanyResearch

# Import agent services
from extraction_agent import ExtractionService
from research_agent import ResearchService
from content_agent import ContentService
from email_agent import EmailService


@celery_app.task(bind=True, max_retries=3)
def process_job_task(self, job_id):
    """
    Process job application asynchronously

    Workflow:
    1. Extract job information from source
    2. Research company (use cache if available)
    3. Generate personalized content
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
                "company_name": "string",
                "role": "string",
                "recruiter_name": "string or null",
                "recruiter_emails": "array of email addresses",
                "recruiter_linkedin": "string URL or null",
                "requirements": "string summary",
                "source_platform": "string (linkedin/email/whatsapp/other)"
            }

            extraction_instructions = """
            Extract job posting information:
            - Company name
            - Role/position title
            - Recruiter name (if mentioned)
            - Recruiter email addresses (extract all found)
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

            # Update job with extracted information
            job.company_name = extracted.get('company_name')
            job.role = extracted.get('role')
            job.recruiter_name = extracted.get('recruiter_name')
            job.recruiter_emails = extracted.get('recruiter_emails', [])
            job.recruiter_linkedin = extracted.get('recruiter_linkedin')
            job.requirements = extracted.get('requirements')
            job.source_platform = extracted.get('source_platform', 'unknown')
            job.status = 'extracted'
            db.session.commit()

            # Step 2: Research company
            job.status = 'researching'
            db.session.commit()

            # Check cache first
            company_research = CompanyResearch.get_cached(job.company_name)

            if not company_research:
                # Perform new research
                research_service = ResearchService(api_key=os.getenv('OPENAI_API_KEY'))
                company_research = research_service.research_company(
                    company_name=job.company_name,
                    context=f"for job application as {job.role}"
                )

                # Cache for future use
                cache_entry = CompanyResearch(
                    company_name=job.company_name,
                    data=company_research,
                    cache_days=app.config['COMPANY_RESEARCH_CACHE_DAYS']
                )
                db.session.add(cache_entry)

            job.status = 'researched'
            db.session.commit()

            # Step 3: Generate content
            job.status = 'generating'
            db.session.commit()

            content_service = ContentService(api_key=os.getenv('OPENAI_API_KEY'))

            # Load user profile (resume data)
            from app.utils import load_user_profile
            user_profile = load_user_profile()

            # Determine recommended channel
            has_email = job.recruiter_emails and len(job.recruiter_emails) > 0
            has_linkedin = job.recruiter_linkedin is not None

            if has_email:
                channel = 'email'
                confidence = 0.9
                reason = "Direct email address available"
            elif has_linkedin:
                channel = 'linkedin'
                confidence = 0.7
                reason = "LinkedIn profile available (email not found)"
            else:
                channel = 'linkedin'
                confidence = 0.5
                reason = "No direct contact info found, defaulting to LinkedIn"

            # Prepare parameters for content generation
            to_info = {
                "name": job.recruiter_name or "Hiring Team",
                "company": job.company_name,
                "role": job.role
            }

            context = {
                "purpose": "job_application",
                "job_role": job.role,
                "company": job.company_name,
                "company_research": company_research,
                "user_custom_context": job.user_context
            }

            sender_info = {
                "name": user_profile.get("name"),
                "email": user_profile.get("email"),
                "phone": user_profile.get("phone"),
                "linkedin": user_profile.get("linkedin"),
                "portfolio": user_profile.get("portfolio"),
                "highlights": user_profile.get("highlights", []),
                "skills": user_profile.get("skills", []),
                "strengths": user_profile.get("strengths")
            }

            # Generate email content
            email_content = content_service.generate_email(
                to_info=to_info,
                context=context,
                sender_info=sender_info,
                max_words=250
            )

            # Create draft
            draft = Draft(
                job_id=job.id,
                channel=channel,
                subject=email_content.get('subject', f"Application for {job.role} at {job.company_name}"),
                body_html=email_content.get('body_html', ''),
                body_text=email_content.get('body', ''),
                confidence=confidence,
                reason=reason
            )
            db.session.add(draft)

            job.status = 'drafted'
            db.session.commit()

            return {
                'status': 'success',
                'job_id': job_id,
                'draft_id': draft.id,
                'channel': channel
            }

        except Exception as e:
            job.status = 'failed'
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
