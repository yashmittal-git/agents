"""Job routes - list and detail views"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database import db
from app.models import Job, Draft

bp = Blueprint('jobs', __name__, url_prefix='/jobs')


@bp.route('/')
def job_list():
    """List all jobs with filtering"""
    # Get filter parameters
    status_filter = request.args.get('status', '')
    search_query = request.args.get('q', '').strip()

    # Build query
    query = Job.query

    if status_filter:
        query = query.filter(Job.status == status_filter)

    if search_query:
        # Search in company name and role
        search_pattern = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Job.company_name.ilike(search_pattern),
                Job.role.ilike(search_pattern)
            )
        )

    # Order by most recent first
    jobs = query.order_by(Job.created_at.desc()).all()

    # Get status counts for filter badges
    status_counts = {
        'all': Job.query.count(),
        'pending': Job.query.filter(Job.status.in_(['pending', 'extracting', 'researching', 'generating'])).count(),
        'drafted': Job.query.filter_by(status='drafted').count(),
        'sent': Job.query.filter_by(status='sent').count(),
        'failed': Job.query.filter_by(status='failed').count(),
    }

    return render_template(
        'jobs.html',
        jobs=jobs,
        status_filter=status_filter,
        search_query=search_query,
        status_counts=status_counts
    )


@bp.route('/<int:job_id>')
def job_detail(job_id):
    """Job detail page with draft editor"""
    job = Job.query.get_or_404(job_id)

    # Get the latest draft (if any)
    draft = Draft.query.filter_by(job_id=job_id).order_by(Draft.created_at.desc()).first()

    return render_template(
        'job_detail.html',
        job=job,
        draft=draft
    )


@bp.route('/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    """Delete a job and its drafts"""
    job = Job.query.get_or_404(job_id)

    db.session.delete(job)
    db.session.commit()

    flash(f'Job deleted: {job.company_name} - {job.role}', 'success')
    return redirect(url_for('jobs.job_list'))
