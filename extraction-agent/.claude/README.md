# Extraction Agent - Claude Code Context

## Purpose

The **Extraction Agent** is a universal content extraction service that uses AI (GPT-4o Vision and GPT-4o) to extract structured information from any content type.

## What This Agent Does

1. **Extract from Images**: Uses GPT-4o Vision to extract structured data from screenshots, photos, diagrams
2. **Extract from Text**: Uses GPT-4o to extract structured data from text files, raw text, messages
3. **Extract from URLs**: Fetches web page content and extracts structured data
4. **Extract from PDFs**: Parses PDF files and extracts structured data
5. **Schema-Based Extraction**: You define what you want (schema), it extracts it

## Key Design Principles

### 1. Generic and Reusable

This agent is NOT specific to job applications or any domain. It's a generic extraction service.

**Good:**
```python
# Job application extraction
schema = {"company_name": "Company name", "role": "Job title"}
extractor.extract(content, "image", schema)

# Meeting notes extraction
schema = {"attendees": "People present", "action_items": "Tasks"}
extractor.extract(content, "text", schema)

# Invoice extraction
schema = {"total": "Total amount", "date": "Invoice date"}
extractor.extract(content, "pdf", schema)
```

**Bad:**
```python
# DON'T hardcode job-specific logic in this agent
def extract_job_info(image):  # ❌ Too specific
    ...
```

### 2. Schema-Driven

The extraction is driven by a schema dictionary that defines expected fields:

```python
schema = {
    "field_name": "Description of what this field should contain",
    "another_field": "Description (can say 'null if not found')"
}
```

The AI uses this schema to know what to extract.

### 3. Content Type Agnostic

The `extract()` method automatically handles different content types:

```python
# All of these work with the same interface
extractor.extract(content="screenshot.png", content_type="image", schema=schema)
extractor.extract(content="text.txt", content_type="text", schema=schema)
extractor.extract(content="https://...", content_type="url", schema=schema)
extractor.extract(content="doc.pdf", content_type="pdf", schema=schema)
```

## Architecture

### Main Class: ExtractionService

```python
class ExtractionService:
    def __init__(self, api_key: str, model: str = "gpt-4o")

    # Universal method
    def extract(self, content, content_type, schema, instructions=None) -> Dict

    # Specific methods
    def extract_from_image(self, image_path, schema, instructions=None) -> Dict
    def extract_from_text(self, text, schema, instructions=None) -> Dict
    def extract_from_url(self, url, schema, instructions=None) -> Dict
    def extract_from_pdf(self, pdf_path, schema, instructions=None) -> Dict

    # Helper
    def _build_schema_description(self, schema: Dict[str, str]) -> str
```

### How It Works

1. **User provides**: Content + Content Type + Schema + Instructions (optional)
2. **Service routes**: Based on content_type, calls appropriate extract method
3. **Appropriate method**:
   - Loads/fetches content
   - Builds prompt from schema and instructions
   - Calls GPT-4o or GPT-4o Vision
   - Returns structured JSON matching schema
4. **Result**: Dictionary with keys matching schema

### Example Flow

```
User Input:
  content = "job_screenshot.png"
  content_type = "image"
  schema = {"company": "Company name", "role": "Job title"}
  instructions = "Extract job info"

↓

extract() routes to extract_from_image()

↓

extract_from_image():
  1. Reads and base64 encodes image
  2. Builds prompt: "Extract job info. Return JSON with: company, role"
  3. Calls GPT-4o Vision API
  4. Parses JSON response

↓

Output:
  {"company": "Anthropic", "role": "Senior Engineer"}
```

## Usage Patterns

### Pattern 1: Job Application Agent (Current Use Case)

```python
from extraction_agent import ExtractionService

extractor = ExtractionService(api_key=api_key)

job_schema = {
    "company_name": "Company name",
    "role": "Job title",
    "recruiter_email": "Email (or null)",
    "requirements": "Job requirements"
}

job_info = extractor.extract(
    content="screenshot.png",
    content_type="image",
    schema=job_schema,
    instructions="Extract job posting information"
)
```

### Pattern 2: Any Other Agent

