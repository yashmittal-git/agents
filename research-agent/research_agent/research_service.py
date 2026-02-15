"""
Research Service
Generic web research service using web scraping and AI
Can be used to research companies, products, markets, competitors, etc.
"""

import requests
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from openai import OpenAI


class ResearchService:
    """
    Generic research service for web-based research

    Usage:
        research = ResearchService(api_key="your-openai-key")
        result = research.research_company("Anthropic")
        result = research.research_topic("AI safety trends 2024")
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o"
    ):
        """
        Initialize research service

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def fetch_website(self, url: str) -> str:
        """
        Fetch and parse website content

        Args:
            url: Website URL to fetch

        Returns:
            Parsed text content from website
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()

                # Get text content
                content = soup.get_text(separator='\n', strip=True)

                # Limit to first 5000 characters
                return content[:5000]

            return ""

        except Exception as e:
            print(f"Error fetching website: {e}")
            return ""

    def find_company_website(self, company_name: str) -> Optional[str]:
        """
        Try to find company website URL

        Args:
            company_name: Name of the company

        Returns:
            Website URL if found, None otherwise
        """
        # Try common URL patterns
        possible_urls = [
            f"https://www.{company_name.lower().replace(' ', '')}.com",
            f"https://{company_name.lower().replace(' ', '')}.com",
            f"https://www.{company_name.lower().replace(' ', '')}.io",
            f"https://{company_name.lower().replace(' ', '')}.io",
            f"https://www.{company_name.lower().replace(' ', '')}.ai",
        ]

        for url in possible_urls:
            try:
                response = requests.head(url, timeout=3, allow_redirects=True)
                if response.status_code == 200:
                    return url
            except:
                continue

        return None

    def research_company(
        self,
        company_name: str,
        context: str = "",
        website_url: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Research a company

        Args:
            company_name: Name of the company
            context: Additional context (e.g., "for job application", "for investment")
            website_url: Company website URL (optional, will try to find if not provided)

        Returns:
            Dictionary with research findings:
            {
                "what_they_build": str,
                "tech_stack": List[str],
                "stage": str,
                "relevant_context": str
            }
        """

        # Fetch website content
        if not website_url:
            website_url = self.find_company_website(company_name)

        website_content = ""
        if website_url:
            website_content = self.fetch_website(website_url)

        # Use AI to analyze and extract information
        prompt = f"""Research and analyze the following company: {company_name}
{f"Context: {context}" if context else ""}

Based on available information, provide:
1. what_they_build: What products/services they build (2-3 sentences)
2. tech_stack: Technologies they likely use (array of key technologies)
3. stage: Company stage (startup/growth/established/enterprise)
4. relevant_context: Any other relevant information

Website content (if available):
{website_content[:3000] if website_content else "No website content available"}

Return as JSON format with these exact keys: what_they_build, tech_stack, stage, relevant_context"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a company research assistant. Analyze companies and provide structured, factual insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Add metadata
            result["company_name"] = company_name
            result["website_url"] = website_url

            return result

        except Exception as e:
            print(f"Research error: {e}")
            return {
                "company_name": company_name,
                "what_they_build": "Information not available",
                "tech_stack": [],
                "stage": "Unknown",
                "relevant_context": f"Research failed: {str(e)}",
                "website_url": website_url
            }

    def research_topic(
        self,
        topic: str,
        depth: str = "medium",
        sources: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Research a general topic

        Args:
            topic: Topic to research
            depth: Research depth (quick/medium/deep)
            sources: Optional list of source URLs to analyze

        Returns:
            Dictionary with research findings
        """

        # Fetch content from sources if provided
        source_content = ""
        if sources:
            for url in sources[:3]:  # Limit to 3 sources
                content = self.fetch_website(url)
                if content:
                    source_content += f"\n\nSource: {url}\n{content[:1000]}\n"

        # Determine prompt based on depth
        depth_instructions = {
            "quick": "Provide a brief summary (2-3 sentences)",
            "medium": "Provide a comprehensive overview with key points",
            "deep": "Provide detailed analysis with insights and implications"
        }

        # Build sources section
        sources_section = f"Sources to analyze:\n{source_content}" if source_content else ""

        prompt = f"""Research the following topic: {topic}

{depth_instructions.get(depth, depth_instructions["medium"])}

{sources_section}

Provide structured findings including:
1. summary: Overview of the topic
2. key_points: Important points (array)
3. insights: Key insights and takeaways
4. sources_used: List of sources analyzed (if any)

Return as JSON format."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a research assistant. Analyze topics and provide structured, factual insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            result["topic"] = topic
            result["depth"] = depth

            return result

        except Exception as e:
            print(f"Research error: {e}")
            return {
                "topic": topic,
                "summary": "Research failed",
                "key_points": [],
                "insights": f"Error: {str(e)}",
                "sources_used": sources or []
            }

    def research_competitor(
        self,
        company_name: str,
        competitor_name: str
    ) -> Dict[str, any]:
        """
        Compare two companies (competitor analysis)

        Args:
            company_name: Main company
            competitor_name: Competitor to compare

        Returns:
            Dictionary with comparison insights
        """

        # Research both companies
        company_info = self.research_company(company_name)
        competitor_info = self.research_company(competitor_name)

        # Use AI to compare
        prompt = f"""Compare these two companies:

Company 1: {company_name}
{json.dumps(company_info, indent=2)}

Company 2: {competitor_name}
{json.dumps(competitor_info, indent=2)}

Provide a competitive analysis including:
1. similarities: What they have in common
2. differences: Key differences
3. competitive_advantages: Each company's strengths
4. market_positioning: How they position themselves
5. recommendations: Strategic insights

Return as JSON format."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business analyst. Provide insightful competitive analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            result["company_name"] = company_name
            result["competitor_name"] = competitor_name

            return result

        except Exception as e:
            print(f"Comparison error: {e}")
            return {
                "company_name": company_name,
                "competitor_name": competitor_name,
                "error": str(e)
            }


def main():
    """Test research service"""
    import os

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    research = ResearchService(api_key=api_key)

    print("Testing company research...")
    result = research.research_company("Anthropic", context="for job application")

    print("\nResearch Results:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
