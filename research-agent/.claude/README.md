# Research Agent - Context for Claude Code

## Project Overview

**Research Agent** is a standalone web research service that combines web scraping with AI-powered analysis. It can research companies, topics, competitors, and markets.

## Core Purpose

Provide intelligent research capabilities for any Python project that needs to gather and analyze information from the web.

## Architecture

### Single Service
- `research_agent/research_service.py`: Core ResearchService class
- No dependencies on other agents
- Fully self-contained

### Design Principles

1. **Generic**: Works for any research need (companies, topics, markets)
2. **AI-Powered**: Uses GPT-4o for intelligent analysis
3. **Flexible**: Multiple research methods (company, topic, competitor)
4. **Structured Output**: Always returns JSON
5. **Reusable**: Can be installed in any project

## Key Components

### ResearchService Class

```python
class ResearchService:
    def __init__(api_key: str, model: str = "gpt-4o")

    # Core methods
    def research_company(company_name, context="", website_url=None) -> Dict
    def research_topic(topic, depth="medium", sources=None) -> Dict
    def research_competitor(company_name, competitor_name) -> Dict

    # Utility methods
    def fetch_website(url) -> str
    def find_company_website(company_name) -> Optional[str]
```

### Technologies Used

- **OpenAI GPT-4o**: AI-powered analysis
- **BeautifulSoup**: HTML parsing
- **requests**: HTTP requests for web scraping

## Usage Patterns

### Pattern 1: Company Research (Job Application)

```python
from research_agent import ResearchService

research = ResearchService(api_key=api_key)

company_info = research.research_company(
    "Anthropic",
    context="for job application as Software Engineer"
)

# Returns:
# {
#     "what_they_build": "...",
#     "tech_stack": ["Python", "PyTorch", ...],
#     "stage": "growth",
#     "relevant_context": "..."
# }
```

### Pattern 2: Topic Research (Content Creation)

```python
research = ResearchService(api_key=api_key)

insights = research.research_topic(
    "AI safety trends 2024",
    depth="deep"
)

# Use for blog post, report, etc.
```

### Pattern 3: Competitor Analysis (Market Research)

```python
comparison = research.research_competitor(
    "Anthropic",
    "OpenAI"
)

# Returns competitive insights
```

## Installation

### In Other Projects

```bash
# Local development
pip install -e /path/to/agents/research-agent

# Or in requirements.txt
-e ../agents/research-agent
```

### In Job Outreach Agent

```python
# job-outreach-agent/requirements.txt
-e ../agents/research-agent
```

## Configuration

### OpenAI API Key

Required for AI-powered analysis:

```python
# Option 1: Environment variable
export OPENAI_API_KEY="your-key"
research = ResearchService(api_key=os.getenv("OPENAI_API_KEY"))

# Option 2: Direct
research = ResearchService(api_key="your-key")
```

### Model Selection

Default is GPT-4o, but can use other models:

```python
research = ResearchService(
    api_key=api_key,
    model="gpt-4o-mini"  # Faster, cheaper
)
```

## Web Scraping

### Website Discovery

Automatically tries common URL patterns:
- `https://www.{company}.com`
- `https://{company}.com`
- `https://www.{company}.io`
- `https://{company}.ai`

### Content Extraction

- Fetches HTML content
- Removes scripts and styles
- Extracts clean text
- Limits to 5000 characters (to fit in AI context)

### Error Handling

- Timeouts (10 seconds max)
- Connection errors
- HTTP errors
- Graceful fallback to "information not available"

## AI Analysis

### Structured Output

Always uses `response_format={"type": "json_object"}` for structured JSON output.

### Prompts

Carefully crafted prompts for:
- Company analysis (tech stack, stage, products)
- Topic research (summary, key points, insights)
- Competitor comparison (similarities, differences, advantages)

### Context Injection

Can inject additional context:
```python
research.research_company(
    "Anthropic",
    context="for investment analysis"  # Tailors output
)
```

## Testing

