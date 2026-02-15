# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Agent Overview

**email-agent** is a standalone Gmail API email sending service with OAuth 2.0 authentication and automatic token management.

## Core Architecture

### Main Service: `email_agent/email_service.py`

The `EmailService` class handles Gmail API operations:

```python
class EmailService:
    def __init__(credentials_path, token_path, sender_email, sender_name)
    def send(to, subject, body) -> bool
    def authenticate() -> Credentials
```

### OAuth Flow

1. **First run**: Opens browser for OAuth consent → saves `token.json`
2. **Subsequent runs**: Uses saved token → auto-refreshes if expired
3. **Scopes**: Uses `gmail.send` only (send-only, secure)

## Development Workflow

### Virtual Environment - REQUIRED
Always activate the shared venv from repository root:
```bash
cd /Users/yash/Documents/agents
source venv/bin/activate
```

### Testing
```bash
# From agent directory
cd email-agent
python tests/test_email.py
```

### Installing/Reinstalling
```bash
# From repository root with venv activated
cd /Users/yash/Documents/agents
source venv/bin/activate
pip install -e email-agent
```

## Gmail Setup Requirements

### 1. Google Cloud Console Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json`
5. Place in repository root: `/Users/yash/Documents/agents/credentials.json`

### 2. OAuth Consent Screen
- Set to "External" (not Internal)
- Add your Gmail address as test user
- This allows sending from your Gmail account

### 3. File Locations
- `credentials.json` - OAuth client credentials (root directory)
- `token.json` - Saved OAuth tokens (root directory, auto-generated)

## Dependencies

- `google-api-python-client` - Gmail API client
- `google-auth` - OAuth authentication
- `google-auth-oauthlib` - OAuth flow handling
- `google-auth-httplib2` - HTTP support

## Key Methods

### `authenticate()` - OAuth handling
- Checks for existing valid token
- Refreshes expired tokens automatically
- Opens browser for new authentication if needed
- Saves token to disk for future use

### `send()` - Email sending
1. Authenticates with Gmail API
2. Creates MIME message with sender info
3. Base64 encodes message
4. Sends via Gmail API
5. Returns True on success, False on failure

## Email Message Format

Messages include proper headers:
- `From`: Sender name and email
- `To`: Recipient email
- `Subject`: Email subject
- Body: Plain text email body

## Error Handling

- Catches OAuth errors → prints helpful error message
- Catches API errors → returns False with error logging
- Token refresh failures → triggers re-authentication

## Integration Points

This agent is used by:
- **job-outreach-agent** - Sends job outreach emails
- Can be imported by any Python service needing email functionality

## Important Notes

- **Send-only permissions** - Cannot read emails (secure)
- **Rate limits** - Gmail API has daily sending limits (check quotas)
- **Token storage** - token.json contains OAuth credentials (keep secure)
- **First-time setup** - Requires manual browser authentication once
- Works only with Gmail accounts (not generic SMTP)
