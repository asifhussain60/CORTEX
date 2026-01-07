"""
Helpers Module - God Object
SOL-07: 500+ lines, mixed responsibilities
CQ-03: Dead code (unused functions)
CQ-08: Magic numbers (no constants)
"""
import re
import json
from datetime import datetime

# SOL-07: This is a GOD OBJECT - too many responsibilities (FLAW)
# Should be split into: StringHelpers, DateHelpers, ValidationHelpers, etc.

def validate_email(email):
    """Email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Phone validation"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def format_currency(amount):
    """Format currency"""
    # CQ-08: Magic number 2 (FLAW)
    return f"${amount:.2f}"

def format_date(date):
    """Format date"""
    return date.strftime('%Y-%m-%d')

def parse_date(date_str):
    """Parse date string"""
    return datetime.strptime(date_str, '%Y-%m-%d')

def sanitize_input(text):
    """Sanitize user input"""
    # CQ-07: Brittle string operations (FLAW)
    return text.replace('<', '').replace('>', '').replace('script', '')

def calculate_tax(amount, region):
    """Calculate tax"""
    # CQ-08: Magic numbers (FLAW)
    if region == 'US':
        return amount * 0.08  # Magic number
    elif region == 'EU':
        return amount * 0.20  # Magic number
    return amount * 0.15  # Magic number

def calculate_discount(price, discount_type):
    """Calculate discount"""
    # CQ-08: More magic numbers (FLAW)
    if discount_type == 'percentage':
        return price * 0.10
    return 5.00  # Magic number

def generate_random_string(length):
    """Generate random string"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters, k=length))

def hash_string(text):
    """Hash string"""
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()

# CQ-03: Dead code - unused functions (FLAW)
def old_validation_method(data):
    """This function is never called anywhere"""
    return True

def deprecated_formatter(text):
    """Deprecated but never removed"""
    return text.upper()

def unused_calculator(a, b):
    """Never used"""
    return a + b

def legacy_parser(data):
    """Old parsing logic, replaced but not deleted"""
    return json.loads(data)

def obsolete_converter(value):
    """No longer needed"""
    return str(value)

def old_validator(item):
    """Replaced by new validator"""
    return len(item) > 0

def deprecated_helper(x, y):
    """Not used since v0.5"""
    return x * y

def unused_utility_function(param):
    """Dead code"""
    pass

# More mixed responsibilities (FLAW)
def send_email(to, subject, body):
    """Email sending - wrong place"""
    print(f"Sending email to {to}")
    return True

def log_event(event):
    """Logging - wrong place"""
    print(f"Event: {event}")

def cache_result(key, value):
    """Caching - wrong place"""
    # Should use cache module
    pass

def make_http_request(url):
    """HTTP requests - wrong place"""
    import requests
    return requests.get(url)

def process_file_upload(file):
    """File processing - wrong place"""
    return file.save('/tmp/upload')

def generate_pdf(data):
    """PDF generation - wrong place"""
    return b'PDF content'

def compress_data(data):
    """Compression - wrong place"""
    import gzip
    return gzip.compress(data.encode())

def encrypt_data(data):
    """Encryption - wrong place"""
    # Should be in security module
    return data[::-1]  # Terrible encryption

def parse_xml(xml_string):
    """XML parsing - wrong place"""
    return {}

def generate_uuid():
    """UUID generation - wrong place"""
    import uuid
    return str(uuid.uuid4())

# PERF-05: Unnecessary list copies (FLAW)
def filter_items(items, condition):
    """Creates unnecessary copies"""
    temp_list = items.copy()  # Unnecessary copy
    filtered = []
    for item in temp_list:
        if condition(item):
            filtered.append(item)
    return filtered.copy()  # Another unnecessary copy

def transform_data(data):
    """More unnecessary copies"""
    result = data.copy()
    result = [x * 2 for x in result]
    return result.copy()  # Yet another copy

# Continue to reach 500+ lines with more dead code...
def another_unused_function():
    """More dead code"""
    pass

def yet_another_unused():
    """Even more dead code"""
    pass

def completely_useless():
    """Padding to reach 500+ lines"""
    pass

# Add many more similar functions to reach target line count
# This demonstrates the god object anti-pattern
