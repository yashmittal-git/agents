"""
Test Email Agent
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from email_agent import EmailService


def test_authentication():
    """Test Gmail authentication"""
    print("Testing Gmail authentication...")

    if not os.path.exists("credentials.json"):
        print("⚠ credentials.json not found")
        print("Please set up Gmail API credentials first")
        print("See README.md for setup instructions")
        return False

    email = EmailService(
        credentials_path="credentials.json",
        token_path="token.json"
    )

    if email.authenticate():
        print("✓ Authentication successful")
        return True
    else:
        print("✗ Authentication failed")
        return False


def test_connection():
    """Test Gmail API connection"""
    print("\nTesting Gmail connection...")

    email = EmailService()

    if email.test_connection():
        print("✓ Connection successful")
        return True
    else:
        print("✗ Connection failed")
        return False


def test_send_email():
    """Test sending email (interactive)"""
    print("\nTest sending email")
    print("="*60)

    response = input("Do you want to send a test email? (y/n): ")

    if response.lower() != 'y':
        print("Skipping email send test")
        return True

    recipient = input("Enter recipient email: ")

    if not recipient:
        print("No recipient provided, skipping")
        return True

    email = EmailService()

    success = email.send(
        to=recipient,
        subject="Test Email from Email Agent",
        body="This is a test email sent from the Email Agent service.\n\n"
             "If you received this, the email agent is working correctly!"
    )

    if success:
        print("✓ Email sent successfully")
        return True
    else:
        print("✗ Failed to send email")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("Email Agent Tests")
    print("="*60)

    tests = [
        test_authentication,
        test_connection
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append(False)

    # Optional interactive test
    try:
        test_send_email()
    except Exception as e:
        print(f"Email send test error: {e}")

    print("\n" + "="*60)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    print("="*60)

    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
