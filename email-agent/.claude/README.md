# Email Agent - Context for Claude Code

## Project Overview

**Email Agent** is a standalone, reusable email sending service built on Gmail API. It's designed to be used by any Python project that needs email functionality.

## Core Purpose

Provide a simple, secure way to send emails via Gmail API with OAuth 2.0 authentication. No passwords, no SMTP configuration - just OAuth and send.

## Architecture

### Single Service
- `email_agent/email_service.py`: Core EmailService class
- No dependencies on other agents
- Fully self-contained

### Design Principles

1. **Generic**: Works for any use case (job outreach, marketing, notifications)
2. **Simple**: One class, clear API
3. **Secure**: OAuth 2.0, send-only permissions
4. **Configurable**: Credentials path, sender details customizable
5. **Reusable**: Can be installed in any project

## Key Components

### EmailService Class

```python
class EmailService:
    def __init__(
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None
    )

    def send(to, subject, body, from_email=None, from_name=None) -> bool
    def authenticate() -> bool
    def test_connection() -> bool
```

### Gmail API Integration

- Uses `google-api-python-client` for Gmail API
- OAuth 2.0 flow with `google-auth-oauthlib`
- Token caching and auto-refresh
- Send-only scope: `https://www.googleapis.com/auth/gmail.send`

## Usage Patterns

### Pattern 1: Job Outreach (Original Use Case)

```python
from email_agent import EmailService

email = EmailService(credentials_path="credentials.json")
email.send(
    to="recruiter@company.com",
    subject="Application for Senior Engineer",
    body=personalized_email_body
)
```

### Pattern 2: Marketing Emails

```python
email = EmailService(
    sender_name="Marketing Team",
    sender_email="marketing@company.com"
)

for customer in customers:
    email.send(
        to=customer.email,
        subject="Product Update",
        body=newsletter_content
    )
```

### Pattern 3: System Notifications

```python
email = EmailService()
email.send(
    to="admin@company.com",
    subject="Alert: Server Down",
    body=f"Server {server_name} is not responding"
)
```

## Installation

### In Other Projects

```bash
# Local development
pip install -e /path/to/agents/email-agent

# Or in requirements.txt
-e ../agents/email-agent
```

### In Job Outreach Agent

```python
# job-outreach-agent/requirements.txt
-e ../agents/email-agent
```

## Configuration

### Gmail API Setup

1. Google Cloud Console → Create project
2. Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials.json
5. Set OAuth consent screen to "External"
6. Add test users

### First Run

On first use:
1. Service opens browser for OAuth
2. User grants permissions
3. Token saved to `token.json`
4. Future calls use cached token

### Token Management

- Token automatically refreshed when expired
- Invalid tokens deleted and re-authenticated
- No manual intervention needed

## Error Handling

- Missing credentials file → Clear error with setup instructions
- Authentication failure → Helpful error message
- Token refresh failure → Auto-delete and re-authenticate
- Gmail API errors → Caught and logged

## Testing

```bash
# Test authentication and connection
python -m email_agent.email_service

# Run tests
python tests/test_email.py
```

## Extension Points

### Future Features to Add

1. **HTML Emails**: Support HTML content
2. **Attachments**: Add file attachment support
3. **CC/BCC**: Support CC and BCC recipients
4. **Templates**: Built-in email templates
5. **Batch Sending**: Efficient bulk email sending
6. **Rate Limiting**: Respect Gmail API quotas
7. **Email Tracking**: Track opens, clicks (if needed)
8. **Multiple Providers**: Support for SendGrid, AWS SES, etc.

### How to Extend

When adding features:
1. Keep the API simple and clean
2. Add methods to EmailService class
3. Maintain backward compatibility
4. Update tests
5. Document new features

## Guidelines for Claude Code

### When Working on Email Agent

1. **Keep it generic**: Don't add job-specific logic
2. **Simple API**: One send() method for most use cases
3. **Error messages**: Clear, actionable errors
4. **Documentation**: Update README for new features
5. **Testing**: Test with actual Gmail API

### Common Tasks

**Add HTML support:**
```python
def send_html(self, to, subject, html_body, text_body=None):
    # Create HTML message
    # Add text alternative
    # Send via Gmail API
```

**Add attachments:**
```python
def send_with_attachment(self, to, subject, body, attachment_path):
    # Read file
    # Encode as base64
    # Attach to MIME message
    # Send
```

**Add CC/BCC:**
```python
def send(self, to, subject, body, cc=None, bcc=None):
    # Add CC/BCC headers
    # Send
```

### DON'Ts

- ❌ Don't add job-specific logic (that belongs in job-outreach-agent)
- ❌ Don't add content generation (that belongs in content-agent)
- ❌ Don't add company research (that belongs in research-agent)
- ❌ Don't make breaking changes to existing API
- ❌ Don't add unnecessary dependencies

### DOs

- ✅ Keep focused on email sending
- ✅ Make it configurable
- ✅ Add helpful error messages
- ✅ Support common email patterns
- ✅ Document everything clearly

## Integration with Other Agents

### Used By:

1. **job-outreach-agent**: Send application emails to recruiters
2. **market-research-tool** (future): Send research reports
3. **sales-automation** (future): Send sales outreach emails
4. **notification-service** (future): Send system notifications

### Dependencies:

None - Email agent is fully self-contained.

## File Structure

```
email-agent/
├── .claude/
│   └── README.md          # This file (Claude context)
├── email_agent/
│   ├── __init__.py        # Package init
│   └── email_service.py   # Core service
├── tests/
│   └── test_email.py      # Tests
├── README.md              # User documentation
├── requirements.txt       # Dependencies
└── setup.py               # Package setup
```

## Development Workflow

1. **Make changes** to email_service.py
2. **Test locally**: `python -m email_agent.email_service`
3. **Run tests**: `python tests/test_email.py`
4. **Update documentation**: README.md and this file
5. **Test integration**: Use in job-outreach-agent
6. **Commit changes**: Git commit with clear message

## Version History

- **1.0.0**: Initial release with Gmail API support

---

**This agent is production-ready and can be used in any Python project.**
