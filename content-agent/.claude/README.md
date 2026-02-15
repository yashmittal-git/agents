# Content Agent - Context for Claude Code

## Project Overview

**Content Agent** is a standalone AI-powered content generation service. It generates emails, LinkedIn messages, cover letters, social posts, and any text content using GPT-4o.

## Core Purpose

Provide intelligent content generation for any Python project that needs to create personalized, high-quality text content.

## Key Components

### ContentService Class

Main service with these methods:
- `generate_email()`: Professional emails with personalization
- `generate_linkedin_message()`: LinkedIn connection requests/messages
- `generate_cover_letter()`: Job application cover letters
- `generate_social_post()`: Social media posts (Twitter, LinkedIn, etc.)
- `generate_content()`: Generic content for any purpose

### Design Principles

1. **Generic**: Works for any content need
2. **Configurable**: Control length, tone, style
3. **Structured**: Returns JSON or clean text
4. **Personalized**: Uses context for customization
5. **Reusable**: One agent, many projects

## Usage Patterns

### Job Application (Original Use Case)
```python
email = content.generate_email(
    to_info={"name": "Jane", "company": "Anthropic"},
    context={"purpose": "job application", "role": "Engineer"},
    sender_info=user_profile
)
```

### Marketing Campaign
```python
for lead in leads:
    email = content.generate_email(
        to_info=lead,
        context={"purpose": "product demo"}
    )
```

### Social Media
```python
post = content.generate_social_post("linkedin", "Product launch")
```

## Guidelines for Claude Code

### DON'Ts
- ❌ Don't add research logic (that's research-agent)
- ❌ Don't add email sending (that's email-agent)
- ❌ Don't add job-specific logic

### DOs
- ✅ Keep focused on content generation
- ✅ Support multiple content types
- ✅ Make it configurable
- ✅ Return structured output

## Integration

Used by: job-outreach-agent, marketing tools, sales automation
Dependencies: None (fully self-contained)

## File Structure
```
content-agent/
├── .claude/README.md
├── content_agent/
│   ├── __init__.py
│   └── content_service.py
├── tests/test_content.py
├── README.md
├── requirements.txt
└── setup.py
```
