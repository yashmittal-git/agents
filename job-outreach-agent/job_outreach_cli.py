#!/usr/bin/env python3
"""
Job Outreach CLI - Easy command-line interface

Usage:
    python job_outreach_cli.py <screenshot.png>
    python job_outreach_cli.py <job_posting.txt>
    python job_outreach_cli.py <url>
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(dotenv_path="../.env")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from job_outreach_agent import JobOrchestrator
from extraction_agent import ExtractionService


def extract_from_image(image_path: str, openai_api_key: str) -> dict:
    """Extract job info from screenshot using extraction-agent"""

    print(f"📸 Extracting job info from image: {image_path}")

    # Use extraction-agent
    extractor = ExtractionService(api_key=openai_api_key)

    schema = {
        "company_name": "Company name",
        "role": "Job role/title",
        "recruiter_email": "Recruiter email (if visible, else null)",
        "recruiter_linkedin": "LinkedIn profile URL (if visible, else null)",
        "recruiter_name": "Recruiter name (if visible, else null)",
        "requirements": "Job requirements (as string)"
    }

    result = extractor.extract(
        content=image_path,
        content_type="image",
        schema=schema,
        instructions="Extract job posting information from this image"
    )

    print(f"✓ Extracted: {result.get('company_name')} - {result.get('role')}")

    return result


def extract_from_text(text_path: str, openai_api_key: str) -> dict:
    """Extract job info from text file using extraction-agent"""

    print(f"📄 Extracting job info from text: {text_path}")

    # Use extraction-agent
    extractor = ExtractionService(api_key=openai_api_key)

    schema = {
        "company_name": "Company name",
        "role": "Job role/title",
        "recruiter_email": "Recruiter email (if available, else null)",
        "recruiter_linkedin": "LinkedIn profile URL (if available, else null)",
        "recruiter_name": "Recruiter name (if available, else null)",
        "requirements": "Job requirements (as string)"
    }

    result = extractor.extract(
        content=text_path,
        content_type="text",
        schema=schema,
        instructions="Extract job posting information from this text"
    )

    print(f"✓ Extracted: {result.get('company_name')} - {result.get('role')}")

    return result


def main():
    """Main CLI entry point"""

    if len(sys.argv) < 2:
        print("Usage: python job_outreach_cli.py <screenshot.png|job.txt>")
        print("")
        print("Examples:")
        print("  python job_outreach_cli.py job_screenshot.png")
        print("  python job_outreach_cli.py job_posting.txt")
        sys.exit(1)

    input_file = sys.argv[1]

    # Check if file exists
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    # Get API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY not found in .env")
        sys.exit(1)

    print("\n" + "="*60)
    print("Job Outreach Agent - Full Workflow")
    print("="*60)

    # Step 1: Extract job info
    print("\n📋 Step 1: Extracting job information...")

    file_ext = Path(input_file).suffix.lower()

    if file_ext in ['.png', '.jpg', '.jpeg']:
        job_info = extract_from_image(input_file, openai_api_key)
    elif file_ext in ['.txt']:
        job_info = extract_from_text(input_file, openai_api_key)
    else:
        print(f"Error: Unsupported file type: {file_ext}")
        print("Supported: .png, .jpg, .jpeg, .txt")
        sys.exit(1)

    # Step 2: Initialize orchestrator with user profile
    print("\n🤖 Step 2: Initializing orchestrator...")

    # Load user profile from environment or use defaults
    user_profile = {
        "name": os.getenv("USER_NAME", "Yash Mittal"),
        "email": os.getenv("USER_EMAIL", "mittal.yash2000@gmail.com"),
        "phone": os.getenv("USER_PHONE", "+91-9756251002"),
        "linkedin": os.getenv("USER_LINKEDIN", "linkedin.com/in/yashmittal-in"),
        "portfolio": os.getenv("USER_PORTFOLIO", "https://yashmittal.co.in"),
        "highlights": [
            "Built AI Voicebot platform with sub-second latency",
            "Scaled to 300K+ automated calls/day",
            "45% cost reduction in TTS/LLM operations",
            "Led team of 4 engineers",
            "AWS to OCI migration (50% cost savings)"
        ],
        "skills": [
            "Python", "Django", "Flask", "FastAPI",
            "AI/ML", "LLMs", "RAG", "Prompt Engineering",
            "AWS", "OCI", "Kubernetes", "Docker",
            "PostgreSQL", "MongoDB", "Redis"
        ],
        "strengths": "Strong technical leadership with proven track record in scaling AI systems"
    }

    orchestrator = JobOrchestrator(
        openai_api_key=openai_api_key,
        gmail_credentials_path="../credentials.json",
        user_profile=user_profile
    )

    # Step 3: Process job (research, match, generate, recommend channel)
    print("\n🎯 Step 3: Processing job application...")
    print("   - Researching company")
    print("   - Matching your experience")
    print("   - Recommending best channel")
    print("   - Generating personalized content")

    result = orchestrator.process_job(
        job_info=job_info,
        auto_send=False  # Always ask for approval
    )

    # Step 4: Ask for approval
    print("\n" + "="*60)
    print("📧 Step 4: Review and Approve")
    print("="*60)

    strategy = result['strategy']

    if strategy['can_auto_send']:
        # Email - can auto-send
        print("\n✓ Email draft ready to send")
        print(f"\nDraft saved to: {result['draft_file']}")
        print("\nReview the email above.")

        response = input("\nSend this email? (yes/no): ").strip().lower()

        if response in ['yes', 'y']:
            print("\n📤 Sending email...")
            success = orchestrator.send_draft(result['draft_file'])

            if success:
                print("\n✅ Email sent successfully!")
            else:
                print("\n❌ Failed to send email")
        else:
            print("\n📝 Email draft saved. You can send it later:")
            print(f"   python -c \"from job_outreach_agent import JobOrchestrator; "
                  f"o = JobOrchestrator(...); o.send_draft('{result['draft_file']}')\"")

    else:
        # LinkedIn or other - requires manual action
        print("\n⚠️  This channel requires manual action")
        print(f"\nDraft saved to: {result['draft_file']}")
        print("\nFollow the instructions above to complete the outreach")

    print("\n" + "="*60)
    print("✅ Workflow complete!")
    print("="*60)


if __name__ == "__main__":
    main()
