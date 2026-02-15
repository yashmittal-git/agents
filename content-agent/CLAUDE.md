# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Agent Overview

**content-agent** is a standalone AI-powered content generation service that creates personalized emails, LinkedIn messages, cover letters, and social media posts using GPT-4o.

## Core Architecture

### Main Service: `content_agent/content_service.py`

The `ContentService` class provides content generation capabilities:

```python
class ContentService:
    def __init__(api_key, model="gpt-4o")
    def generate_email(to_info, context, sender_info, max_words) -> Dict
    def generate_linkedin_message(to_info, context, sender_info, max_words) -> Dict
    def generate_cover_letter(to_info, context, sender_info, max_words) -> Dict
    def generate_social_post(platform, topic, context, max_words) -> Dict
    def generate_content(content_type, prompt, max_words) -> str
```

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
cd content-agent
python tests/test_content.py
```

### Installing/Reinstalling
```bash
# From repository root with venv activated
cd /Users/yash/Documents/agents
source venv/bin/activate
pip install -e content-agent
```

## Dependencies

- `openai>=1.0.0` - For GPT-4o content generation

Model used: `gpt-4o`

## Key Methods

### `generate_email()` - Email generation
Returns structured email with subject and body:
```python
{
    "subject": "Application for Software Engineer at Anthropic",
    "body": "Dear Jane,\n\n[Personalized content]...\n\nBest,\nJohn"
}
```

**Parameters:**
- `to_info`: Recipient details (name, company, role)
- `context`: Email context (purpose, role, highlights, optional `user_custom_context` for specific user instructions)
- `sender_info`: Sender details (name, email, linkedin, phone, highlights, skills)
- `max_words`: Word limit (default 250)

**Style Guidelines:**
- Professional but warm tone
- Personalized based on company research
- Highlights relevant experience/skills
- Clear call-to-action
- Includes contact info in signature

### `generate_linkedin_message()` - LinkedIn message
Returns LinkedIn connection message (280 char limit):
```python
{
    "message": "Hi Jane! Saw your work at Anthropic on AI safety..."
}
```

**Parameters:** Same as `generate_email()`

**Style Guidelines:**
- Very concise (LinkedIn char limit)
- Casual but professional
- Personal connection/shared interest
- Clear reason for reaching out

### `generate_cover_letter()` - Cover letter
Returns formal cover letter:
```python
{
    "cover_letter": "[Full formatted cover letter]"
}
```

**Parameters:** Same as `generate_email()`

**Style Guidelines:**
- Formal business letter format
- Detailed experience showcase
- Company-specific customization
- Strong opening and closing

### `generate_social_post()` - Social media post
Returns platform-optimized post:
```python
{
    "post": "[Social media content]"
}
```

**Parameters:**
- `platform`: "twitter", "linkedin", "facebook", "instagram"
- `topic`: Post topic/theme
- `context`: Additional context
- `max_words`: Word limit

**Platform-Specific Styles:**
- Twitter: Concise, hashtags, engaging
- LinkedIn: Professional, thought leadership
- Facebook: Conversational, community-focused
- Instagram: Visual-first, emoji-friendly

### `generate_content()` - Generic content
Flexible content generation for any purpose.

## Content Quality Features

### Personalization
- Uses recipient and sender details for context
- References company research and specifics
- Incorporates user's custom instructions when provided (via `context.user_custom_context`)
- Tailors tone and style to purpose

### Length Control
- Respects `max_words` parameter
- Automatically adjusts for platform constraints
- Balances brevity with completeness

### Tone Adaptation
- Professional for business emails
- Casual for LinkedIn connection requests
- Formal for cover letters
- Platform-appropriate for social posts

## Integration Points

This agent is used by:
- **job-outreach-agent** - Generates personalized job outreach content
- Can be imported by any service needing AI content generation

## Important Notes

- **Stateless** - No memory between calls
- **API cost** - Each generation uses OpenAI tokens
- **Quality variance** - AI output may vary slightly between calls
- **No editing** - Generates fresh content each time (no iterative refinement)
- **Context is key** - Better input context = better output quality
- **Length is approximate** - Word count is guidance, not strict limit
