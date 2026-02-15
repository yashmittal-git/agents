"""API routes for AJAX requests

Note: These routes return JSON and are consumed by JavaScript in templates.
For HTML views, see jobs.py and main.py.

Route organization:
- /api/jobs/<id>/status → JSON for polling (used by job_detail.html)
- /api/drafts/<id>/update → JSON for saving edits
- /api/drafts/<id>/send → JSON for sending emails
- /jobs/<id> (in jobs.py) → HTML page for viewing job details
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from app.database import db
from app.models import Job, Draft
from app.tasks import send_email_task

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/jobs/<int:job_id>/status')
def job_status(job_id):
    """Get job processing status (for polling)"""
    job = Job.query.get_or_404(job_id)
    return jsonify(job.to_dict())


@bp.route('/drafts/<int:draft_id>', methods=['GET'])
def get_draft(draft_id):
    """Get draft details"""
    draft = Draft.query.get_or_404(draft_id)
    return jsonify(draft.to_dict())


@bp.route('/drafts/<int:draft_id>/update', methods=['POST'])
def update_draft(draft_id):
    """Update draft content (user edits)"""
    draft = Draft.query.get_or_404(draft_id)

    data = request.get_json()

    if 'subject' in data:
        draft.subject = data['subject']

    if 'body_text' in data:
        draft.body_text = data['body_text']

    if 'body_html' in data:
        draft.body_html = data['body_html']

    draft.edited = True
    draft.edited_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'status': 'success',
        'draft': draft.to_dict()
    })


@bp.route('/drafts/<int:draft_id>/send', methods=['POST'])
def send_draft(draft_id):
    """Send email draft"""
    draft = Draft.query.get_or_404(draft_id)

    if draft.sent:
        return jsonify({
            'status': 'error',
            'message': 'Draft already sent'
        }), 400

    if draft.channel != 'email':
        return jsonify({
            'status': 'error',
            'message': f'Cannot auto-send via {draft.channel}. Please send manually.'
        }), 400

    job = draft.job
    if not job.recruiter_emails or len(job.recruiter_emails) == 0:
        return jsonify({
            'status': 'error',
            'message': 'No recipient email addresses found'
        }), 400

    # Enqueue send task
    task = send_email_task.apply_async(args=[draft_id])

    return jsonify({
        'status': 'success',
        'message': 'Email queued for sending',
        'task_id': task.id
    })


@bp.route('/drafts/<int:draft_id>/preview')
def preview_draft(draft_id):
    """Preview email HTML (for iframe)"""
    draft = Draft.query.get_or_404(draft_id)
    return draft.body_html or draft.body_text or ''
