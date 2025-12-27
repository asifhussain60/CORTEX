"""
CORTEX Native HTML Toolkit
Pure Python HTML validation, generation, and manipulation tools

Author: Asif Hussain
Date: December 27, 2025
"""

from .validator import HTMLValidator, validate_file, validate_directory
from .generator import HTMLGenerator, create_html_document

__all__ = [
    'HTMLValidator',
    'validate_file', 
    'validate_directory',
    'HTMLGenerator',
    'create_html_document'
]

__version__ = '1.0.0'
