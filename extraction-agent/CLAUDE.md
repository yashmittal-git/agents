# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Agent Overview

**extraction-agent** is a universal content extraction service that uses GPT-4o Vision to extract structured data from any content type (images, PDFs, URLs, text).

## Core Architecture

### Main Service: `extraction_agent/extraction_service.py`

The `ExtractionService` class provides a unified interface for extracting structured data:

```python
class ExtractionService:
    def extract(content, content_type, schema, instructions) -> Dict
    def extract_from_image(image_path, schema, instructions) -> Dict
    def extract_from_text(text, schema, instructions) -> Dict
    def extract_from_url(url, schema, instructions) -> Dict
    def extract_from_pdf(pdf_path, schema, instructions) -> Dict
```

### Schema-Based Extraction

The agent uses **schema definitions** to extract structured data:
- Schema is a dict where keys are field names and values are descriptions
- The AI extracts data matching the schema from the content
- Returns structured JSON matching the schema

Example schema:
```python
schema = {
    "company_name": "Company name",
    "role": "Job role/title",
    "recruiter_email": "Recruiter email (if visible, else null)",
    "requirements": "Job requirements as string"
}
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
cd extraction-agent
python tests/test_extraction.py
```

### Installing/Reinstalling
```bash
# From repository root with venv activated
cd /Users/yash/Documents/agents
source venv/bin/activate
pip install -e extraction-agent
```

## Dependencies

- `openai>=1.0.0` - For GPT-4o and GPT-4o Vision
- `requests>=2.31.0` - For URL fetching
- `PyPDF2>=3.0.0` - For PDF parsing

Model used: `gpt-4o` (supports both text and vision)

## Key Methods

### `extract()` - Universal extraction
Main entry point that delegates to specific extractors based on `content_type`:
- `"image"` → `extract_from_image()`
- `"text"` → `extract_from_text()`
- `"url"` → `extract_from_url()`
- `"pdf"` → `extract_from_pdf()`

### `extract_from_image()` - Vision extraction
Uses GPT-4o Vision to analyze images (screenshots, photos, diagrams):
- Encodes image to base64
- Sends to OpenAI with schema and instructions
- Returns structured JSON

### `extract_from_url()` - Web scraping + AI
1. Fetches webpage content with requests
2. Extracts text with BeautifulSoup
3. Uses GPT-4o to extract structured data

### `extract_from_pdf()` - PDF parsing + AI
1. Extracts text from PDF with PyPDF2
2. Uses GPT-4o to extract structured data

## Common Use Cases

1. **Job posting extraction** from screenshots (LinkedIn, email, WhatsApp)
2. **Resume parsing** from PDFs
3. **Document analysis** from any format
4. **Web scraping** with intelligent extraction
5. **Message extraction** from chat screenshots

## Integration Points

This agent is used by:
- **job-outreach-agent** - Extracts job info from screenshots/text files via CLI
- Can be imported by any Python service needing content extraction

## Important Notes

- The service is **stateless** - no database, no persistent storage
- All extraction happens via OpenAI API calls
- Requires valid OpenAI API key with GPT-4o access
- Image extraction requires GPT-4o Vision capabilities
- PDF extraction may be slow for large documents
