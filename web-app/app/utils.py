"""Utility functions for web app"""
import os
from pathlib import Path


def load_user_profile():
    """
    Load user profile from data files and environment variables

    Returns:
        dict: User profile with name, email, highlights, skills, etc.
    """
    # Get paths to data files (relative to agents root, not web-app)
    agents_root = Path(__file__).parent.parent.parent
    data_dir = agents_root / 'job-outreach-agent' / 'data'

    # Load resume content
    resume_file = data_dir / 'resume_content.txt'
    portfolio_file = data_dir / 'portfolio_content.txt'

    resume_content = ""
    portfolio_content = ""

    if resume_file.exists():
        with open(resume_file, 'r') as f:
            resume_content = f.read()

    if portfolio_file.exists():
        with open(portfolio_file, 'r') as f:
            portfolio_content = f.read()

    # Build user profile from environment and data files
    profile = {
        "name": os.getenv('USER_NAME', 'Yash Mittal'),
        "email": os.getenv('USER_EMAIL', 'mittal.yash2000@gmail.com'),
        "linkedin": os.getenv('USER_LINKEDIN', 'linkedin.com/in/yashmittal-in'),
        "portfolio": os.getenv('USER_PORTFOLIO', 'https://yashmittal.co.in'),
        "phone": os.getenv('USER_PHONE', '+91-9756251002'),

        # Key highlights from resume/portfolio
        "highlights": [
            "Built AI Voicebot platform with sub-second latency",
            "Scaled to 300K+ automated calls/day",
            "45% cost reduction in TTS/LLM operations",
            "Led team of 4 engineers",
            "Tech Lead at Convin.ai"
        ],

        # Technical skills
        "skills": [
            "Python", "Go", "AI/ML", "Distributed Systems",
            "AWS", "Kubernetes", "Docker", "PostgreSQL",
            "Redis", "RabbitMQ", "Microservices"
        ],

        # Brief strengths summary
        "strengths": "Strong technical leadership with proven track record in scaling AI systems and cost optimization",

        # Full resume and portfolio content for context
        "resume_text": resume_content,
        "portfolio_text": portfolio_content
    }

    return profile
