"""
Test Content Agent
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from content_agent import ContentService


def test_api_key():
    """Test API key availability"""
    print("Testing API key...")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠ OPENAI_API_KEY environment variable not set")
        return False

    print("✓ API key found")
    return True


def test_email_generation():
    """Test email generation"""
    print("\nTesting email generation...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠ Skipping (no API key)")
        return True

    try:
        content = ContentService(api_key=api_key)

        email = content.generate_email(
            to_info={"name": "Jane", "company": "TestCorp"},
            context={"purpose": "test", "role": "Engineer"},
            sender_info={"name": "John", "email": "john@test.com"},
            max_words=100
        )

        print("✓ Email generation successful")
        print(f"  Subject: {email.get('subject', '')[:50]}...")
        return True

    except Exception as e:
        print(f"✗ Email generation failed: {e}")
        return False


def test_linkedin_message():
    """Test LinkedIn message generation"""
    print("\nTesting LinkedIn message...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠ Skipping (no API key)")
        return True

    try:
        content = ContentService(api_key=api_key)

        message = content.generate_linkedin_message(
            to_info={"name": "Jane", "role": "Engineer"},
            context={"reason": "networking"},
            max_chars=200
        )

        print("✓ LinkedIn message generation successful")
        print(f"  Message length: {len(message)} chars")
        return True

    except Exception as e:
        print(f"✗ LinkedIn message failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("Content Agent Tests")
    print("="*60)

    tests = [
        test_api_key,
        test_email_generation,
        test_linkedin_message
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
