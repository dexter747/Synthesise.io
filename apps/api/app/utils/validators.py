"""
Input validation utilities for Synthesize.io API.
"""
import re
from typing import Optional, List, Tuple
from email_validator import validate_email as email_validator_check, EmailNotValidError


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an email address.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Validate and normalize
        email_info = email_validator_check(email, check_deliverability=False)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)


def validate_password(password: str) -> Tuple[bool, List[str]]:
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character (optional but recommended)
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number")
    
    # Optional: special character (warning, not error)
    # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
    #     warnings.append("Consider adding a special character for stronger security")
    
    return len(errors) == 0, errors


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a URL.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if url_pattern.match(url):
        return True, None
    return False, "Invalid URL format"


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a phone number (basic validation).
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it starts with + (international format) or is just digits
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    if not cleaned.isdigit():
        return False, "Phone number must contain only digits"
    
    if len(cleaned) < 10 or len(cleaned) > 15:
        return False, "Phone number must be between 10 and 15 digits"
    
    return True, None


def validate_slug(slug: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a URL slug.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not slug:
        return False, "Slug cannot be empty"
    
    if len(slug) < 3:
        return False, "Slug must be at least 3 characters"
    
    if len(slug) > 100:
        return False, "Slug must be at most 100 characters"
    
    # Only lowercase letters, numbers, and hyphens
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', slug):
        return False, "Slug must contain only lowercase letters, numbers, and hyphens"
    
    # No consecutive hyphens
    if '--' in slug:
        return False, "Slug cannot contain consecutive hyphens"
    
    return True, None


def validate_row_count(count: int, max_allowed: int = -1) -> Tuple[bool, Optional[str]]:
    """
    Validate requested row count.
    
    Args:
        count: Requested number of rows
        max_allowed: Maximum allowed (-1 for unlimited)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if count < 1:
        return False, "Row count must be at least 1"
    
    if max_allowed > 0 and count > max_allowed:
        return False, f"Row count exceeds maximum allowed ({max_allowed:,})"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe storage.
    
    Removes/replaces potentially dangerous characters.
    """
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Replace other problematic characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    
    # Limit length
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if len(name) > 200:
        name = name[:200]
    
    return f"{name}.{ext}" if ext else name


def validate_json_schema(schema: dict) -> Tuple[bool, Optional[str]]:
    """
    Basic validation of a data schema definition.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(schema, dict):
        return False, "Schema must be a dictionary"
    
    if "columns" not in schema and "fields" not in schema:
        return False, "Schema must contain 'columns' or 'fields'"
    
    columns = schema.get("columns") or schema.get("fields", [])
    
    if not isinstance(columns, list):
        return False, "Columns must be a list"
    
    if len(columns) == 0:
        return False, "Schema must have at least one column"
    
    for i, col in enumerate(columns):
        if not isinstance(col, dict):
            return False, f"Column {i} must be a dictionary"
        
        if "name" not in col:
            return False, f"Column {i} must have a 'name'"
        
        if "type" not in col:
            return False, f"Column {i} must have a 'type'"
    
    return True, None
