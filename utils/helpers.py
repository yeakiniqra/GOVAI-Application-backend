import re
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Detect if text is primarily Bangla, English, or Banglish
    
    Args:
        text: Input text
    
    Returns:
        Language code: 'bn' for Bangla, 'en' for English
    """
    # Check for Bangla Unicode characters
    bangla_chars = len(re.findall(r'[\u0980-\u09FF]', text))
    total_chars = len(re.findall(r'[a-zA-Z\u0980-\u09FF]', text))
    
    if total_chars == 0:
        return 'en'
    
    bangla_ratio = bangla_chars / total_chars
    
    # If more than 30% Bangla characters, consider it Bangla
    if bangla_ratio > 0.3:
        return 'bn'
    else:
        return 'en'


def sanitize_query(query: str) -> str:
    """
    Sanitize and clean user query
    
    Args:
        query: Raw user query
    
    Returns:
        Cleaned query
    """
    # Remove excessive whitespace
    query = ' '.join(query.split())
    
    # Remove special characters that might cause issues
    query = re.sub(r'[<>{}[\]\\]', '', query)
    
    return query.strip()


def is_government_related(query: str) -> Tuple[bool, str]:
    """
    Check if query is related to government services
    
    Args:
        query: User query
    
    Returns:
        Tuple of (is_related, message)
    """
    # Common government-related keywords in multiple languages
    gov_keywords = [
        # English
        'passport', 'visa', 'nid', 'birth certificate', 'government', 'ministry',
        'license', 'tax', 'citizen', 'application', 'registration', 'certificate',
        
        # Bangla (transliterated)
        'পাসপোর্ট', 'ভিসা', 'জাতীয় পরিচয়পত্র', 'জন্ম নিবন্ধন', 'সরকার', 'মন্ত্রণালয়',
        'লাইসেন্স', 'কর', 'নাগরিক', 'আবেদন', 'নিবন্ধন', 'সনদ',
        
        # Common Banglish
        'passport', 'nid', 'birth', 'license', 'tax'
    ]
    
    query_lower = query.lower()
    
    for keyword in gov_keywords:
        if keyword.lower() in query_lower:
            return True, "সরকারি সেবা সংক্রান্ত প্রশ্ন সনাক্ত করা হয়েছে"
    
    # If not clearly government-related, still process but with a note
    return False, "সাধারণ প্রশ্ন - সরকারি প্রেক্ষাপট যোগ করা হচ্ছে"


def format_processing_time(seconds: float) -> str:
    """
    Format processing time in human-readable format
    
    Args:
        seconds: Processing time in seconds
    
    Returns:
        Formatted time string
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    else:
        return f"{seconds:.2f}s"


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Input text
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."


def humanize_response(text: str) -> str:
    """
    Make AI response more human-friendly
    
    Args:
        text: Raw AI response
    
    Returns:
        Humanized response
    """
    # Basic cleanup
    text = text.strip()
    
    # Ensure proper punctuation
    if not text.endswith(('.', '!', '?')):
        text += '.'
    
    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:]
    
    return text