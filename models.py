"""
Pydantic models for input validation and type safety.

This module defines all data models used throughout Dana's Brain,
ensuring type safety and proper validation of user inputs.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class CampaignInput(BaseModel):
    """
    Validated input for campaign content generation.

    All fields are required and validated to ensure quality inputs
    before processing begins.
    """

    product: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Product or service name"
    )

    benefits: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Key product benefits (at least 10 characters)"
    )

    audience: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Target audience description (at least 5 characters)"
    )

    offer: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Promotional offer or call-to-action"
    )

    persona: Literal[
        "Professional Dana",
        "Friendly Dana",
        "Inspirational Dana",
        "Mentor Dana"
    ] = Field(
        ...,
        description="Selected Dana persona for content generation"
    )

    @validator('product', 'benefits', 'audience', 'offer')
    def not_empty_after_strip(cls, v: str) -> str:
        """Ensure field is not just whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError('Field cannot be empty or only whitespace')
        return stripped

    @validator('benefits')
    def benefits_sufficient_detail(cls, v: str) -> str:
        """Ensure benefits have sufficient detail."""
        if len(v.strip()) < 10:
            raise ValueError('Benefits must be at least 10 characters for meaningful content')
        return v

    @validator('audience')
    def audience_sufficient_detail(cls, v: str) -> str:
        """Ensure audience description has sufficient detail."""
        if len(v.strip()) < 5:
            raise ValueError('Audience description must be at least 5 characters')
        return v

    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True
        validate_assignment = True

    def to_dict(self) -> dict:
        """Convert to dictionary for agent consumption."""
        return {
            'product': self.product,
            'benefits': self.benefits,
            'audience': self.audience,
            'offer': self.offer,
            'persona': self.persona
        }


class ToolInitError(BaseModel):
    """Error information from tool initialization."""

    error_type: str = Field(..., description="Type of error that occurred")
    message: str = Field(..., description="Human-readable error message")
    missing_files: Optional[list[str]] = Field(None, description="List of missing file paths")
    suggestion: str = Field(..., description="Suggested action to fix the error")

    def format_for_user(self) -> str:
        """Format error for display to user."""
        msg = f"❌ **{self.error_type}**: {self.message}\n\n"

        if self.missing_files:
            msg += "**Missing files:**\n"
            for file in self.missing_files:
                msg += f"- `{file}`\n"
            msg += "\n"

        msg += f"**Suggestion**: {self.suggestion}"
        return msg


class AgentExecutionResult(BaseModel):
    """Result from agent execution."""

    success: bool = Field(..., description="Whether execution succeeded")
    content: Optional[str] = Field(None, description="Generated content")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class CrewExecutionConfig(BaseModel):
    """Configuration for crew execution."""

    inputs: dict = Field(..., description="Input dictionary for the crew")
    timeout: int = Field(default=180, description="Timeout in seconds")
    verbose: bool = Field(default=True, description="Enable verbose logging")

    @validator('timeout')
    def timeout_reasonable(cls, v: int) -> int:
        """Ensure timeout is reasonable (30 sec to 10 min)."""
        if v < 30:
            raise ValueError('Timeout must be at least 30 seconds')
        if v > 600:
            raise ValueError('Timeout cannot exceed 10 minutes (600 seconds)')
        return v


class OutputMetadata(BaseModel):
    """Metadata for generated output files."""

    product_name: str
    persona: str
    timestamp: datetime = Field(default_factory=datetime.now)
    word_count: Optional[int] = None
    post_count: int = 9
    execution_time: Optional[float] = None

    def generate_filename(self) -> str:
        """
        Generate filename for the output markdown file.

        Format: YYYYMMDD_HHMMSS_ProductName_Persona.md
        """
        # Clean product name (remove special chars)
        clean_product = "".join(
            c for c in self.product_name if c.isalnum() or c in (' ', '_', '-')
        ).strip().replace(' ', '_')

        # Clean persona (remove "Dana" suffix)
        clean_persona = self.persona.replace(' Dana', '').replace(' ', '_')

        # Format timestamp
        timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")

        return f"{timestamp_str}_{clean_product}_{clean_persona}.md"


class SearchTransparencyLog(BaseModel):
    """Log entry for search transparency."""

    tool_name: str = Field(..., description="Name of the tool used")
    search_query: str = Field(..., description="Search query executed")
    results_found: int = Field(..., description="Number of results found")
    timestamp: datetime = Field(default_factory=datetime.now)

    def format_for_display(self) -> str:
        """Format for display to user."""
        return f"🔍 Searching **{self.tool_name}** for: *{self.search_query}* → {self.results_found} results"


class PersonaSearchTerms(BaseModel):
    """Search terms specific to a persona."""

    persona: str
    tone_terms: list[str] = Field(..., description="Tone-related search terms")
    style_terms: list[str] = Field(..., description="Style-related search terms")

    class Config:
        """Pydantic configuration."""
        frozen = True  # Immutable


class ValidationError(BaseModel):
    """Structured validation error."""

    field: str = Field(..., description="Field that failed validation")
    error: str = Field(..., description="Error message")
    value: Optional[str] = Field(None, description="Value that was rejected")

    def format_for_user(self) -> str:
        """Format for display to user."""
        msg = f"❌ **{self.field}**: {self.error}"
        if self.value:
            msg += f" (received: '{self.value[:50]}...')" if len(self.value) > 50 else f" (received: '{self.value}')"
        return msg


class WebScrapingInput(BaseModel):
    """Input for web scraping operation."""

    url: str = Field(
        ...,
        min_length=10,
        description="URL to scrape"
    )

    @validator('url')
    def validate_url(cls, v: str) -> str:
        """Ensure URL is valid and has proper protocol."""
        import re

        url = v.strip()

        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not url_pattern.match(url):
            raise ValueError('כתובת URL לא תקינה. ודא שהכתובת מתחילה ב-http:// או https://')

        return url


class WebScrapingResult(BaseModel):
    """Result from web scraping operation."""

    success: bool = Field(..., description="Whether scraping succeeded")
    url: str = Field(..., description="URL that was scraped")

    # Extracted fields (optional)
    product: Optional[str] = Field(None, description="Extracted product name")
    benefits: Optional[str] = Field(None, description="Extracted benefits")
    audience: Optional[str] = Field(None, description="Extracted target audience")
    offer: Optional[str] = Field(None, description="Extracted offer")

    # Metadata
    error_message: Optional[str] = Field(None, description="Error message if failed")
    extraction_confidence: Optional[float] = Field(None, description="Confidence score 0-1")
    detected_language: Optional[str] = Field(None, description="Detected language")

    def get_filled_fields(self) -> list[str]:
        """Get list of fields that were successfully extracted."""
        filled = []
        for field in ['product', 'benefits', 'audience', 'offer']:
            value = getattr(self, field)
            if value and value.strip():
                filled.append(field)
        return filled

    def get_empty_fields(self) -> list[str]:
        """Get list of fields that were NOT extracted."""
        empty = []
        for field in ['product', 'benefits', 'audience', 'offer']:
            value = getattr(self, field)
            if not value or not value.strip():
                empty.append(field)
        return empty

    def format_warning_message(self) -> str:
        """Format warning message for empty fields in Hebrew."""
        empty = self.get_empty_fields()
        if not empty:
            return ""

        field_names_hebrew = {
            'product': 'שם מוצר',
            'benefits': 'יתרונות',
            'audience': 'קהל יעד',
            'offer': 'הצעה'
        }

        missing_names = [field_names_hebrew.get(f, f) for f in empty]
        return f"⚠️ השדות הבאים לא נמצאו באתר: {', '.join(missing_names)}"
