import re
from typing import Optional


def validate_username(username: str) -> bool:
    """Validate username format"""
    # Username should be 3-50 characters, alphanumeric and underscore only
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return bool(re.match(pattern, username))


def validate_password(password: str) -> bool:
    """Validate password strength"""
    # Password should be at least 8 characters
    if len(password) < 8:
        return False
    
    # Should contain at least one letter and one number
    has_letter = re.search(r'[a-zA-Z]', password)
    has_number = re.search(r'\d', password)
    
    return bool(has_letter and has_number)


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS"""
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text.strip() 