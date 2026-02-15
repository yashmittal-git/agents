#!/usr/bin/env python3
"""
Send Draft - Send a saved draft email

Usage:
    python send_draft.py <draft_json_path>
"""

import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(dotenv_path="../.env")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from job_outreach_agent import JobOrchestrator


def send_draft(draft_path: str):
    """Send a draft email"""

    # Check if draft exists
    if not os.path.exists(draft_path):
        print(f"❌ Error: Draft not found: {draft_path}")
        return False

    # Load draft
    with open(draft_path, 'r') as f:
        draft = json.load(f)

    # Display draft info
    job_info = draft.get('job_info', {})
    content = draft.get('strategy', {}).get('content', {})

    # Get all emails
    all_emails = job_info.get('all_emails', [])
    if not all_emails and job_info.get('recruiter_email'):
        all_emails = [job_info.get('recruiter_email')]

    print("\n" + "="*60)
    print("📧 Sending Draft")
    print("="*60)
    print(f"Company: {job_info.get('company_name')}")
    print(f"Role: {job_info.get('role')}")
    print(f"To ({len(all_emails)} recipient{'s' if len(all_emails) > 1 else ''}):")
    for email in all_emails:
        print(f"  - {email}")
    print(f"Subject: {content.get('subject')}")
    print("="*60)

    # Confirm
    response = input(f"\n⚠️  Send to {len(all_emails)} recipient{'s' if len(all_emails) > 1 else ''}? (yes/no): ").strip().lower()

    if response != 'yes':
        print("❌ Cancelled. Email not sent.")
        return False

    # Initialize orchestrator
    print("\n📤 Initializing email service...")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    gmail_credentials_path = os.getenv("GMAIL_CREDENTIALS_PATH", "../credentials.json")

    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment")
        return False

    # Get user profile from environment or use defaults
    user_profile = {
        "name": os.getenv("USER_NAME", "Yash Mittal"),
        "email": os.getenv("USER_EMAIL", "mittal.yash2000@gmail.com"),
        "phone": os.getenv("USER_PHONE", "+91-9756251002"),
        "linkedin": os.getenv("USER_LINKEDIN", "linkedin.com/in/yashmittal-in"),
        "portfolio": os.getenv("USER_PORTFOLIO", "https://yashmittal.co.in"),
        "resume": os.getenv("USER_RESUME", "https://resume.yashmittal.co.in"),
    }

    orchestrator = JobOrchestrator(
        openai_api_key=openai_api_key,
        gmail_credentials_path=gmail_credentials_path,
        user_profile=user_profile
    )

    # Send draft
    print(f"📧 Sending email to {len(all_emails)} recipient{'s' if len(all_emails) > 1 else ''}...")
    success = orchestrator.send_draft(draft_path)

    if success:
        print("\n✅ Email sent successfully!")
        print(f"📬 Sent to:")
        for email in all_emails:
            print(f"  ✓ {email}")
        return True
    else:
        print("\n❌ Failed to send email. Check the error above.")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python send_draft.py <draft_json_path>")
        print("\nExample:")
        print("  python send_draft.py outreach_drafts/20260215_154957_MyOperator.json")
        sys.exit(1)

    draft_path = sys.argv[1]
    send_draft(draft_path)


if __name__ == '__main__':
    main()
