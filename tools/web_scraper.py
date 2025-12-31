# -*- coding: utf-8 -*-
"""
Dana's Brain - Web Scraper Tool
Scrapes product information from websites and extracts structured data using LLM
"""

import re
import json
from typing import Dict, Any
from bs4 import BeautifulSoup
import requests
from openai import OpenAI

from models import WebScrapingInput, WebScrapingResult
from config import OPENAI_API_KEY


# Language detection patterns
HEBREW_PATTERN = re.compile(r'[\u0590-\u05FF]')
FRENCH_PATTERN = re.compile(r'[àâäæçéèêëïîôœùûüÿ]', re.IGNORECASE)


def detect_language(text: str) -> str:
    """
    Detect primary language of text.

    Args:
        text: Text to analyze

    Returns:
        Language code: 'he' (Hebrew), 'fr' (French), or 'en' (English)
    """
    hebrew_count = len(HEBREW_PATTERN.findall(text))
    french_count = len(FRENCH_PATTERN.findall(text))

    if len(text) > 0 and (hebrew_count / len(text)) > 0.05:
        return 'he'

    if french_count > 5:
        return 'fr'

    return 'en'


def scrape_website(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Scrape website and extract text content.

    Args:
        url: URL to scrape
        timeout: Request timeout in seconds

    Returns:
        Dict with clean_text, title, meta_description

    Raises:
        requests.RequestException: If request fails
        ValueError: If URL is invalid
    """
    # Validate URL
    validated_input = WebScrapingInput(url=url)
    clean_url = validated_input.url

    # Set headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'he,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }

    # Make request
    response = requests.get(clean_url, headers=headers, timeout=timeout, allow_redirects=True)
    response.raise_for_status()

    # Parse HTML
    soup = BeautifulSoup(response.content, 'lxml')

    # Remove unwanted elements
    for script in soup(['script', 'style', 'nav', 'footer', 'header']):
        script.decompose()

    # Extract title
    title = soup.title.string if soup.title else ""

    # Extract meta description
    meta_desc = ""
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag and meta_tag.get('content'):
        meta_desc = meta_tag['content']

    # Extract clean text
    text = soup.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text).strip()

    # Limit text length to avoid token limits
    if len(text) > 8000:
        text = text[:8000] + "..."

    return {
        'clean_text': text,
        'title': title.strip() if title else "",
        'meta_description': meta_desc.strip()
    }


def extract_campaign_data_with_llm(
    scraped_data: Dict[str, Any],
    detected_language: str
) -> Dict[str, str]:
    """
    Use OpenAI to extract structured campaign data from scraped content.

    Args:
        scraped_data: Dict from scrape_website() with clean_text, title, meta_description
        detected_language: Detected language code (he/en/fr)

    Returns:
        Dict with product, benefits, audience, offer fields
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    language_note = {
        'he': 'The content is in Hebrew',
        'en': 'The content is in English',
        'fr': 'The content is in French'
    }

    prompt = f"""You are a marketing data extraction assistant. Extract structured campaign information from the following website content and translate everything to Hebrew.

**Website Title:** {scraped_data.get('title', 'N/A')}

**Meta Description:** {scraped_data.get('meta_description', 'N/A')}

**Website Content:**
{scraped_data['clean_text']}

---

**Task:** Extract the following fields in JSON format and TRANSLATE all content to HEBREW. If a field cannot be found, use null.

**Output Format:**
{{
    "product": "Product or service name IN HEBREW",
    "benefits": "Key benefits and features IN HEBREW (detailed, 50-200 words)",
    "audience": "Target audience description IN HEBREW (20-100 words)",
    "offer": "Current promotional offer, discount, or call-to-action IN HEBREW"
}}

**CRITICAL INSTRUCTIONS:**
1. The website content is in {language_note.get(detected_language, 'the original language')}
2. **TRANSLATE EVERYTHING TO HEBREW** - all extracted fields must be in Hebrew (עברית)
3. For benefits: combine multiple benefits into a comprehensive paragraph IN HEBREW
4. For audience: infer from content if not explicitly stated, write IN HEBREW
5. For offer: look for promotions, discounts, special deals, CTAs and translate to HEBREW
6. If you cannot find a field, set it to null (not empty string)
7. Product names can stay in original language if they are brand names, but add Hebrew description

**Output only valid JSON with all content in Hebrew, no additional text:**
"""

    # Call OpenAI with timeout to prevent hanging
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise data extraction assistant. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000,
        timeout=30.0  # 30 second timeout to prevent indefinite hangs
    )

    # Parse JSON response
    try:
        result_text = response.choices[0].message.content.strip()

        # Remove markdown code fences if present
        if result_text.startswith('```'):
            result_text = re.sub(r'^```json?\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)

        extracted_data = json.loads(result_text)

        return {
            'product': extracted_data.get('product'),
            'benefits': extracted_data.get('benefits'),
            'audience': extracted_data.get('audience'),
            'offer': extracted_data.get('offer')
        }

    except json.JSONDecodeError:
        # Fallback: return empty data
        return {
            'product': None,
            'benefits': None,
            'audience': None,
            'offer': None
        }


def scrape_and_extract(url: str) -> WebScrapingResult:
    """
    Main entry point: scrape website and extract campaign data.

    Args:
        url: URL to scrape

    Returns:
        WebScrapingResult with extracted data or error
    """
    try:
        # Step 1: Scrape website
        scraped_data = scrape_website(url)

        # Step 2: Detect language
        combined_text = f"{scraped_data['title']} {scraped_data['meta_description']} {scraped_data['clean_text'][:500]}"
        detected_lang = detect_language(combined_text)

        # Step 3: Extract with LLM
        extracted = extract_campaign_data_with_llm(scraped_data, detected_lang)

        # Step 4: Calculate confidence
        filled_fields = sum(1 for v in extracted.values() if v and str(v).strip())
        confidence = filled_fields / 4.0

        # Step 5: Build result
        return WebScrapingResult(
            success=True,
            url=url,
            product=extracted['product'],
            benefits=extracted['benefits'],
            audience=extracted['audience'],
            offer=extracted['offer'],
            extraction_confidence=confidence,
            detected_language=detected_lang,
            error_message=None
        )

    except requests.RequestException as e:
        return WebScrapingResult(
            success=False,
            url=url,
            error_message=f"שגיאת רשת: {str(e)}"
        )

    except ValueError as e:
        return WebScrapingResult(
            success=False,
            url=url,
            error_message=str(e)
        )

    except Exception as e:
        return WebScrapingResult(
            success=False,
            url=url,
            error_message=f"שגיאה לא צפויה: {str(e)}"
        )
