"""SQLAlchemy models for job outreach application"""
from datetime import datetime, timedelta
from app.database import db


class Job(db.Model):
    """Job application tracking"""
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Source information
    source_type = db.Column(db.String(20), nullable=False)  # 'image', 'text', 'url'
    source_file = db.Column(db.String(500))  # Path to uploaded file or URL

    # Extracted job information
    company_name = db.Column(db.String(255))
    role = db.Column(db.String(255))
    recruiter_name = db.Column(db.String(255))
    recruiter_emails = db.Column(db.JSON)  # List of email addresses
    recruiter_linkedin = db.Column(db.String(500))
    requirements = db.Column(db.Text)
    source_platform = db.Column(db.String(50))  # 'linkedin', 'email', 'whatsapp', etc.

    # User context (optional notes from user)
    user_context = db.Column(db.Text)

    # Processing status
    status = db.Column(
        db.String(20),
        nullable=False,
        default='pending',
        index=True
    )  # 'pending', 'extracting', 'extracted', 'researching', 'researched', 'generating', 'drafted', 'sent', 'failed', 'irrelevant'
    task_id = db.Column(db.String(255))  # Celery task ID for status tracking
    error_message = db.Column(db.Text)
    is_relevant = db.Column(db.Boolean, default=True)  # Whether content is job-related

    # Relationships
    drafts = db.relationship('Draft', backref='job', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Job {self.id}: {self.company_name} - {self.role}>'

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'source_type': self.source_type,
            'source_file': self.source_file,
            'company_name': self.company_name,
            'role': self.role,
            'recruiter_name': self.recruiter_name,
            'recruiter_emails': self.recruiter_emails,
            'recruiter_linkedin': self.recruiter_linkedin,
            'requirements': self.requirements,
            'source_platform': self.source_platform,
            'user_context': self.user_context,
            'status': self.status,
            'is_relevant': self.is_relevant,
            'error_message': self.error_message,
            'drafts': [draft.to_dict() for draft in self.drafts] if self.drafts else []
        }


class Draft(db.Model):
    """Email/message drafts for job applications"""
    __tablename__ = 'draft'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Content
    channel = db.Column(db.String(20), nullable=False)  # 'email', 'linkedin', 'whatsapp'
    subject = db.Column(db.Text)  # For email
    body_html = db.Column(db.Text)  # HTML version
    body_text = db.Column(db.Text)  # Plain text version

    # Metadata
    confidence = db.Column(db.Float)  # Confidence score for channel recommendation
    reason = db.Column(db.Text)  # Reason for channel selection

    # User edits
    edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime)

    # Send status
    sent = db.Column(db.Boolean, default=False, index=True)
    sent_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Draft {self.id}: {self.channel} for Job {self.job_id}>'

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'channel': self.channel,
            'subject': self.subject,
            'body_html': self.body_html,
            'body_text': self.body_text,
            'confidence': self.confidence,
            'reason': self.reason,
            'edited': self.edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'sent': self.sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }


class CompanyResearch(db.Model):
    """Cached company research data"""
    __tablename__ = 'company_research'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    researched_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    data = db.Column(db.JSON, nullable=False)  # Full research data

    def __init__(self, company_name, data, cache_days=7):
        self.company_name = company_name
        self.data = data
        self.researched_at = datetime.utcnow()
        self.expires_at = self.researched_at + timedelta(days=cache_days)

    def __repr__(self):
        return f'<CompanyResearch {self.company_name}>'

    @property
    def is_expired(self):
        """Check if cache is expired"""
        return datetime.utcnow() > self.expires_at

    @classmethod
    def get_cached(cls, company_name):
        """Get cached research if available and not expired"""
        cached = cls.query.filter_by(company_name=company_name).first()
        if cached and not cached.is_expired:
            return cached.data
        return None
