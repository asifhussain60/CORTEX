"""
Formatters Module
CQ-07: Brittle string operations, no validation
"""
import re

def format_phone_number(phone):
    """
    CQ-07: Brittle string operations (FLAW)
    No validation, will crash on invalid input
    """
    # Assumes specific format, breaks easily
    return f"({phone[0:3]}) {phone[3:6]}-{phone[6:10]}"

def format_credit_card(number):
    """Brittle formatting"""
    # No validation, assumes 16 digits
    return f"{number[0:4]}-{number[4:8]}-{number[8:12]}-{number[12:16]}"

def format_address(street, city, state, zip_code):
    """Brittle string concatenation"""
    # No null checks, will fail on None values
    return f"{street}, {city}, {state} {zip_code}"

# PERF-06: Regex compilation in loop would happen in calling code
def format_list(items, pattern):
    """Inefficient regex usage"""
    formatted = []
    for item in items:
        # If this is called in a loop, regex is recompiled each time
        regex = re.compile(pattern)  # Should compile once outside loop
        formatted.append(regex.sub('', item))
    return formatted
