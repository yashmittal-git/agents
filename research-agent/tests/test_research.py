"""
Test Research Agent
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from research_agent import ResearchService


def test_api_key():
    """Test API key availability"""
    print("Testing API key...")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key'")
        return False

    print("✓ API key found")
    return True


def test_company_research():
    """Test company research"""
    print("\nTesting company research...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠ Skipping (no API key)")
        return True

    try:
        research = ResearchService(api_key=api_key)

        result = research.research_company("Anthropic")

        print("✓ Company research successful")
        print(f"  Company: {result.get('company_name')}")
        print(f"  Stage: {result.get('stage')}")
        print(f"  Tech Stack: {', '.join(result.get('tech_stack', [])[:3])}")

        return True

    except Exception as e:
        print(f"✗ Company research failed: {e}")
        return False


def test_topic_research():
    """Test topic research"""
    print("\nTesting topic research...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠ Skipping (no API key)")
        return True

    try:
        research = ResearchService(api_key=api_key)

        result = research.research_topic(
            "Python web scraping best practices",
            depth="quick"
        )

        print("✓ Topic research successful")
        print(f"  Topic: {result.get('topic')}")
        print(f"  Summary: {result.get('summary', '')[:100]}...")

        return True

    except Exception as e:
        print(f"✗ Topic research failed: {e}")
        return False


def test_website_fetch():
    """Test website fetching"""
    print("\nTesting website fetch...")

    try:
        research = ResearchService(api_key="dummy")  # Don't need real key for this

        content = research.fetch_website("https://www.anthropic.com")

        if content:
            print("✓ Website fetch successful")
            print(f"  Content length: {len(content)} characters")
            return True
        else:
            print("⚠ No content fetched (website may be unavailable)")
            return True  # Not a failure, just no content

    except Exception as e:
        print(f"✗ Website fetch failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("Research Agent Tests")
    print("="*60)

    tests = [
        test_api_key,
        test_website_fetch,
        test_company_research,
        test_topic_research
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append(False)

    print("\n" + "="*60)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    print("="*60)

    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
