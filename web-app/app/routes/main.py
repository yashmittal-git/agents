"""Main routes - home page and file upload"""
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.database import db
from app.models import Job
from app.tasks import process_job_task

bp = Blueprint('main', __name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/')
def index():
    """Home page with upload form"""
    return render_template('index.html')


@bp.route('/upload', methods=['POST'])
def upload():
    """Handle file/text upload and create job"""

    # Determine source type
    source_type = request.form.get('source_type', 'image')
    user_context = request.form.get('user_context', '').strip()

    if source_type == 'text':
        # Text input
        text_content = request.form.get('text_content', '').strip()
        if not text_content:
            flash('Please provide job posting text', 'error')
            return redirect(url_for('main.index'))

        # Save text to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f'job_text_{timestamp}.txt')
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        with open(filepath, 'w') as f:
            f.write(text_content)

        source_file = filepath

    elif source_type == 'url':
        # URL input
        url = request.form.get('url', '').strip()
        if not url:
            flash('Please provide a URL', 'error')
            return redirect(url_for('main.index'))

        source_file = url

    else:
        # File upload (image/PDF)
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('main.index'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('main.index'))

        if not allowed_file(file.filename):
            flash('Invalid file type. Allowed: PNG, JPG, JPEG, GIF, PDF, TXT', 'error')
            return redirect(url_for('main.index'))

        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f'{timestamp}_{file.filename}')
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        source_file = filepath

    # Create job in database
    job = Job(
        source_type=source_type,
        source_file=source_file,
        user_context=user_context if user_context else None,
        status='pending'
    )
    db.session.add(job)
    db.session.commit()

    # Enqueue async task
    task = process_job_task.apply_async(args=[job.id])
    job.task_id = task.id
    db.session.commit()

    flash('Job uploaded successfully! Processing...', 'success')
    return redirect(url_for('jobs.job_detail', job_id=job.id))
