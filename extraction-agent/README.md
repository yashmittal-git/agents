# Extraction Agent

**Universal Content Extraction Service** - Extract structured information from any content type using AI.

## Overview

The Extraction Agent is a generic service that extracts structured data from various content sources:

- **Images**: Screenshots, photos, diagrams (using GPT-4o Vision)
- **Text**: Plain text, text files, messages
- **URLs**: Web pages, blog posts, documentation
- **PDFs**: Documents, reports, resumes

## Key Feature

**Generic Schema-Based Extraction** - You define what you want to extract, and the service extracts it.

## Installation

```bash
cd /Users/yash/Documents/agents/extraction-agent
pip install -e .
```

## Quick Start

```python
from extraction_agent import ExtractionService

# Initialize
extractor = ExtractionService(api_key="your-openai-api-key")

# Define what you want to extract
schema = {
    "company_name": "Company name",
    "role": "Job role/title",
    "recruiter_email": "Recruiter email (if visible, else null)",
    "requirements": "Job requirements (as string)"
}

# Extract from image
result = extractor.extract(
    content="path/to/job_screenshot.png",
    content_type="image",
    schema=schema,
    instructions="Extract job posting information"
)

print(result)
# {
#   "company_name": "Anthropic",
#   "role": "Senior Software Engineer",
#   "recruiter_email": "careers@anthropic.com",
#   "requirements": "Python, AI/ML, 5+ years experience..."
# }
```

## Usage

### Extract from Image

```python
from extraction_agent import ExtractionService

extractor = ExtractionService(api_key=api_key)

# Screenshot of job posting
schema = {
    "company_name": "Company name",
    "role": "Job title",
    "location": "Job location"
}

result = extractor.extract_from_image(
    image_path="job_screenshot.png",
    schema=schema,
    instructions="Extract job information"
)
```

### Extract from Text

```python
# From text file
result = extractor.extract_from_text(
    text="path/to/job_posting.txt",
    schema=schema,
    instructions="Extract job information"
)

# From raw text
text_content = "We're hiring a Senior Engineer at Anthropic..."
result = extractor.extract_from_text(
    text=text_content,
    schema=schema
)
```

### Extract from URL

```python
# From web page
result = extractor.extract_from_url(
    url="https://anthropic.com/careers/engineer",
    schema=schema,
    instructions="Extract job information"
)
```

### Extract from PDF

```python
# From PDF file
result = extractor.extract_from_pdf(
    pdf_path="job_description.pdf",
    schema=schema,
    instructions="Extract job information"
)
```

### Universal Extract Method

```python
# Automatically handles different content types
result = extractor.extract(
    content="screenshot.png",
    content_type="image",
    schema=schema
)

result = extractor.extract(
    content="https://example.com/job",
    content_type="url",
    schema=schema
)
```

## Use Cases

### Job Application Extraction

```python
schema = {
    "company_name": "Company name",
    "role": "Job role/title",
    "recruiter_email": "Recruiter email (if visible, else null)",
    "recruiter_linkedin": "LinkedIn URL (if visible, else null)",
    "requirements": "Job requirements",
    "salary_range": "Salary range (if mentioned, else null)"
}

result = extractor.extract(
    content="linkedin_job_screenshot.png",
    content_type="image",
    schema=schema,
    instructions="Extract job posting from LinkedIn screenshot"
)
```

### WhatsApp Message Extraction

```python
schema = {
    "sender_name": "Name of sender",
    "job_title": "Job title mentioned",
    "company": "Company name",
    "contact_info": "Contact information"
}

result = extractor.extract(
    content="whatsapp_screenshot.png",
    content_type="image",
    schema=schema,
    instructions="Extract job referral information from WhatsApp message"
)
```

### Notion Page Extraction

```python
# Copy Notion page content to text file
schema = {
    "tasks": "List of tasks mentioned",
    "deadlines": "Deadlines mentioned",
    "key_points": "Key points or highlights"
}

result = extractor.extract(
    content="notion_page.txt",
    content_type="text",
    schema=schema,
    instructions="Extract action items from Notion page"
)
```

### Resume Parsing

```python
schema = {
    "name": "Candidate name",
    "email": "Email address",
    "phone": "Phone number",
    "skills": "List of skills",
    "experience": "Work experience summary",
    "education": "Education background"
}

result = extractor.extract(
    content="resume.pdf",
    content_type="pdf",
    schema=schema,
    instructions="Parse resume information"
)
```

## API Reference

### ExtractionService

```python
ExtractionService(api_key: str, model: str = "gpt-4o")
```

**Methods:**

- `extract(content, content_type, schema, instructions=None)` - Universal extraction
- `extract_from_image(image_path, schema, instructions=None)` - Image extraction
- `extract_from_text(text, schema, instructions=None)` - Text extraction
- `extract_from_url(url, schema, instructions=None)` - URL extraction
- `extract_from_pdf(pdf_path, schema, instructions=None)` - PDF extraction

**Parameters:**

- `content`: Content to extract from (file path, URL, or text)
- `content_type`: Type of content ("image", "text", "url", "pdf")
- `schema`: Dictionary defining expected fields (field_name -> description)
- `instructions`: Optional additional instructions for extraction

**Returns:** Dictionary with extracted data matching schema keys

## Schema Format

Schema is a dictionary where:
- **Key**: Field name you want in the output
- **Value**: Description of what that field should contain

```python
schema = {
    "field_name": "Description of this field",
    "another_field": "Description (can specify 'null if not found')"
}
```

## Error Handling

```python
try:
    result = extractor.extract(
        content="screenshot.png",
        content_type="image",
        schema=schema
    )
except ValueError as e:
    print(f"Extraction failed: {e}")
except FileNotFoundError:
    print("File not found")
```

## Dependencies

- `openai>=1.0.0` - For GPT-4o and GPT-4o Vision
- `requests>=2.31.0` - For URL fetching
- `PyPDF2>=3.0.0` - For PDF parsing

## Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-key"
```

Or pass directly:

```python
extractor = ExtractionService(api_key="your-key")
```

## Testing

```bash
cd extraction-agent
python tests/test_extraction.py
```

## Integration with Other Agents

The Extraction Agent is designed to be used by other agents:

```python
# In job-outreach-agent
from extraction_agent import ExtractionService

extractor = ExtractionService(api_key=api_key)

job_info = extractor.extract(
    content=user_screenshot,
    content_type="image",
    schema=job_schema
)
```

## Supported Content Types

| Type | Description | Example |
|------|-------------|---------|
| `image` | Screenshots, photos | Job postings, WhatsApp messages, LinkedIn posts |
| `text` | Plain text, text files | Job descriptions, messages, notes |
| `url` | Web pages | Career pages, blog posts, documentation |
| `pdf` | PDF documents | Resumes, job descriptions, reports |

## Limitations

- Image size limited by GPT-4o Vision API (max 20MB)
- URL fetching has 10-second timeout
- PDF extraction requires PyPDF2 library
- Complex PDFs (with tables, images) may have reduced accuracy

## Version

1.0.0

## Author

Yash Mittal (with Claude Sonnet 4.5)

---

**This agent provides universal content extraction for use in any AI workflow.**
