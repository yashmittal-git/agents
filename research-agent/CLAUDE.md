# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Agent Overview

**research-agent** is a standalone AI-powered web research service that performs company research, topic analysis, and competitive intelligence using web scraping + GPT-4o.

## Core Architecture

### Main Service: `research_agent/research_service.py`

The `ResearchService` class provides research capabilities:

```python
class ResearchService:
    def __init__(api_key, model="gpt-4o")
    def research_company(company_name, context=None) -> Dict
    def research_topic(topic, context=None) -> Dict
```

### Research Process

**Company Research Flow:**
1. Generate search query for company
2. Attempt to find company website
3. Scrape website content (if found)
4. Use GPT-4o to analyze and structure insights
5. Return structured company profile

**Topic Research Flow:**
1. Generate search query for topic
2. Use GPT-4o to synthesize information
3. Return structured insights

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
cd research-agent
python tests/test_research.py
```

### Installing/Reinstalling
```bash
# From repository root with venv activated
cd /Users/yash/Documents/agents
source venv/bin/activate
pip install -e research-agent
```

## Dependencies

- `openai>=1.0.0` - For GPT-4o AI analysis
- `requests>=2.31.0` - For HTTP requests
- `beautifulsoup4>=4.12.0` - For HTML parsing

Model used: `gpt-4o`

## Key Methods

### `research_company()` - Company research
Returns structured company profile:
```python
{
    "company_name": "Anthropic",
    "what_they_build": "AI safety-focused language models...",
    "tech_stack": ["Python", "PyTorch", "Kubernetes"],
    "stage": "growth",
    "relevant_context": "Context specific to your query",
    "website_url": "https://www.anthropic.com"
}
```

**Parameters:**
- `company_name`: Company to research
- `context`: Optional context (e.g., "for job application as SWE")

**Process:**
1. Searches for company website
2. Scrapes and parses website HTML
3. Extracts text content
4. Uses GPT-4o to analyze and structure
5. Returns comprehensive company profile

### `research_topic()` - Topic research
Returns structured topic insights:
```python
{
    "topic": "AI Safety",
    "summary": "Overview of the topic...",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "relevant_context": "Context specific to your query"
}
```

**Parameters:**
- `topic`: Topic to research
- `context`: Optional context to focus research

## Web Scraping Details

### URL Discovery
- Constructs search-friendly query
- Attempts to find official company website
- Falls back to search-based research if no website found

### Content Extraction
- Uses BeautifulSoup to parse HTML
- Extracts text from paragraphs, headings, lists
- Cleans and structures content for AI analysis
- Limits content length to avoid token limits

### Error Handling
- Gracefully handles failed requests
- Falls back to AI-only research if scraping fails
- Continues even if website is unreachable

## AI Analysis

Uses GPT-4o to:
- Synthesize scraped content into structured insights
- Extract tech stack and company stage
- Generate relevant context based on research purpose
- Produce consistent JSON output format

## Integration Points

This agent is used by:
- **job-outreach-agent** - Researches companies for job applications
- Can be imported by any service needing research capabilities

## Important Notes

- **No database** - Stateless, no caching
- **Rate limits** - Web scraping may be rate-limited by target sites
- **Content quality** - Depends on website structure and content
- **Cost** - Each research call uses OpenAI API tokens
- **Accuracy** - AI analysis is context-dependent, may not be 100% accurate
- Some websites may block scraping (robots.txt, anti-bot measures)
