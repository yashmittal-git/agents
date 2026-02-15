"""
Content Service
Generic content generation service using AI
Can generate emails, messages, letters, posts, and more
"""

import json
from typing import Dict, Optional, List
from openai import OpenAI


class ContentService:
    """
    Generic content generation service using AI

    Usage:
        content = ContentService(api_key="your-openai-key")

        # Generate email
        email = content.generate_email(
            to_info={"name": "Jane", "company": "Anthropic"},
            context={"purpose": "job application", ...},
            sender_info={"name": "John", ...}
        )

        # Generate LinkedIn message
        message = content.generate_linkedin_message(...)

        # Generate any content
        text = content.generate_content(
            content_type="blog_post",
            context={...}
        )
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o"
    ):
        """
        Initialize content service

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_content(
        self,
        content_type: str,
        context: Dict,
        constraints: Optional[Dict] = None,
        style: Optional[str] = None
    ) -> str:
        """
        Generate any type of content

        Args:
            content_type: Type of content (email, message, post, letter, etc.)
            context: Context and requirements for content
            constraints: Optional constraints (word limit, tone, etc.)
            style: Writing style (professional, casual, friendly, etc.)

        Returns:
            Generated content as string
        """

        constraints = constraints or {}
        max_words = constraints.get("max_words", 500)
        tone = constraints.get("tone", style or "professional")

        prompt = f"""Generate a {content_type} with the following requirements:

Context:
{json.dumps(context, indent=2)}

Constraints:
- Maximum {max_words} words
- Tone: {tone}
{f"- Additional constraints: {constraints.get('additional', '')}" if constraints.get('additional') else ""}

Requirements:
1. Be clear and concise
2. Match the requested tone
3. Include all relevant information from context
4. Stay within word limit

Return just the content text (no JSON, no formatting)."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert content writer. Generate high-quality {content_type} content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating content: {str(e)}"

    def generate_email(
        self,
        to_info: Dict[str, any],
        context: Dict[str, any],
        sender_info: Optional[Dict[str, str]] = None,
        max_words: int = 250,
        include_signature: bool = True
    ) -> Dict[str, str]:
        """
        Generate personalized email

        Args:
            to_info: Recipient information (name, company, role, etc.)
            context: Email context (purpose, details, etc.)
            sender_info: Sender information (name, email, phone, etc.)
            max_words: Maximum words for email body
            include_signature: Whether to include signature

        Returns:
            Dictionary with subject and body
        """

        prompt = f"""Generate a personalized professional email with these details:

Recipient:
{json.dumps(to_info, indent=2)}

Context:
{json.dumps(context, indent=2)}

Requirements:
1. Maximum {max_words} words (body only, excluding signature)
2. Professional and engaging tone
3. Clear subject line
4. Personalized content showing research/understanding
5. Clear call-to-action
6. {"Include sender signature" if include_signature else "No signature needed"}

{f'''Sender Info (for signature):
{json.dumps(sender_info, indent=2)}''' if sender_info and include_signature else ""}

