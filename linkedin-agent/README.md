# LinkedIn Agent

LinkedIn messaging service for sending connection requests and messages.

**Status: PLACEHOLDER - Future Implementation**

## Note

LinkedIn does not provide a public API for sending messages. Implementation options:

1. **LinkedIn API** (requires enterprise partnership)
2. **Browser Automation** (Selenium/Playwright) - technically works but against LinkedIn ToS
3. **Manual with Guidance** (current approach) - agent provides step-by-step instructions

## Current Functionality

Currently, this agent provides **manual guidance** for LinkedIn actions:

```python
from linkedin_agent import LinkedInService

linkedin = LinkedInService()

# Provides step-by-step instructions
result = linkedin.send_connection_request(
    profile_url="https://linkedin.com/in/jane",
    message="Hi Jane, I'd love to connect..."
)

# Prints:
# 1. Open LinkedIn
# 2. Go to profile
# 3. Click Connect
# 4. Add note
# 5. Send
```

## Future Implementation

When/if LinkedIn API becomes available or browser automation is approved:

```python
# Automated sending (future)
linkedin = LinkedInService(credentials={...})
linkedin.authenticate()

success = linkedin.send_connection_request(
    profile_url="...",
    message="..."
)
# True (actually sent)
```

## Use Cases

- Job outreach via LinkedIn
- Professional networking
- Sales/business development
- Recruiter outreach

## Installation

```bash
pip install -e /path/to/agents/linkedin-agent
```

## Requirements

- Python 3.9+
- Future: Selenium or Playwright (for automation)
- Future: LinkedIn API credentials (if available)

## Version

1.0.0 (Placeholder)
