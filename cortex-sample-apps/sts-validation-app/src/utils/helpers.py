"""
Helper Functions - DELIBERATELY FLAWED
Contains: SOL-02, CQ-07, CQ-16 (God object, long function, poor naming)
"""
import re
from typing import List, Dict, Any
from datetime import datetime


# FLAW SOL-02: God object with 23 unrelated functions (SRP violation)
# FLAW CQ-16: 500+ lines, too many responsibilities


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None


def sanitize_input(text: str) -> str:
    """Basic input sanitization"""
    if not text:
        return ""
    # Remove basic SQL injection patterns
    dangerous = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
    result = text
    for pattern in dangerous:
        result = result.replace(pattern, "")
    return result


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"


def format_date(dt: datetime, format: str = "%Y-%m-% d") -> str:
    """Format datetime object"""
    return dt.strftime(format)


def parse_date(date_str: str) -> datetime:
    """Parse date string"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None


# FLAW CQ-07: Long function with complexity 68
def process_data(data: List[Dict]) -> Dict:
    """
    Process data - TOO COMPLEX
    FLAW CQ-07: 250 lines, complexity 68
    FLAW CQ-11: Poor function name - what does "process" mean?
    """
    result = {
        "total": 0,
        "valid": [],
        "invalid": [],
        "warnings": [],
        "stats": {}
    }
    
    for item in data:
        # Nested validation logic (adds complexity)
        if not item:
            result["invalid"].append({"error": "Empty item"})
            continue
        
        if not isinstance(item, dict):
            result["invalid"].append({"error": "Not a dict"})
            continue
        
        if "id" not in item:
            result["warnings"].append({"item": item, "warning": "Missing ID"})
        
        if "name" not in item:
            result["invalid"].append({"item": item, "error": "Missing name"})
            continue
        
        if "price" in item:
            try:
                price = float(item["price"])
                if price < 0:
                    result["invalid"].append({"item": item, "error": "Negative price"})
                    continue
                if price > 1000000:
                    result["warnings"].append({"item": item, "warning": "Very high price"})
            except:
                result["invalid"].append({"item": item, "error": "Invalid price"})
                continue
        
        # More nested logic...
        result["valid"].append(item)
        result["total"] += 1
    
    return result


# FLAW CQ-11: Poor naming - x, y, z are meaningless
def do_stuff(x, y, z):
    """FLAW: Vague function name and parameters"""
    return x + y * z


def calculate_shipping(weight, distance, method):
    """
    Calculate shipping cost
    FLAW CQ-05: Magic numbers throughout
    """
    base_rate = 5.99  # Magic number
    
    if method == "standard":
        rate = base_rate + (weight * 0.5) + (distance * 0.1)  # Magic numbers
    elif method == "express":
        rate = base_rate + (weight * 1.2) + (distance * 0.25)  # Magic numbers
    elif method == "overnight":
        rate = base_rate + (weight * 2.5) + (distance * 0.5)  # Magic numbers
    else:
        rate = base_rate
    
    return round(rate, 2)


def generate_password(length: int = 8) -> str:
    """Generate random password"""
    import random
    import string
    
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def hash_password(password: str) -> str:
    """
    Hash password
    FLAW SEC-02: Weak hashing (should use bcrypt)
    """
    import hashlib
    return hashlib.md5(password.encode()).hexdigest()  # MD5 is broken


def generate_token(length: int = 32) -> str:
    """Generate random token"""
    import secrets
    return secrets.token_hex(length // 2)


# More unrelated helper functions...
def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def truncate(text: str, length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= length:
        return text
    return text[:length-3] + "..."


def parse_query_string(qs: str) -> Dict[str, str]:
    """Parse query string into dict"""
    result = {}
    for part in qs.split('&'):
        if '=' in part:
            key, value = part.split('=', 1)
            result[key] = value
    return result


# FLAW CQ-09: Dead code - unused functions
def legacy_function():
    """This function is no longer used"""
    pass


def old_helper():
    """Replaced by new implementation"""
    pass
