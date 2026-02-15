"""
Example Usage of Job Outreach Agent v2.0

Demonstrates the orchestrator using 4 external agent services
"""

import os
from job_outreach_agent import JobOrchestrator


def example_email_outreach():
    """Example: Email outreach (auto-sendable)"""

    print("\n" + "="*60)
    print("Example 1: Email Outreach")
    print("="*60)

    # Initialize orchestrator
    orchestrator = JobOrchestrator(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        gmail_credentials_path="credentials.json",
        user_profile={
            "name": "Yash Mittal",
            "email": "mittal.yash2000@gmail.com",
            "linkedin": "linkedin.com/in/yashmittal-in",
            "portfolio": "https://yashmittal.co.in",
            "phone": "+91-9756251002",
            "highlights": [
                "Built AI Voicebot platform with sub-second latency",
                "Scaled to 300K+ automated calls/day",
                "45% cost reduction in TTS/LLM operations",
                "Led team of 4 engineers"
            ],
            "skills": ["Python", "AI/ML", "Distributed Systems", "AWS", "Kubernetes"],
            "strengths": "Strong technical leadership with proven track record in scaling AI systems"
        }
    )

    # Process job with email
    result = orchestrator.process_job(
        job_info={
            "company_name": "Anthropic",
            "role": "Software Engineer",
            "recruiter_email": "careers@anthropic.com",
            "requirements": "Python, AI/ML, distributed systems, 5+ years experience"
        },
        auto_send=False  # Set to True to auto-send
    )

    print(f"\nResult: {result['draft_file']}")
    print(f"Sent: {result['sent']}")

    # To send later:
    # orchestrator.send_draft(result['draft_file'])


def example_linkedin_outreach():
    """Example: LinkedIn outreach (manual guidance)"""

    print("\n" + "="*60)
    print("Example 2: LinkedIn Outreach (Manual Guidance)")
    print("="*60)

    orchestrator = JobOrchestrator(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        user_profile={
            "name": "Yash Mittal",
            "email": "mittal.yash2000@gmail.com",
            "highlights": ["AI Voicebot", "300K+ calls/day", "Tech Lead"],
            "skills": ["Python", "AI/ML"]
        }
    )

    # Process job with LinkedIn only
    result = orchestrator.process_job(
        job_info={
            "company_name": "Anthropic",
            "role": "Senior Software Engineer",  # Senior role
            "recruiter_linkedin": "linkedin.com/in/jane-recruiter",
            "requirements": "AI safety, Python, distributed systems"
        }
    )

    print(f"\nResult: {result['draft_file']}")
    print("LinkedIn requires manual action - follow the instructions above")


def example_smart_recommendation():
    """Example: Smart channel recommendation"""

    print("\n" + "="*60)
    print("Example 3: Smart Channel Recommendation")
    print("="*60)

    orchestrator = JobOrchestrator(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        user_profile={"name": "Yash", "email": "yash@test.com"}
    )

    # Both email and LinkedIn available - system chooses best
    result = orchestrator.process_job(
        job_info={
            "company_name": "OpenAI",
            "role": "Senior ML Engineer",  # Senior + AI company = LinkedIn preferred
            "recruiter_email": "careers@openai.com",
            "recruiter_linkedin": "linkedin.com/in/recruiter",
            "requirements": "ML, Python, research"
        }
    )

    print(f"\nChosen channel: {result['strategy']['channel']}")
    print("System intelligently chose based on role level and company culture")


def main():
    """Run examples"""

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it: export OPENAI_API_KEY='your-key'")
        return

    print("\n" + "="*60)
    print("Job Outreach Agent v2.0 - Examples")
    print("Demonstrates orchestration of 4 external agent services")
    print("="*60)

    try:
        # Run examples
        example_email_outreach()
        # example_linkedin_outreach()
        # example_smart_recommendation()

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure all agents are installed:")
        print("  pip install -r requirements.txt")


if __name__ == "__main__":
    main()