Return JSON with:
- subject: Compelling subject line
- body: Email body (without signature if signature will be added separately)"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at writing compelling, personalized professional emails."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Add signature if requested
            if include_signature and sender_info:
                signature = self._format_signature(sender_info)
                result['body'] = f"{result['body']}\n\n{signature}"

            return result

        except Exception as e:
            return {
                "subject": "Email Subject",
                "body": f"Error generating email: {str(e)}"
            }

    def generate_linkedin_message(
        self,
        to_info: Dict[str, any],
        context: Dict[str, any],
        sender_info: Optional[Dict[str, str]] = None,
        max_chars: int = 300
    ) -> str:
        """
        Generate LinkedIn connection request or message

        Args:
            to_info: Recipient information
            context: Message context
            sender_info: Sender information
            max_chars: Maximum characters (LinkedIn limit: 300 for connection requests)

        Returns:
            LinkedIn message text
        """

        prompt = f"""Generate a LinkedIn message with these details:

Recipient:
{json.dumps(to_info, indent=2)}

Context:
{json.dumps(context, indent=2)}

{f'''Sender:
{json.dumps(sender_info, indent=2)}''' if sender_info else ""}

Requirements:
1. Maximum {max_chars} characters
2. Professional yet personable tone
3. Specific reason for connecting
4. No generic templates
5. Focus on mutual value

Return just the message text (no JSON)."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at writing engaging LinkedIn messages that get responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating LinkedIn message: {str(e)}"

    def generate_cover_letter(
        self,
        job_info: Dict[str, any],
        candidate_info: Dict[str, any],
        company_research: Optional[Dict[str, any]] = None,
        max_words: int = 400
    ) -> str:
        """
        Generate cover letter

        Args:
            job_info: Job details (role, requirements, etc.)
            candidate_info: Candidate details (experience, skills, etc.)
            company_research: Company information (optional)
            max_words: Maximum words

        Returns:
            Cover letter text
        """

        prompt = f"""Generate a compelling cover letter with these details:

Job Information:
{json.dumps(job_info, indent=2)}

Candidate Information:
{json.dumps(candidate_info, indent=2)}

{f'''Company Research:
{json.dumps(company_research, indent=2)}''' if company_research else ""}

Requirements:
1. Maximum {max_words} words
2. Professional tone
3. Show genuine interest in company/role
4. Highlight relevant experience and achievements
5. Explain why candidate is a great fit
6. Professional opening and closing

Return just the cover letter text (no JSON)."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at writing compelling cover letters that stand out."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating cover letter: {str(e)}"

    def generate_social_post(
        self,
        platform: str,
        topic: str,
        context: Optional[Dict] = None,
        style: str = "professional"
    ) -> str:
        """
        Generate social media post

        Args:
            platform: Platform (twitter, linkedin, facebook, etc.)
            topic: Post topic/content
            context: Additional context
            style: Writing style

        Returns:
            Social media post text
        """

        platform_limits = {
            "twitter": 280,
            "linkedin": 3000,
            "facebook": 500,
            "instagram": 2200
        }

        max_chars = platform_limits.get(platform.lower(), 500)

        prompt = f"""Generate a {platform} post with these details:

Topic: {topic}

{f"Context: {json.dumps(context, indent=2)}" if context else ""}

Requirements:
1. Maximum {max_chars} characters
2. Style: {style}
3. Platform-appropriate format and tone
4. Engaging and actionable
5. Include relevant hashtags if appropriate

Return just the post text (no JSON)."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert at creating engaging {platform} content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating post: {str(e)}"

    def _format_signature(self, sender_info: Dict[str, str]) -> str:
        """Format email signature from sender info"""
        signature_parts = ["Best regards,"]

        if sender_info.get("name"):
            signature_parts.append(sender_info["name"])

        if sender_info.get("email"):
            signature_parts.append(sender_info["email"])

        if sender_info.get("phone"):
            signature_parts.append(sender_info["phone"])

        if sender_info.get("linkedin"):
            signature_parts.append(f"LinkedIn: {sender_info['linkedin']}")

        if sender_info.get("portfolio"):
            signature_parts.append(f"Portfolio: {sender_info['portfolio']}")

        return "\n".join(signature_parts)


def main():
    """Test content service"""
    import os

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    content = ContentService(api_key=api_key)

    # Test email generation
    print("Testing email generation...")
    email = content.generate_email(
        to_info={
            "name": "Jane Recruiter",
            "company": "Anthropic",
            "role": "Technical Recruiter"
        },
        context={
            "purpose": "job application",
            "role": "Software Engineer",
            "highlights": "Experience with AI systems, Python, distributed systems"
        },
        sender_info={
            "name": "John Doe",
            "email": "john@example.com",
            "linkedin": "linkedin.com/in/johndoe"
        },
        max_words=200
    )

    print("\nGenerated Email:")
    print(f"Subject: {email['subject']}")
    print(f"\n{email['body']}")


if __name__ == "__main__":
    main()
