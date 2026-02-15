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
import os
from flask import Blueprint, jsonify, request, send_file
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


@bp.route('/jobs/<int:job_id>/source')
def view_source(job_id):
    """View the original source content (image, text, or URL)"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"view_source called for job_id: {job_id}")

    job = Job.query.get_or_404(job_id)
    logger.info(f"Job found: {job.company_name}, source_type: {job.source_type}, source_file: {job.source_file}")

    if not job.source_file:
        logger.warning(f"No source file for job {job_id}")
        return jsonify({'error': 'No source file'}), 404

    # Helper function to normalize file path
    def normalize_path(file_path):
        """Fix paths - handle both relative and absolute paths"""
        # If it's a relative path (like 'uploads/file.png'), make it absolute
        if not file_path.startswith('/'):
            file_path = os.path.join('/app', file_path)

        # Fix paths that have /app/app instead of /app
        if file_path.startswith('/app/app/'):
            file_path = file_path.replace('/app/app/', '/app/', 1)

        return file_path

    # For images, serve the file directly
    if job.source_type == 'image':
        file_path = normalize_path(job.source_file)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': f'File not found: {file_path}'}), 404

    # For text, read and return the content
    elif job.source_type == 'text':
        file_path = normalize_path(job.source_file)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            return jsonify({
                'type': 'text',
                'content': content,
                'filename': os.path.basename(file_path)
            })
        else:
            return jsonify({'error': f'File not found: {file_path}'}), 404

    # For URLs, return the URL
    elif job.source_type == 'url':
        return jsonify({
            'type': 'url',
            'url': job.source_file
        })
