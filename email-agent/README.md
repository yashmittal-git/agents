# Email Agent

Standalone email sending service using Gmail API. Can be used by any Python application for sending emails.

## Features

- Gmail API integration with OAuth 2.0
- Simple, clean interface
- Automatic token management and refresh
- Send-only permissions (secure)
- Configurable sender details
- Reusable across multiple projects

## Installation

### Option 1: Local Development

```bash
pip install -e /path/to/agents/email-agent
```

### Option 2: From Requirements

```
# requirements.txt
-e ../agents/email-agent
```

## Setup

### 1. Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Change OAuth consent screen from "Internal" to "External"
6. Add your email as test user
7. Download the credentials JSON file
8. Save it as `credentials.json` in your project root

### 2. First-time Authentication

On first use, the service will open a browser for OAuth authentication. After successful authentication, a token file will be saved for future use.

## Usage

### Basic Usage

```python
from email_agent import EmailService

# Initialize
email = EmailService(
    credentials_path="credentials.json",
    token_path="token.json",
    sender_email="your.email@gmail.com",
    sender_name="Your Name"
)

# Send email
email.send(
    to="recipient@example.com",
    subject="Hello from Email Agent",
    body="This is a test email sent via Email Agent!"
)
```

### In Job Outreach Agent

```python
from email_agent import EmailService

email = EmailService(
    credentials_path="credentials.json",
    token_path="token.json"
)

success = email.send(
    to=recruiter_email,
    subject=email_subject,
    body=email_body
)
```

### In Any Other Project

```python
from email_agent import EmailService

# Marketing emails
email = EmailService()
email.send(
    to="customer@company.com",
    subject="Product Update",
    body="Check out our new features..."
)

# Notification emails
email.send(
    to="admin@company.com",
    subject="System Alert",
    body="Server usage at 90%"
)

# Newsletter
for subscriber in subscribers:
    email.send(
        to=subscriber.email,
        subject="Weekly Newsletter",
        body=newsletter_content
    )
```

## API Reference

### EmailService

```python
EmailService(
    credentials_path: str = "credentials.json",
    token_path: str = "token.json",
    sender_email: Optional[str] = None,
    sender_name: Optional[str] = None
)
```

**Parameters:**
- `credentials_path`: Path to Gmail OAuth credentials JSON
- `token_path`: Path to store/load authentication token
- `sender_email`: Default sender email (optional)
- `sender_name`: Default sender name (optional)

### Methods

#### `send(to, subject, body, from_email=None, from_name=None) -> bool`

Send an email via Gmail API.

**Parameters:**
- `to`: Recipient email address
- `subject`: Email subject
- `body`: Email body (plain text)
- `from_email`: Override sender email (optional)
- `from_name`: Override sender name (optional)

**Returns:** `True` if email sent successfully, `False` otherwise

#### `authenticate() -> bool`

Authenticate with Gmail API. Called automatically by `send()` if not already authenticated.

**Returns:** `True` if authentication successful

#### `test_connection() -> bool`

Test Gmail API connection.

**Returns:** `True` if connection successful

## Testing

```bash
# Test authentication
python -m email_agent.email_service

# Or use the test script
python tests/test_email.py
```

## Use Cases

- **Job Outreach**: Send personalized outreach emails to recruiters
- **Marketing**: Send newsletters, product updates, promotional emails
- **Notifications**: System alerts, user notifications, confirmations
- **Automation**: Automated reports, digests, reminders
- **Customer Support**: Automated responses, ticket notifications
- **Sales**: Lead follow-ups, proposals, meeting confirmations

## Security

- Uses OAuth 2.0 for authentication (no password storage)
- Send-only permissions (cannot read emails)
- Token is stored locally and refreshed automatically
- Credentials file should be kept secure (.gitignore)

## Requirements

- Python 3.9+
- Gmail account with API access
- Google Cloud project with Gmail API enabled

## License

MIT License

## Author

Yash Mittal

## Version

1.0.0
