# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Agent Overview

**linkedin-agent** is a **placeholder service** that provides manual guidance for LinkedIn actions. LinkedIn has no public messaging API, so this agent generates step-by-step instructions instead of automating actions.

## Core Architecture

### Main Service: `linkedin_agent/linkedin_service.py`

The `LinkedInService` class provides manual guidance:

```python
class LinkedInService:
    def send_connection_request(profile_url, message) -> Dict
    def send_message(profile_url, message) -> Dict
```

### Current Functionality

**Returns manual instructions, NOT automated actions:**
- Profile URL to visit
- Step-by-step manual instructions
- Message to copy/paste
- Success: Always `False` (manual action required)

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
cd linkedin-agent
python tests/test_linkedin.py
```

### Installing/Reinstalling
```bash
# From repository root with venv activated
cd /Users/yash/Documents/agents
source venv/bin/activate
pip install -e linkedin-agent
```

## Dependencies

**None** - This is a placeholder with no external dependencies.

## Key Methods

### `send_connection_request()` - Connection guidance
Returns manual instructions:
```python
{
    "success": False,
    "manual_action_required": True,
    "instructions": [
        "1. Open LinkedIn",
        "2. Go to: [profile_url]",
        "3. Click 'Connect' button",
        "4. Click 'Add a note'",
        "5. Copy this message: [message]",
        "6. Paste and click 'Send'"
    ],
    "profile_url": "https://linkedin.com/in/jane",
    "message": "[Your message]"
}
```

### `send_message()` - Message guidance
Similar to connection request, provides step-by-step manual instructions.

## Why Placeholder?

### LinkedIn API Limitations
1. **No public messaging API** - LinkedIn doesn't offer public API for sending messages
2. **Enterprise partnership required** - Only enterprise partners can access messaging
3. **Against ToS** - Browser automation (Selenium/Playwright) violates LinkedIn terms

### Current Approach
- Provides **manual guidance** instead of automation
- User manually performs actions following instructions
- Integrates seamlessly with job-outreach-agent orchestrator
- Future-proof: can be upgraded when API becomes available

## Future Implementation Options

### If LinkedIn API becomes available:
```python
# Potential future implementation
linkedin = LinkedInService(credentials={...})
linkedin.authenticate()
success = linkedin.send_connection_request(url, message)
# Returns: True (actually sent)
```

### If browser automation is approved:
- Selenium/Playwright integration
- Headless browser control
- Automated clicking and typing
- Risk: Account suspension if detected

## Integration Points

This agent is used by:
- **job-outreach-agent** - Provides LinkedIn outreach guidance
- Returns manual instructions when email is not available
- Orchestrator intelligently recommends LinkedIn when appropriate

## Important Notes

- **No actual automation** - Always requires manual action
- **Always returns success=False** - Indicates manual action needed
- **No credentials required** - No authentication needed
- **ToS compliant** - Doesn't violate LinkedIn terms
- **User-friendly** - Clear step-by-step instructions
- Future-ready architecture for when/if automation becomes possible
