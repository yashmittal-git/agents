"""
Extraction Service - Universal content extraction

Extracts structured information from various content types:
- Images (screenshots, photos)
- Text files
- URLs (web pages)
- PDFs
- Any text content

Uses GPT-4o Vision for images, GPT-4o for text/URLs
"""

import base64
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from openai import OpenAI
import requests
from io import BytesIO


class ExtractionService:
    """Universal content extraction service"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initialize extraction service

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o)
        """
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def extract(
        self,
        content: Union[str, bytes],
        content_type: str,
        schema: Dict[str, str],
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Universal extraction method - extracts structured data from any content

        Args:
            content: Content to extract from (file path, URL, or text)
            content_type: Type of content ("image", "text", "url", "pdf")
            schema: Dictionary defining expected fields
                   Format: {"field_name": "field description"}
            instructions: Optional additional instructions

        Returns:
            Dictionary with extracted structured data

        Example:
            schema = {
                "company_name": "Company name",
                "role": "Job role/title",
                "recruiter_email": "Recruiter email (if visible, else null)",
                "requirements": "Job requirements (as string)"
            }

            result = extractor.extract(
                content="path/to/job_screenshot.png",
                content_type="image",
                schema=schema,
                instructions="Extract job posting information"
            )
        """
        if content_type == "image":
            return self.extract_from_image(content, schema, instructions)
        elif content_type == "text":
            return self.extract_from_text(content, schema, instructions)
        elif content_type == "url":
            return self.extract_from_url(content, schema, instructions)
        elif content_type == "pdf":
            return self.extract_from_pdf(content, schema, instructions)
        else:
            raise ValueError(f"Unsupported content_type: {content_type}")

    def extract_from_image(
        self,
        image_path: str,
        schema: Dict[str, str],
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured information from image using GPT-4o Vision

        Args:
            image_path: Path to image file
            schema: Dictionary defining expected fields
            instructions: Optional additional instructions

        Returns:
            Dictionary with extracted data matching schema
        """
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Build prompt from schema
        schema_description = self._build_schema_description(schema)

        base_prompt = instructions or "Extract information from this image."
        prompt = f"""{base_prompt}

Return JSON with these exact keys:
{schema_description}

Return ONLY valid JSON, no other text."""

        # Call GPT-4o Vision
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    def extract_from_text(
        self,
        text: str,
        schema: Dict[str, str],
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured information from text

        Args:
            text: Text content (can be file path or raw text)
            schema: Dictionary defining expected fields
            instructions: Optional additional instructions

        Returns:
            Dictionary with extracted data matching schema
        """
        # Check if text is a file path
        if Path(text).is_file():
            with open(text, 'r') as f:
                text_content = f.read()
        else:
            text_content = text

        # Build prompt from schema
        schema_description = self._build_schema_description(schema)

        base_prompt = instructions or "Extract information from this text."
        prompt = f"""{base_prompt}

Text to analyze:
{text_content}

Return JSON with these exact keys:
{schema_description}

Return ONLY valid JSON, no other text."""

        # Call GPT-4o
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    def extract_from_url(
        self,
        url: str,
        schema: Dict[str, str],
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured information from web page

        Args:
            url: URL to fetch and extract from
            schema: Dictionary defining expected fields
            instructions: Optional additional instructions

        Returns:
            Dictionary with extracted data matching schema
        """
        # Fetch URL content
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            text_content = response.text
        except Exception as e:
            raise ValueError(f"Failed to fetch URL: {e}")

        # Build prompt from schema
        schema_description = self._build_schema_description(schema)

        base_prompt = instructions or f"Extract information from this web page ({url})."
        prompt = f"""{base_prompt}

Web page content:
{text_content[:10000]}  # Limit to first 10k chars

Return JSON with these exact keys:
{schema_description}

Return ONLY valid JSON, no other text."""

        # Call GPT-4o
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    def extract_from_pdf(
        self,
        pdf_path: str,
        schema: Dict[str, str],
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured information from PDF

        Args:
            pdf_path: Path to PDF file
            schema: Dictionary defining expected fields
            instructions: Optional additional instructions

        Returns:
            Dictionary with extracted data matching schema

        Note:
            For now, this converts PDF to text and uses text extraction.
            For better PDF support, consider adding PyPDF2 or pdfplumber.
        """
        try:
            # Try using PyPDF2 if available
            import PyPDF2

            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text()
        except ImportError:
            # If PyPDF2 not available, return error
            raise ImportError(
                "PDF extraction requires PyPDF2. Install with: pip install PyPDF2"
            )
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {e}")

        # Use text extraction
        return self.extract_from_text(text_content, schema, instructions)

    def _build_schema_description(self, schema: Dict[str, str]) -> str:
        """
        Build schema description for prompt

        Args:
            schema: Dictionary of field_name -> description

        Returns:
            Formatted schema description
        """
        lines = []
        for field_name, description in schema.items():
            lines.append(f"- {field_name}: {description}")
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv(dotenv_path="../../.env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env")
        exit(1)

    extractor = ExtractionService(api_key=api_key)

    # Example: Extract from image
    schema = {
        "company_name": "Company name",
        "role": "Job role/title",
        "recruiter_email": "Recruiter email (if visible, else null)",
        "recruiter_linkedin": "LinkedIn profile URL (if visible, else null)",
        "recruiter_name": "Recruiter name (if visible, else null)",
        "requirements": "Job requirements (as string)"
    }

    print("Extraction Service initialized")
    print(f"API Key configured: {api_key[:10]}...")
    print("\nExample usage:")
    print("  result = extractor.extract(")
    print("      content='path/to/screenshot.png',")
    print("      content_type='image',")
    print("      schema=schema,")
    print("      instructions='Extract job posting information'")
    print("  )")
