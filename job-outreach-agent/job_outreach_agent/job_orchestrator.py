"""
Job Orchestrator
Orchestrates the 4 external agent services for job outreach
"""

import json
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime

# Import external agent services
from email_agent import EmailService
from research_agent import ResearchService
from content_agent import ContentService
from linkedin_agent import LinkedInService


class JobOrchestrator:
    """
    Orchestrates job outreach using 4 external agent services

    Responsibilities:
    - Extract job information
    - Match candidate experience
    - Recommend outreach channel (email vs LinkedIn)
    - Orchestrate research, content generation, and sending
    - Provide intelligent guidance for manual actions

    Does NOT:
    - Send emails directly (delegates to email-agent)
    - Research companies (delegates to research-agent)
    - Generate content (delegates to content-agent)
    - Handle LinkedIn (delegates to linkedin-agent)
    """

    def __init__(
        self,
        openai_api_key: str,
        gmail_credentials_path: str = "credentials.json",
        user_profile: Optional[Dict] = None
    ):
        """
        Initialize orchestrator with external agents

        Args:
            openai_api_key: OpenAI API key for content/research
            gmail_credentials_path: Path to Gmail credentials
            user_profile: User profile (resume, contact info, etc.)
        """
        # Initialize external agents
        self.email_agent = EmailService(
            credentials_path=gmail_credentials_path,
            sender_email=user_profile.get('email') if user_profile else None,
            sender_name=user_profile.get('name') if user_profile else None
        )

        self.research_agent = ResearchService(api_key=openai_api_key)
        self.content_agent = ContentService(api_key=openai_api_key)
        self.linkedin_agent = LinkedInService()

        # Store user profile
        self.user_profile = user_profile or {}

        # Create drafts directory
        self.drafts_dir = Path("outreach_drafts")
        self.drafts_dir.mkdir(exist_ok=True)

    def process_job(
        self,
        job_info: Dict[str, str],
        auto_send: bool = False
    ) -> Dict:
        """
        Process job application with intelligent channel recommendation

        Args:
            job_info: Job information dict with keys:
                - company_name: Company name
                - role: Job role
                - recruiter_email: Recruiter email (if available)
                - recruiter_linkedin: LinkedIn profile (if available)
                - requirements: Job requirements
            auto_send: Whether to auto-send if channel supports it

        Returns:
            Dictionary with strategy and results
        """

        print(f"\n{'='*60}")
        print(f"Processing Job Application")
        print(f"{'='*60}")
        print(f"Company: {job_info.get('company_name')}")
        print(f"Role: {job_info.get('role')}")
        print(f"{'='*60}\n")

        # Step 1: Research company
        print("📊 Researching company...")
        company_research = self.research_agent.research_company(
            company_name=job_info['company_name'],
            context=f"for job application as {job_info.get('role', '')}"
        )
        print(f"✓ Research complete: {company_research.get('stage')} stage")

        # Step 2: Match experience with requirements
        print("\n🎯 Matching experience...")
        experience_match = self._match_experience(
            job_info=job_info,
            company_research=company_research
        )
        print(f"✓ Match score: {experience_match.get('relevance_score', 0)}/10")

        # Step 3: Recommend channel (email vs LinkedIn)
        print("\n🤔 Analyzing best outreach channel...")
        channel_recommendation = self._recommend_channel(
            job_info=job_info,
            company_research=company_research
        )

        primary_channel = channel_recommendation['primary_channel']
        print(f"✓ Recommended: {primary_channel.upper()}")
        print(f"  Reason: {channel_recommendation['reason']}")

        # Step 4: Create outreach strategy
        print(f"\n✍️  Creating {primary_channel} content...")
        strategy = self._create_strategy(
            channel=primary_channel,
            job_info=job_info,
            company_research=company_research,
            experience_match=experience_match,
            channel_recommendation=channel_recommendation
        )
        print("✓ Content created")

        # Step 5: Save draft
        draft_file = self._save_draft({
            "job_info": job_info,
            "company_research": company_research,
            "experience_match": experience_match,
            "channel_recommendation": channel_recommendation,
            "strategy": strategy,
            "status": "draft"
        })

        print(f"\n💾 Draft saved: {draft_file}")

        # Step 6: Display strategy to user
        self._display_strategy(strategy, channel_recommendation)

        # Step 7: Auto-send if requested and channel supports it
        if auto_send and strategy['can_auto_send']:
            print("\n📧 Auto-sending (auto_send=True)...")
            result = self._execute_strategy(strategy, job_info)
            return {
                "draft_file": draft_file,
                "strategy": strategy,
                "sent": result
            }

        return {
            "draft_file": draft_file,
            "strategy": strategy,
            "sent": False
        }

    def send_draft(self, draft_file: str) -> bool:
        """
        Send a saved draft

        Args:
            draft_file: Path to draft JSON file

        Returns:
            True if sent successfully
        """
        # Load draft
        with open(draft_file, 'r') as f:
            draft = json.load(f)

        if draft.get('status') == 'sent':
            print("⚠ This draft has already been sent")
            return False

        strategy = draft['strategy']

        if not strategy['can_auto_send']:
            print("⚠ This channel requires manual action")
            self._display_strategy(strategy, draft['channel_recommendation'])
            return False

        # Send via appropriate channel
        result = self._execute_strategy(strategy, draft['job_info'])

        if result:
            # Update draft status
            draft['status'] = 'sent'
            draft['sent_at'] = datetime.now().isoformat()
            with open(draft_file, 'w') as f:
                json.dump(draft, f, indent=2)

        return result

    def _match_experience(
        self,
        job_info: Dict,
        company_research: Dict
    ) -> Dict:
        """Match user experience with job requirements"""

        # For now, create a simple match object
        # In full implementation, this would use AI to analyze resume
        return {
            "relevant_experience": self.user_profile.get('highlights', []),
            "matching_skills": self.user_profile.get('skills', []),
            "relevance_score": 9,
            "unique_strengths": self.user_profile.get('strengths', '')
        }

    def _recommend_channel(
        self,
        job_info: Dict,
        company_research: Dict
    ) -> Dict:
        """
        Recommend best outreach channel

        Logic:
        - If email available → Email (90% confidence)
        - If LinkedIn available + no email → LinkedIn (85% confidence)
        - If both available + senior role → LinkedIn preferred (80% confidence)
        - If both available + startup → LinkedIn preferred (85% confidence)
        """

        has_email = bool(job_info.get('recruiter_email'))
        has_linkedin = bool(job_info.get('recruiter_linkedin'))
        is_senior = 'senior' in job_info.get('role', '').lower() or 'lead' in job_info.get('role', '').lower()
        is_startup = company_research.get('stage', '').lower() in ['startup', 'growth']

        # Decision logic
        if has_email and not has_linkedin:
            return {
                "primary_channel": "email",
                "confidence": 0.90,
                "reason": "Direct email address available",
                "alternatives": []
            }

        if has_linkedin and not has_email:
            return {
                "primary_channel": "linkedin",
                "confidence": 0.85,
                "reason": "LinkedIn available, no email found",
                "alternatives": []
            }

        if has_both := (has_email and has_linkedin):
            if is_senior or is_startup:
                return {
                    "primary_channel": "linkedin",
                    "confidence": 0.85 if is_startup else 0.80,
                    "reason": f"{'Startup culture' if is_startup else 'Senior role'} - LinkedIn preferred",
                    "alternatives": [{"channel": "email", "confidence": 0.70}]
                }
            else:
                return {
                    "primary_channel": "email",
                    "confidence": 0.85,
                    "reason": "Professional email preferred",
                    "alternatives": [{"channel": "linkedin", "confidence": 0.75}]
                }

        # Default: email if any contact info
        return {
            "primary_channel": "email",
            "confidence": 0.50,
            "reason": "Default to email",
            "alternatives": []
        }

    def _create_strategy(
        self,
        channel: str,
        job_info: Dict,
        company_research: Dict,
        experience_match: Dict,
        channel_recommendation: Dict
    ) -> Dict:
        """Create outreach strategy for recommended channel"""

        if channel == "email":
            # Generate email content using content-agent
            email_content = self.content_agent.generate_email(
                to_info={
                    "name": job_info.get('recruiter_name', 'Hiring Team'),
                    "company": job_info['company_name'],
                    "role": job_info.get('role', '')
                },
                context={
                    "purpose": "job application",
                    "role": job_info.get('role'),
                    "specific_interest": "Tech and Engineering leadership roles" if "leadership" in job_info.get('role', '').lower() else job_info.get('role'),
                    "job_source": job_info.get('source', 'your job posting'),  # e.g., "your LinkedIn post"
                    "company_info": company_research.get('what_they_build'),
                    "tech_stack": company_research.get('tech_stack'),
                    "candidate_highlights": experience_match.get('relevant_experience'),
                    "latest_project_focus": "AI Voicebot platform with sub-second latency, scaled to 300K+ calls/day",
                    "user_custom_context": job_info.get('user_context')  # User's additional context/instructions
                },
                sender_info=self.user_profile,
                max_words=250,
                include_signature=True
            )

            return {
                "channel": "email",
                "content": email_content,
                "can_auto_send": True,
                "instructions": None
            }

        elif channel == "linkedin":
            # Generate LinkedIn message using content-agent
            linkedin_message = self.content_agent.generate_linkedin_message(
                to_info={
                    "name": job_info.get('recruiter_name', ''),
                    "company": job_info['company_name'],
                    "role": job_info.get('role', '')
                },
                context={
                    "purpose": "job application",
                    "role": job_info.get('role'),
                    "company_interest": company_research.get('what_they_build')
                },
                sender_info=self.user_profile,
                max_chars=300
            )

            # Create manual instructions
            instructions = self._create_linkedin_instructions(
                job_info=job_info,
                message=linkedin_message
            )

            return {
                "channel": "linkedin",
                "content": {"message": linkedin_message},
                "can_auto_send": False,
                "instructions": instructions
            }

        return {}

    def _create_linkedin_instructions(self, job_info: Dict, message: str) -> Dict:
        """Create step-by-step LinkedIn instructions"""

        profile_url = job_info.get('recruiter_linkedin', '')

        return {
            "steps": [
                f"1. Open LinkedIn and go to: {profile_url}",
                "2. Click the 'Connect' or 'Message' button",
                "3. If connecting, click 'Add a note'",
                "4. Copy and paste the message below:",
                "5. Review and personalize if needed",
                "6. Click 'Send'!"
            ],
            "message": message,
            "tips": [
                "LinkedIn messages work best 9-11 AM on weekdays",
                "Connection notes are limited to 300 characters",
                "Follow up after 3-5 days if no response"
            ]
        }

    def _execute_strategy(self, strategy: Dict, job_info: Dict) -> bool:
        """Execute outreach strategy (send via appropriate channel)"""

        if strategy['channel'] == 'email':
            # Use email-agent to send
            content = strategy['content']

            # Get all email addresses (support multiple recipients)
            to_emails = job_info.get('all_emails') or [job_info.get('recruiter_email')]
            if not to_emails or not to_emails[0]:
                print("❌ No recipient email addresses found")
                return False

            # Always BCC sender's email for record keeping
            bcc_email = self.user_profile.get('email')

            # Check if content has HTML formatting
            is_html = content.get('is_html', False)
            email_body = content.get('body_html', content.get('body'))

            success = self.email_agent.send(
                to=to_emails if len(to_emails) > 1 else to_emails[0],  # Pass list if multiple, string if single
                subject=content['subject'],
                body=email_body,
                bcc=bcc_email,  # Add sender to BCC
                is_html=is_html  # Support HTML formatting
            )

            if success and bcc_email:
                print(f"📋 BCC: {bcc_email} (you'll receive a copy)")

            return success

        elif strategy['channel'] == 'linkedin':
            # LinkedIn requires manual action
            # Use linkedin-agent to provide guidance
            result = self.linkedin_agent.send_connection_request(
                profile_url=job_info.get('recruiter_linkedin', ''),
                message=strategy['content']['message']
            )

            return result['status'] == 'manual_action_required'

        return False

    def _display_strategy(self, strategy: Dict, channel_rec: Dict):
        """Display strategy to user"""

        print(f"\n{'='*60}")
        print("OUTREACH STRATEGY")
        print(f"{'='*60}")

        print(f"\nChannel: {strategy['channel'].upper()}")
        print(f"Confidence: {channel_rec['confidence']*100:.0f}%")
        print(f"Reason: {channel_rec['reason']}")

        if strategy['can_auto_send']:
            print("\n✓ This channel supports automatic sending")
            print("  Review the content below and use send_draft() to send")
        else:
            print("\n⚠ This channel requires manual action")
            print("\nFollow these steps:")

        # Display content
        if strategy['channel'] == 'email':
            content = strategy['content']
            print(f"\nSubject: {content['subject']}\n")
            print("Body:")
            print("-"*60)
            print(content['body'])
            print("-"*60)

        elif strategy['channel'] == 'linkedin':
            if strategy.get('instructions'):
                for step in strategy['instructions']['steps']:
                    print(f"  {step}")

                print(f"\n{'='*60}")
                print("MESSAGE TO SEND:")
                print(f"{'='*60}")
                print(strategy['instructions']['message'])
                print(f"{'='*60}")

                if strategy['instructions'].get('tips'):
                    print("\nTips:")
                    for tip in strategy['instructions']['tips']:
                        print(f"  • {tip}")

        # Display alternatives
        if channel_rec.get('alternatives'):
            print("\nAlternative Channels:")
            for alt in channel_rec['alternatives']:
                print(f"  - {alt['channel']} (confidence: {alt['confidence']*100:.0f}%)")

        print(f"{'='*60}\n")

    def _save_draft(self, draft_data: Dict) -> str:
        """Save draft to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company = draft_data['job_info']['company_name'].replace(' ', '_')
        filename = f"{timestamp}_{company}.json"
        filepath = self.drafts_dir / filename

        draft_data['generated_at'] = datetime.now().isoformat()

        with open(filepath, 'w') as f:
            json.dump(draft_data, f, indent=2)

        return str(filepath)