```python
# Market research agent
research_schema = {
    "competitors": "List of competitors",
    "market_size": "Market size estimate",
    "trends": "Key market trends"
}

insights = extractor.extract(
    content="https://industry-report.com",
    content_type="url",
    schema=research_schema
)
```

### Pattern 3: Batch Extraction

```python
# Extract from multiple sources
sources = [
    ("linkedin_post.png", "image"),
    ("email.txt", "text"),
    ("https://company.com/careers", "url")
]

results = []
for content, content_type in sources:
    result = extractor.extract(content, content_type, schema)
    results.append(result)
```

## Integration with Other Agents

### Job Outreach Agent

The job-outreach-agent uses extraction-agent to extract job information:

```python
# job_outreach_agent/job_orchestrator.py

from extraction_agent import ExtractionService

class JobOrchestrator:
    def __init__(self, ...):
        self.extractor = ExtractionService(api_key=openai_api_key)

    def process_job(self, content, content_type):
        # Extract job info using extraction-agent
        job_info = self.extractor.extract(
            content=content,
            content_type=content_type,
            schema=self.job_schema
        )

        # Continue with research, matching, content generation...
```

### Any Future Agent

Any agent can use extraction-agent for content extraction:

```python
from extraction_agent import ExtractionService

class MyAgent:
    def __init__(self, api_key):
        self.extractor = ExtractionService(api_key=api_key)

    def process(self, content):
        data = self.extractor.extract(content, "image", my_schema)
        # Use extracted data...
```

## What This Agent Does NOT Do

1. **Does NOT make decisions** - Only extracts data, doesn't decide what to do with it
2. **Does NOT send emails** - Use email-agent for that
3. **Does NOT research companies** - Use research-agent for that
4. **Does NOT generate content** - Use content-agent for that
5. **Does NOT orchestrate workflows** - Use job-outreach-agent or other orchestrators

## Extension Points

### Adding New Content Type

To add a new content type (e.g., "audio"):

1. Add new method: `extract_from_audio(audio_path, schema, instructions)`
2. Update `extract()` method to route to it
3. Use appropriate AI model/API for that content type

### Custom Preprocessing

You can subclass and override methods:

```python
class CustomExtractor(ExtractionService):
    def extract_from_image(self, image_path, schema, instructions=None):
        # Custom preprocessing
        processed_image = self.preprocess_image(image_path)
        # Call parent
        return super().extract_from_image(processed_image, schema, instructions)
```

## Error Handling

The service raises appropriate errors:

- `ValueError`: Invalid content_type, failed to fetch URL, failed to read PDF
- `FileNotFoundError`: File doesn't exist
- `ImportError`: Missing dependency (e.g., PyPDF2)

## Dependencies

- **openai**: For GPT-4o and GPT-4o Vision API
- **requests**: For fetching URLs
- **PyPDF2**: For PDF parsing (optional, only needed for PDF extraction)

## Testing

See `tests/test_extraction.py` for example tests.

## Files

- `extraction_agent/extraction_service.py` - Main service implementation
- `extraction_agent/__init__.py` - Package initialization
- `setup.py` - Package installation
- `requirements.txt` - Dependencies
- `README.md` - User documentation
- `tests/test_extraction.py` - Tests

## Development Guidelines

### DO:

- Keep the service generic and domain-agnostic
- Support any schema structure
- Handle errors gracefully
- Add support for new content types when needed
- Write clear error messages

### DON'T:

- Hardcode domain-specific logic (job postings, invoices, etc.)
- Make assumptions about schema structure
- Make decisions about what to do with extracted data
- Add orchestration logic (that's for orchestrator agents)
- Couple with other agents (keep it independent)

## Version

1.0.0

## Relationships

**Used by:**
- job-outreach-agent (extracts job information)
- Any future agent needing content extraction

**Uses:**
- OpenAI API (GPT-4o, GPT-4o Vision)
- requests library (URL fetching)
- PyPDF2 library (PDF parsing)

**Does NOT depend on:**
- email-agent
- research-agent
- content-agent
- linkedin-agent

## Future Enhancements

Potential future additions:
- Audio transcription extraction
- Video content extraction
- Table extraction from complex PDFs
- Batch extraction with parallelization
- Caching layer for repeated extractions
- Custom model selection per content type

---

**This agent is the foundation for content understanding in the agents ecosystem.**