```bash
# Test with environment variable
OPENAI_API_KEY=your-key python -m research_agent.research_service

# Run full tests
python tests/test_research.py
```

## Extension Points

### Future Features to Add

1. **Search API Integration**
   - Google Search API
   - Brave Search API
   - Serper API

2. **Enhanced Scraping**
   - JavaScript rendering (Selenium/Playwright)
   - PDF document analysis
   - LinkedIn profile scraping

3. **Caching**
   - Cache research results
   - Avoid duplicate requests
   - TTL-based invalidation

4. **Rate Limiting**
   - Respect robots.txt
   - Throttle requests
   - Queue management

5. **Multi-source Research**
   - Crunchbase API
   - LinkedIn API
   - Twitter API
   - News APIs

### How to Extend

Example: Add search API integration

```python
def research_company_with_search(self, company_name):
    # 1. Use search API to find company
    search_results = self.search_api.search(f"{company_name} official site")

    # 2. Fetch top results
    for result in search_results[:3]:
        content += self.fetch_website(result['url'])

    # 3. Analyze with AI
    analysis = self.analyze_with_ai(content)

    return analysis
```

## Guidelines for Claude Code

### When Working on Research Agent

1. **Keep it generic**: Don't add job-specific or email-specific logic
2. **Structured output**: Always return consistent JSON structure
3. **Error handling**: Graceful fallbacks, never crash
4. **Documentation**: Update README for new features
5. **Testing**: Test with real websites and API

### Common Tasks

**Add new research method:**
```python
def research_market(self, market_name: str, region: str = "global"):
    # Research market trends, size, competitors
    # Return structured JSON
    pass
```

**Add caching:**
```python
import functools
from functools import lru_cache

@lru_cache(maxsize=100)
def research_company(self, company_name, context=""):
    # Research results cached for same inputs
    pass
```

**Add search API:**
```python
def search_web(self, query: str) -> List[Dict]:
    # Integrate with Brave/Google/Serper
    # Return search results
    pass
```

### DON'Ts

- ❌ Don't add content generation (that's content-agent)
- ❌ Don't add email sending (that's email-agent)
- ❌ Don't add job matching logic (that's job-outreach-agent)
- ❌ Don't add heavy dependencies (keep it lightweight)
- ❌ Don't store sensitive data in code

### DOs

- ✅ Keep focused on research and analysis
- ✅ Make it flexible and configurable
- ✅ Add helpful error messages
- ✅ Support multiple research types
- ✅ Document everything clearly

## Integration with Other Agents

### Used By:

1. **job-outreach-agent**: Research companies for job applications
2. **market-research-tool** (future): Market analysis
3. **sales-automation** (future): Prospect research
4. **content-creator** (future): Topic research for content

### Uses:

None - Research agent is fully self-contained.

## File Structure

```
research-agent/
├── .claude/
│   └── README.md          # This file (Claude context)
├── research_agent/
│   ├── __init__.py        # Package init
│   └── research_service.py # Core service
├── tests/
│   └── test_research.py   # Tests
├── README.md              # User documentation
├── requirements.txt       # Dependencies
└── setup.py               # Package setup
```

## Development Workflow

1. **Make changes** to research_service.py
2. **Test locally**: `OPENAI_API_KEY=key python -m research_agent.research_service`
3. **Run tests**: `python tests/test_research.py`
4. **Update documentation**: README.md and this file
5. **Test integration**: Use in job-outreach-agent
6. **Commit changes**: Git commit with clear message

## Performance Considerations

### API Costs

- GPT-4o is expensive (~$5 per million input tokens)
- Consider using gpt-4o-mini for simple research
- Cache results to avoid duplicate API calls

### Web Scraping

- Respect rate limits
- Use timeouts to avoid hanging
- Handle errors gracefully
- Consider using CDN/cache for popular sites

### Output Size

- Limit website content to 5000 chars
- Keep AI output focused and concise
- Use pagination for large result sets

## Version History

- **1.0.0**: Initial release with company/topic/competitor research

---

**This agent is production-ready and can be used in any Python project for intelligent web research.**
