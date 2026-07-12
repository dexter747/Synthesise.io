"""
Helper utilities for Synthesize.io API.
"""
import re
import uuid
import secrets
from datetime import datetime, date
from typing import Optional, Any, List


def generate_slug(text: str, max_length: int = 100) -> str:
    """
    Generate a URL-safe slug from text.
    
    Args:
        text: Text to convert to slug
        max_length: Maximum length of the slug
    
    Returns:
        URL-safe slug
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)
    
    # Remove special characters
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Truncate to max length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    # Ensure minimum length
    if len(slug) < 3:
        slug = slug + '-' + secrets.token_hex(4)
    
    return slug


def generate_unique_slug(text: str, existing_slugs: List[str], max_length: int = 100) -> str:
    """
    Generate a unique slug by appending numbers if necessary.
    
    Args:
        text: Text to convert to slug
        existing_slugs: List of existing slugs to avoid
        max_length: Maximum length of the slug
    
    Returns:
        Unique URL-safe slug
    """
    base_slug = generate_slug(text, max_length - 4)  # Leave room for suffix
    
    if base_slug not in existing_slugs:
        return base_slug
    
    # Append numbers until unique
    counter = 1
    while True:
        slug = f"{base_slug}-{counter}"
        if slug not in existing_slugs:
            return slug
        counter += 1
        if counter > 999:
            # Fallback to random suffix
            return f"{base_slug}-{secrets.token_hex(4)}"


def generate_invoice_number(prefix: str = "INV") -> str:
    """
    Generate a unique invoice number.
    
    Format: INV-YYYYMMDD-XXXXX
    """
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = secrets.token_hex(3).upper()
    return f"{prefix}-{date_part}-{random_part}"


def generate_ticket_number(prefix: str = "TKT") -> str:
    """
    Generate a unique support ticket number.
    
    Format: TKT-XXXXXX
    """
    random_part = secrets.token_hex(3).upper()
    return f"{prefix}-{random_part}"


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable string.
    
    Examples:
        1024 -> "1.00 KB"
        1048576 -> "1.00 MB"
    """
    if bytes_value < 0:
        return "Unlimited"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if abs(bytes_value) < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    
    return f"{bytes_value:.2f} EB"


def format_number(number: int) -> str:
    """
    Format number with thousand separators.
    
    Examples:
        1000 -> "1,000"
        1000000 -> "1,000,000"
    """
    if number < 0:
        return "Unlimited"
    return f"{number:,}"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to max length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: String to append when truncated
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def mask_email(email: str) -> str:
    """
    Mask an email address for display.
    
    Examples:
        user@example.com -> u***@example.com
        john.doe@company.org -> j***e@company.org
    """
    if '@' not in email:
        return email
    
    local, domain = email.rsplit('@', 1)
    
    if len(local) <= 2:
        masked_local = local[0] + '***'
    else:
        masked_local = local[0] + '***' + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_api_key(key: str) -> str:
    """
    Mask an API key for display.
    
    Examples:
        sk_test_abc123xyz789 -> sk_test_abc...789
    """
    if len(key) <= 12:
        return key[:4] + '...'
    
    return key[:10] + '...' + key[-4:]


def parse_user_agent(user_agent: str) -> dict:
    """
    Parse user agent string into device info.
    
    Returns:
        Dictionary with browser, os, and device info
    """
    info = {
        "browser": "Unknown",
        "os": "Unknown",
        "device": "Unknown",
        "raw": user_agent[:500] if user_agent else None,
    }
    
    if not user_agent:
        return info
    
    user_agent_lower = user_agent.lower()
    
    # Detect browser
    if 'chrome' in user_agent_lower and 'edge' not in user_agent_lower:
        info["browser"] = "Chrome"
    elif 'firefox' in user_agent_lower:
        info["browser"] = "Firefox"
    elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
        info["browser"] = "Safari"
    elif 'edge' in user_agent_lower:
        info["browser"] = "Edge"
    elif 'opera' in user_agent_lower or 'opr' in user_agent_lower:
        info["browser"] = "Opera"
    
    # Detect OS
    if 'windows' in user_agent_lower:
        info["os"] = "Windows"
    elif 'mac os' in user_agent_lower or 'macos' in user_agent_lower:
        info["os"] = "macOS"
    elif 'linux' in user_agent_lower:
        info["os"] = "Linux"
    elif 'android' in user_agent_lower:
        info["os"] = "Android"
    elif 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
        info["os"] = "iOS"
    
    # Detect device type
    if 'mobile' in user_agent_lower or 'android' in user_agent_lower or 'iphone' in user_agent_lower:
        info["device"] = "Mobile"
    elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
        info["device"] = "Tablet"
    else:
        info["device"] = "Desktop"
    
    return info


def calculate_pagination(
    total: int,
    page: int = 1,
    per_page: int = 20,
    max_per_page: int = 100
) -> dict:
    """
    Calculate pagination metadata.
    
    Args:
        total: Total number of items
        page: Current page (1-indexed)
        per_page: Items per page
        max_per_page: Maximum items per page
    
    Returns:
        Pagination metadata
    """
    # Enforce limits
    per_page = min(max(1, per_page), max_per_page)
    page = max(1, page)
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    # Adjust page if out of bounds
    page = min(page, total_pages)
    
    offset = (page - 1) * per_page
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "offset": offset,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries.
    
    Values in override take precedence.
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def get_date_range(period: str) -> tuple:
    """
    Get date range for common periods.
    
    Args:
        period: "today", "yesterday", "last_7_days", "last_30_days", "this_month", "last_month"
    
    Returns:
        Tuple of (start_date, end_date)
    """
    today = date.today()
    
    if period == "today":
        return today, today
    
    elif period == "yesterday":
        yesterday = today.replace(day=today.day - 1)
        return yesterday, yesterday
    
    elif period == "last_7_days":
        start = today.replace(day=today.day - 6)
        return start, today
    
    elif period == "last_30_days":
        start = today.replace(day=today.day - 29)
        return start, today
    
    elif period == "this_month":
        start = today.replace(day=1)
        return start, today
    
    elif period == "last_month":
        first_of_this_month = today.replace(day=1)
        last_of_last_month = first_of_this_month.replace(day=first_of_this_month.day - 1)
        first_of_last_month = last_of_last_month.replace(day=1)
        return first_of_last_month, last_of_last_month
    
    else:
        raise ValueError(f"Unknown period: {period}")
