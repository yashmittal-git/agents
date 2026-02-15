"""
Job Outreach Agent - Orchestrator Service
Orchestrates extraction-agent, email-agent, research-agent, content-agent, and linkedin-agent
for intelligent job application outreach
"""

from .job_orchestrator import JobOrchestrator

__version__ = "2.0.0"
__all__ = ["JobOrchestrator"]
