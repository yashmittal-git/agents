# Research Agent

Standalone web research service using AI and web scraping. Can research companies, topics, competitors, markets, and more.

## Features

- Company research with web scraping
- General topic research
- Competitor analysis
- AI-powered insights using GPT-4o
- Automatic website discovery
- Structured JSON output
- Reusable across multiple projects

## Installation

### Option 1: Local Development

```bash
pip install -e /path/to/agents/research-agent
```

### Option 2: From Requirements

```
# requirements.txt
-e ../agents/research-agent
```

## Setup

### 1. OpenAI API Key

Get your API key from [OpenAI](https://platform.openai.com/api-keys)

### 2. Set API Key

```bash
export OPENAI_API_KEY="your-api-key"

# Or in your code
research = ResearchService(api_key="your-api-key")
```

## Usage

### Basic Company Research

```python
from research_agent import ResearchService

# Initialize
research = ResearchService(api_key="your-openai-key")

# Research a company
result = research.research_company("Anthropic")

print(result)
# {
#     "company_name": "Anthropic",
#     "what_they_build": "Anthropic builds AI safety-focused...",
#     "tech_stack": ["Python", "PyTorch", "Kubernetes", ...],
#     "stage": "growth",
#     "relevant_context": "...",
#     "website_url": "https://www.anthropic.com"
# }
```

### Company Research with Context

```python
# For job application
result = research.research_company(
    company_name="Anthropic",
    context="for job application as Software Engineer"
)

# For investment analysis
result = research.research_company(
    company_name="OpenAI",
    context="for investment analysis"
)

# With known website URL
result = research.research_company(
    company_name="Custom Company",
    website_url="https://example.com"
)
```

### Topic Research

```python
# Research a topic
result = research.research_topic(
    topic="AI safety trends 2024",
    depth="medium"  # quick, medium, or deep
)

print(result)
# {
#     "topic": "AI safety trends 2024",
#     "summary": "...",
#     "key_points": [...],
#     "insights": "...",
#     "depth": "medium"
# }
```

### Topic Research with Sources

```python
# Research with specific sources
result = research.research_topic(
    topic="React vs Vue comparison",
    sources=[
        "https://react.dev",
        "https://vuejs.org"
    ],
    depth="deep"
)
```

### Competitor Analysis

```python
# Compare two companies
result = research.research_competitor(
    company_name="Anthropic",
    competitor_name="OpenAI"
)

print(result)
# {
#     "company_name": "Anthropic",
#     "competitor_name": "OpenAI",
#     "similarities": "...",
#     "differences": "...",
#     "competitive_advantages": "...",
#     "market_positioning": "...",
#     "recommendations": "..."
# }
```

## API Reference

### ResearchService

```python
ResearchService(
    api_key: str,
    model: str = "gpt-4o"
)
```

**Parameters:**
- `api_key`: OpenAI API key (required)
- `model`: OpenAI model to use (default: "gpt-4o")

### Methods

#### `research_company(company_name, context="", website_url=None) -> Dict`

Research a company and return structured information.

**Parameters:**
- `company_name`: Name of the company
- `context`: Additional context (optional)
- `website_url`: Company website URL (optional, will auto-detect if not provided)

**Returns:**
```python
{
    "company_name": str,
    "what_they_build": str,
    "tech_stack": List[str],
    "stage": str,  # startup/growth/established/enterprise
    "relevant_context": str,
    "website_url": str
}
```

#### `research_topic(topic, depth="medium", sources=None) -> Dict`

Research a general topic.

**Parameters:**
- `topic`: Topic to research
- `depth`: Research depth ("quick", "medium", or "deep")
- `sources`: Optional list of source URLs to analyze

**Returns:**
```python
{
    "topic": str,
    "summary": str,
    "key_points": List[str],
    "insights": str,
    "sources_used": List[str],
    "depth": str
}
```

#### `research_competitor(company_name, competitor_name) -> Dict`

Compare two companies for competitive analysis.

**Parameters:**
- `company_name`: Main company
- `competitor_name`: Competitor to compare

**Returns:**
```python
{
    "company_name": str,
    "competitor_name": str,
    "similarities": str,
    "differences": str,
    "competitive_advantages": str,
    "market_positioning": str,
    "recommendations": str
}
```

#### `fetch_website(url) -> str`

Fetch and parse website content.

**Parameters:**
- `url`: Website URL

**Returns:** Parsed text content (up to 5000 characters)

#### `find_company_website(company_name) -> Optional[str]`

Try to find company website URL.

**Parameters:**
- `company_name`: Name of the company

**Returns:** Website URL if found, None otherwise

## Use Cases

### Job Application
```python
# Research company before applying
research = ResearchService(api_key=api_key)

company_info = research.research_company(
    "Target Company",
    context="for job application"
)

# Use in application email
email_body = f"""
I'm impressed by {company_info['what_they_build']}
and my experience with {company_info['tech_stack'][0]} aligns well...
"""
```

### Market Research
```python
# Research market landscape
companies = ["Company A", "Company B", "Company C"]

for company in companies:
    info = research.research_company(company)
    print(f"{company}: {info['stage']} - {info['what_they_build']}")

# Compare competitors
comparison = research.research_competitor("Company A", "Company B")
```

### Content Creation
```python
# Research topic for blog post
topic_research = research.research_topic(
    "Future of AI in healthcare",
    depth="deep"
)

# Use insights for content
blog_outline = f"""
Title: {topic_research['topic']}
Summary: {topic_research['summary']}
Key Points:
{chr(10).join('- ' + point for point in topic_research['key_points'])}
"""
```

### Sales Intelligence
```python
# Research prospect company
prospect_info = research.research_company(
    "Prospect Company",
    context="for sales outreach"
)

# Tailor pitch
pitch = f"""
I noticed you're building {prospect_info['what_they_build']}.
Given your {prospect_info['stage']} stage...
"""
```

## Testing

```bash
# Test research service
OPENAI_API_KEY=your-key python -m research_agent.research_service

# Run tests
python tests/test_research.py
```

## Requirements

- Python 3.9+
- OpenAI API key
- Internet connection

## Security

- API key should be kept secure (use environment variables)
- Respects website robots.txt (future enhancement)
- Rate limiting for web scraping (future enhancement)

## Limitations

- Website content limited to 5000 characters
- May not find all company websites automatically
- Depends on OpenAI API availability
- Web scraping may fail for some sites

## Future Enhancements

- Search API integration (Google, Bing, Brave)
- PDF document analysis
- LinkedIn company profile scraping
- Crunchbase integration
- Rate limiting and caching
- Multi-language support

## License

MIT License

## Author

Yash Mittal

## Version

1.0.0
