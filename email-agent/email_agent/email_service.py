"""
Email Service
Generic email sending service using Gmail API
Can be used by any application
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Union, List
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class EmailService:
    """
    Generic email sending service using Gmail API

    Usage:
        email = EmailService(
            credentials_path="credentials.json",
            token_path="token.json"
        )
        email.send(
            to="recipient@example.com",
            subject="Hello",
            body="This is a test email"
        )
    """

    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None
    ):
        """
        Initialize email service

        Args:
            credentials_path: Path to Gmail OAuth credentials JSON
            token_path: Path to store/load token
            sender_email: Default sender email (optional)
            sender_name: Default sender name (optional)
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.service = None
        self.authenticated = False

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API

        Returns:
            bool: True if authentication successful
        """
        creds = None

        # Check if token file exists
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(
                self.token_path,
                self.GMAIL_SCOPES
            )

        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    # Delete invalid token and re-authenticate
                    if os.path.exists(self.token_path):
                        os.remove(self.token_path)
                    return self.authenticate()
            else:
                if not os.path.exists(self.credentials_path):
                    print("\n" + "="*60)
                    print("Gmail API Setup Required")
                    print("="*60)
                    print("\nTo use Gmail API, you need to:")
                    print("1. Go to: https://console.cloud.google.com/")
                    print("2. Create a new project or select existing one")
                    print("3. Enable Gmail API")
                    print("4. Create OAuth 2.0 credentials (Desktop app)")
                    print("5. Download the credentials JSON file")
                    print(f"6. Save it as: {self.credentials_path}")
                    print("\nDetailed guide: https://developers.google.com/gmail/api/quickstart/python")
                    print("="*60 + "\n")
                    return False

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path,
                        self.GMAIL_SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Authentication failed: {e}")
                    return False

            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.authenticated = True
            print("✓ Gmail authentication successful")
            return True
        except Exception as e:
            print(f"Failed to build Gmail service: {e}")
            return False

    def create_message(
        self,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> dict:
        """
        Create email message

        Args:
            to: Recipient email(s) - can be a string or list of strings
            subject: Email subject
            body: Email body
            from_email: Sender email (defaults to sender_email from init)
            from_name: Sender name (defaults to sender_name from init)

        Returns:
            Email message dict ready to send
        """
        message = MIMEMultipart()

        # Handle multiple recipients
        if isinstance(to, list):
            message['To'] = ', '.join(to)
        else:
            message['To'] = to

        # Set From header
        sender = from_email or self.sender_email or "me"
        if from_name or self.sender_name:
            name = from_name or self.sender_name
            message['From'] = f"{name} <{sender}>"
        else:
            message['From'] = sender

        message['Subject'] = subject

        # Add body
        msg_body = MIMEText(body, 'plain')
        message.attach(msg_body)

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def send(
        self,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """
        Send email via Gmail API

        Args:
            to: Recipient email(s) - can be a string or list of strings
            subject: Email subject
            body: Email body
            from_email: Sender email (optional)
            from_name: Sender name (optional)

        Returns:
            bool: True if email sent successfully
        """
        if not self.authenticated:
            if not self.authenticate():
                print("Cannot send email: Authentication failed")
                return False

        try:
            message = self.create_message(to, subject, body, from_email, from_name)
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            print(f"✓ Email sent successfully to {to} (Message ID: {sent_message['id']})")
            return True

        except HttpError as error:
            print(f"Gmail API error: {error}")
            return False
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def test_connection(self) -> bool:
        """Test Gmail API connection"""
        if not self.authenticated:
            return self.authenticate()

        try:
            if self.service:
                print(f"✓ Connected to Gmail (send-only access)")
                return True
            return False
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


def main():
    """Test email service"""
    import sys

    # Check for credentials
    if not os.path.exists("credentials.json"):
        print("Error: credentials.json not found")
        print("Please set up Gmail API credentials first")
        sys.exit(1)

    email = EmailService()

    print("Testing Gmail authentication...")
    if email.authenticate():
        print("\nTesting connection...")
        email.test_connection()
        print("\nEmail service is ready!")
    else:
        print("\nAuthentication failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
