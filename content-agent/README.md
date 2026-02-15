# Content Agent

Standalone AI-powered content generation service. Generate emails, LinkedIn messages, cover letters, social media posts, and more.

## Features

- Email generation with personalization
- LinkedIn messages (connection requests, outreach)
- Cover letters
- Social media posts (Twitter, LinkedIn, Facebook, Instagram)
- Generic content generation for any purpose
- AI-powered using GPT-4o
- Flexible styling and constraints
- Structured JSON output
- Reusable across multiple projects

## Installation

### Option 1: Local Development

```bash
pip install -e /path/to/agents/content-agent
```

### Option 2: From Requirements

```
# requirements.txt
-e ../agents/content-agent
```

## Setup

### OpenAI API Key

Get your API key from [OpenAI](https://platform.openai.com/api-keys)

```bash
export OPENAI_API_KEY="your-api-key"
```

## Usage

### Email Generation

```python
from content_agent import ContentService

content = ContentService(api_key="your-key")

email = content.generate_email(
    to_info={
        "name": "Jane Recruiter",
        "company": "Anthropic",
        "role": "Technical Recruiter"
    },
    context={
        "purpose": "job application",
        "role": "Software Engineer",
        "highlights": "AI systems experience, Python expert"
    },
    sender_info={
        "name": "John Doe",
        "email": "john@example.com",
        "linkedin": "linkedin.com/in/johndoe",
        "phone": "+1234567890"
    },
    max_words=250
)

print(f"Subject: {email['subject']}")
print(email['body'])
```

### LinkedIn Message

```python
message = content.generate_linkedin_message(
    to_info={
        "name": "Jane",
        "role": "Engineering Manager at Anthropic",
        "background": "AI Safety researcher"
    },
    context={
        "reason": "interested in AI safety role",
        "connection": "saw your talk at AI Conference"
    },
    max_chars=300  # LinkedIn connection request limit
)

print(message)
```

### Cover Letter

```python
cover_letter = content.generate_cover_letter(
    job_info={
        "company": "Anthropic",
        "role": "Senior Software Engineer",
        "requirements": "Python, AI/ML, distributed systems"
    },
    candidate_info={
        "name": "John Doe",
        "experience": "8 years in AI systems",
        "highlights": ["Built AI Voicebot", "Scaled to 300K+ calls/day"]
    },
    company_research={
        "mission": "AI safety",
        "products": "Claude AI"
    },
    max_words=400
)

print(cover_letter)
```

### Social Media Posts

```python
# LinkedIn post
post = content.generate_social_post(
    platform="linkedin",
    topic="Lessons from building an AI Voicebot",
    style="professional"
)

# Twitter thread
tweet = content.generate_social_post(
    platform="twitter",
    topic="5 tips for scaling AI systems",
    style="engaging"
)
```

### Generic Content

```python
content_text = content.generate_content(
    content_type="blog_post_intro",
    context={
        "topic": "Future of AI in Healthcare",
        "target_audience": "healthcare professionals",
        "key_points": ["diagnostics", "patient care", "efficiency"]
    },
    constraints={
        "max_words": 300,
        "tone": "informative"
    }
)
```

## API Reference

### ContentService

```python
ContentService(
    api_key: str,
    model: str = "gpt-4o"
)
```

### Methods

#### `generate_email(to_info, context, sender_info=None, max_words=250, include_signature=True) -> Dict`

Generate personalized email.

**Returns:**
```python
{
    "subject": "Email subject line",
    "body": "Email body with signature"
}
```

#### `generate_linkedin_message(to_info, context, sender_info=None, max_chars=300) -> str`

Generate LinkedIn message (connection request or DM).

#### `generate_cover_letter(job_info, candidate_info, company_research=None, max_words=400) -> str`

Generate cover letter for job application.

#### `generate_social_post(platform, topic, context=None, style="professional") -> str`

Generate social media post for any platform.

#### `generate_content(content_type, context, constraints=None, style=None) -> str`

Generate any type of content.

## Use Cases

### Job Application

```python
# Complete job application content
content = ContentService(api_key=api_key)

# Email outreach
email = content.generate_email(...)

# LinkedIn connection
linkedin_msg = content.generate_linkedin_message(...)

# Cover letter
cover_letter = content.generate_cover_letter(...)
```

### Marketing

```python
# Email campaign
for lead in leads:
    email = content.generate_email(
        to_info=lead,
        context={"purpose": "product demo"},
        max_words=150
    )
    send_email(email)

# Social media content
linkedin_post = content.generate_social_post(
    "linkedin",
    "Product launch announcement"
)
```

### Sales Outreach

```python
# Personalized sales email
email = content.generate_email(
    to_info=prospect,
    context={
        "purpose": "sales outreach",
        "product": "AI Analytics Platform",
        "value_prop": "Reduce costs by 45%"
    },
    max_words=200
)
```

### Content Creation

```python
# Blog content
intro = content.generate_content(
    "blog_intro",
    context={"topic": "AI trends", "audience": "developers"}
)

# Newsletter
newsletter = content.generate_content(
    "newsletter",
    context={"updates": [...], "cta": "..."}
)
```

## Testing

```bash
OPENAI_API_KEY=your-key python -m content_agent.content_service
python tests/test_content.py
```

## Requirements

- Python 3.9+
- OpenAI API key

## License

MIT License

## Author

Yash Mittal

## Version

1.0.0
