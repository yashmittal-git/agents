"""
Real agent integration tests

These tests actually call the agent services to verify they work correctly
with the web app's task code.

IMPORTANT: These require valid OPENAI_API_KEY in environment
"""

import os
import sys
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check if we should skip tests (no API key)
SKIP_REASON = "OPENAI_API_KEY not set" if not os.getenv('OPENAI_API_KEY') else None


class TestContentAgentIntegration:
    """Test ContentService with actual API calls"""

    @pytest.mark.skipif(SKIP_REASON is not None, reason=SKIP_REASON)
    def test_generate_email_with_correct_params(self):
        """Test that generate_email works with the parameters we use in tasks.py"""
        from content_agent import ContentService

        service = ContentService(api_key=os.getenv('OPENAI_API_KEY'))

        # These are the exact parameters from tasks.py
        to_info = {
            "name": "Jane Recruiter",
            "company": "Anthropic",
            "role": "Software Engineer"
        }

        context = {
            "purpose": "job_application",
            "job_role": "Software Engineer",
            "company": "Anthropic",
            "company_research": {
                "overview": "Anthropic is an AI safety company",
                "products": ["Claude"],
                "focus": "AI safety and alignment"
            },
            "user_custom_context": "I'm particularly interested in AI safety work"
        }

        sender_info = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "linkedin": "linkedin.com/in/testuser",
            "portfolio": "https://testuser.com",
            "highlights": [
                "Built AI systems",
                "Led engineering teams"
            ],
            "skills": ["Python", "AI/ML"],
            "strengths": "Strong technical background"
        }

        # This should not raise an error
        result = service.generate_email(
            to_info=to_info,
            context=context,
            sender_info=sender_info,
            max_words=250
        )

        # Verify result structure
        assert 'subject' in result
        assert 'body' in result
        assert 'body_html' in result
        assert isinstance(result['subject'], str)
        assert len(result['subject']) > 0

    @pytest.mark.skipif(SKIP_REASON is not None, reason=SKIP_REASON)
    def test_extraction_service_basic(self):
        """Test ExtractionService with text content"""
        from extraction_agent import ExtractionService

        service = ExtractionService(api_key=os.getenv('OPENAI_API_KEY'))

        test_text = """
        Software Engineer at Anthropic

        We're hiring a Software Engineer to work on Claude.

        Requirements:
        - Python expertise
        - AI/ML experience

        Contact: careers@anthropic.com
        Recruiter: Jane Smith
        """

        schema = {
            "company_name": "string",
            "role": "string",
            "recruiter_name": "string or null",
            "recruiter_emails": "array of emails"
        }

        result = service.extract(
            content=test_text,
            content_type='text',
            schema=schema,
            instructions="Extract job posting information"
        )

        assert 'company_name' in result
        assert 'role' in result
        assert result['company_name'] == 'Anthropic' or 'anthropic' in result['company_name'].lower()

    @pytest.mark.skipif(SKIP_REASON is not None, reason=SKIP_REASON)
    def test_research_service_basic(self):
        """Test ResearchService with company research"""
        from research_agent import ResearchService

        service = ResearchService(api_key=os.getenv('OPENAI_API_KEY'))

        # Use a well-known company for reliable results
        result = service.research_company(
            company_name="Anthropic",
            context="for job application"
        )

        assert isinstance(result, dict)
        # Research should return some data
        assert len(result) > 0


class TestTasksParametersMatch:
    """Verify tasks.py uses correct parameters for all agents"""

    def test_content_service_parameters_match(self):
        """Verify ContentService.generate_email signature matches tasks.py usage"""
        from content_agent import ContentService
        import inspect

        sig = inspect.signature(ContentService.generate_email)
        params = list(sig.parameters.keys())

        # Should have these parameters
        assert 'to_info' in params
        assert 'context' in params
        assert 'sender_info' in params
        assert 'max_words' in params

        # Should NOT have these (old wrong parameters)
        assert 'recipient_name' not in params
        assert 'recipient_company' not in params
        assert 'job_role' not in params
        assert 'company_research' not in params
        assert 'user_profile' not in params
        assert 'user_context' not in params

    def test_extraction_service_parameters_match(self):
        """Verify ExtractionService.extract signature matches tasks.py usage"""
        from extraction_agent import ExtractionService
        import inspect

        sig = inspect.signature(ExtractionService.extract)
        params = list(sig.parameters.keys())

        assert 'content' in params
        assert 'content_type' in params
        assert 'schema' in params
        assert 'instructions' in params

    def test_research_service_parameters_match(self):
        """Verify ResearchService.research_company signature matches tasks.py usage"""
        from research_agent import ResearchService
        import inspect

        sig = inspect.signature(ResearchService.research_company)
        params = list(sig.parameters.keys())

        assert 'company_name' in params
        assert 'context' in params


def run_tests():
    """Run agent integration tests"""
    print("="*60)
    print("Running Agent Integration Tests")
    print("="*60)

    if not os.getenv('OPENAI_API_KEY'):
        print("\nWARNING: OPENAI_API_KEY not set - API tests will be skipped")
        print("Set OPENAI_API_KEY to run full integration tests\n")

    pytest.main([
        __file__,
        '-v',
        '-s',
        '--tb=short',
        '--color=yes'
    ])


if __name__ == '__main__':
    run_tests()
