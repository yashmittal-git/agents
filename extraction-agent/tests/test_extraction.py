#!/usr/bin/env python3
"""
Test Extraction Agent

Tests the extraction service with different content types
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extraction_agent import ExtractionService


def test_initialization():
    """Test service initialization"""
    print("Testing Extraction Agent initialization...")

    # Load API key from environment
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return False

    try:
        extractor = ExtractionService(api_key=api_key)
        print(f"✓ ExtractionService initialized")
        print(f"  API Key: {api_key[:10]}...")
        print(f"  Model: {extractor.model}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False


def test_text_extraction():
    """Test text extraction"""
    print("\nTesting text extraction...")

    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return False

    extractor = ExtractionService(api_key=api_key)

    # Test text extraction
    text = """
    Anthropic is hiring a Senior Software Engineer.
    Contact: careers@anthropic.com
    Requirements: Python, AI/ML, 5+ years experience
    """

    schema = {
        "company_name": "Company name",
        "role": "Job role/title",
        "email": "Contact email",
        "requirements": "Job requirements"
    }

    try:
        result = extractor.extract_from_text(
            text=text,
            schema=schema,
            instructions="Extract job information"
        )
        print(f"✓ Text extraction successful")
        print(f"  Extracted: {result}")
        return True
    except Exception as e:
        print(f"❌ Text extraction failed: {e}")
        return False


def test_schema_building():
    """Test schema description building"""
    print("\nTesting schema building...")

    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")

    api_key = os.getenv("OPENAI_API_KEY")
    extractor = ExtractionService(api_key=api_key)

    schema = {
        "company": "Company name",
        "role": "Job title",
        "email": "Contact email (or null)"
    }

    description = extractor._build_schema_description(schema)
    expected_lines = 3

    if description.count('\n') == expected_lines - 1:
        print(f"✓ Schema description built correctly")
        print(f"  Output:\n{description}")
        return True
    else:
        print(f"❌ Schema description incorrect")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Extraction Agent Tests")
    print("="*60)

    results = []

    # Run tests
    results.append(("Initialization", test_initialization()))
    results.append(("Schema Building", test_schema_building()))
    results.append(("Text Extraction", test_text_extraction()))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)
