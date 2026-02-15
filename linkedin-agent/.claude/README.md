# LinkedIn Agent - Context for Claude Code

## Project Overview

**LinkedIn Agent** is a placeholder for future LinkedIn messaging functionality.

## Current Status

**PLACEHOLDER - Not Implemented**

Currently provides manual guidance instead of automated sending.

## Why Not Implemented?

LinkedIn does not provide public API for:
- Sending connection requests
- Sending direct messages
- Automated profile interactions

Options:
1. **LinkedIn API**: Requires enterprise partnership (not publicly available)
2. **Browser Automation**: Against LinkedIn Terms of Service
3. **Manual with Guidance**: Current approach (safe, compliant)

## Current Implementation

Provides step-by-step instructions for manual LinkedIn actions:

```python
linkedin = LinkedInService()
linkedin.send_connection_request(url, message)
# Prints instructions for user to follow
```

## Future Implementation

When LinkedIn API becomes available or automation is approved:

### Option 1: Official API
```python
# Use LinkedIn API SDK
linkedin = LinkedInService(api_key="...")
linkedin.send_connection_request(...)
```

### Option 2: Browser Automation
```python
# Use Selenium/Playwright (check ToS first)
linkedin = LinkedInService(automation="selenium")
linkedin.authenticate(email, password)
linkedin.send_connection_request(...)
```

## Guidelines for Claude Code

### When Implementing LinkedIn Agent

1. **Check LinkedIn ToS** before implementing automation
2. **Prefer official API** if/when available
3. **Rate limiting** to avoid account restrictions
4. **Error handling** for failed connections
5. **Secure credentials** (never hardcode)

### DON'Ts
- ❌ Don't implement without checking ToS
- ❌ Don't spam or abuse LinkedIn
- ❌ Don't store credentials insecurely

### DOs
- ✅ Wait for official API
- ✅ Provide manual guidance (current approach)
- ✅ Document limitations clearly

## Integration

Used by: job-outreach-agent (with manual guidance)
Dependencies: None (currently)

## Version

1.0.0 (Placeholder)
