"""
Output Encoding for XSS Prevention - OWASP A03:2021 Injection Defense

This module provides comprehensive output encoding for the CORTEX dashboard
to prevent Cross-Site Scripting (XSS) attacks. Implements OWASP recommendations
for contextual output encoding.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

import html
import json
import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, quote_plus
import logging

logger = logging.getLogger(__name__)


class OutputEncoder:
    """
    Multi-context output encoder following OWASP XSS Prevention Cheat Sheet.
    
    Supports encoding for:
    - HTML content (body text, attributes)
    - JavaScript contexts (strings, JSON data)
    - URL contexts (query parameters, paths)
    - CSS contexts (style attributes)
    """
    
    # XSS-dangerous HTML characters
    HTML_ENTITIES = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;',
    }
    
    # JavaScript special characters requiring escaping
    JS_ESCAPE_CHARS = {
        '\\': '\\\\',
        '"': '\\"',
        "'": "\\'",
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '\b': '\\b',
        '\f': '\\f',
        '\v': '\\v',
        '\0': '\\0',
        '\u2028': '\\u2028',  # Line separator
        '\u2029': '\\u2029',  # Paragraph separator
    }
    
    # Dangerous URL patterns
    DANGEROUS_URL_PATTERNS = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
        r'about:',
    ]
    
    @staticmethod
    def encode_html(text: str) -> str:
        """
        Encode text for safe output in HTML body context.
        
        Use this for user-generated content displayed in HTML elements.
        
        Args:
            text: Raw user input or untrusted data
            
        Returns:
            HTML-encoded safe string
            
        Example:
            >>> encode_html("<script>alert('XSS')</script>")
            "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;"
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Use html.escape (Python standard library)
        # Note: html.escape by default only escapes &, <, >, but not quotes
        # We need to explicitly escape quotes for attribute context safety
        encoded = html.escape(text, quote=True)
        
        # Additional escaping for forward slash (prevents </script> injection)
        encoded = encoded.replace('/', '&#x2F;')
        
        return encoded
    
    @staticmethod
    def encode_html_attribute(text: str) -> str:
        """
        Encode text for safe output in HTML attribute context.
        
        Use this for values in HTML attributes like id, class, data-*, etc.
        
        Args:
            text: Raw user input for attribute value
            
        Returns:
            Attribute-safe encoded string
            
        Example:
            >>> encode_html_attribute('"><script>alert(1)</script>')
            '&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;'
        """
        if not isinstance(text, str):
            text = str(text)
        
        # More aggressive encoding for attribute context
        result = ''
        for char in text:
            if char in OutputEncoder.HTML_ENTITIES:
                result += OutputEncoder.HTML_ENTITIES[char]
            elif ord(char) < 32 or ord(char) > 126:
                # Encode non-printable and non-ASCII
                result += f'&#x{ord(char):02x};'
            else:
                result += char
        
        return result
    
    @staticmethod
    def encode_javascript(text: str) -> str:
        """
        Encode text for safe output in JavaScript string context.
        
        Use this when embedding user data in JS strings or JSON values.
        
        Args:
            text: Raw user input for JavaScript context
            
        Returns:
            JavaScript-escaped safe string
            
        Example:
            >>> encode_javascript("'; alert('XSS'); //")
            "\\'; alert(\\'XSS\\'); //"
        """
        if not isinstance(text, str):
            text = str(text)
        
        result = ''
        for char in text:
            if char in OutputEncoder.JS_ESCAPE_CHARS:
                result += OutputEncoder.JS_ESCAPE_CHARS[char]
            elif ord(char) < 32 or ord(char) > 126:
                # Unicode escape for non-ASCII
                result += f'\\u{ord(char):04x}'
            else:
                result += char
        
        return result
    
    @staticmethod
    def encode_json(data: Any) -> str:
        """
        Encode Python object as safe JSON for embedding in HTML.
        
        Uses json.dumps with ensure_ascii=True to prevent encoding issues.
        Additionally escapes < > & to prevent script injection via JSON.
        
        Args:
            data: Python object (dict, list, str, int, etc.)
            
        Returns:
            JSON string safe for embedding in HTML <script> tags
            
        Example:
            >>> encode_json({'name': '<script>alert(1)</script>'})
            '{"name": "\\u003cscript\\u003ealert(1)\\u003c/script\\u003e"}'
        """
        # Standard JSON encoding with ASCII safety
        json_str = json.dumps(data, ensure_ascii=True, separators=(',', ':'))
        
        # Additional HTML context escaping
        json_str = json_str.replace('<', '\\u003c')
        json_str = json_str.replace('>', '\\u003e')
        json_str = json_str.replace('&', '\\u0026')
        
        return json_str
    
    @staticmethod
    def encode_url(text: str, plus_safe: bool = False) -> str:
        """
        Encode text for safe use in URL contexts.
        
        Args:
            text: Raw text for URL encoding
            plus_safe: If True, use quote_plus (space → +), else quote (space → %20)
            
        Returns:
            URL-encoded safe string
            
        Example:
            >>> encode_url("search?q=<script>")
            "search%3Fq%3D%3Cscript%3E"
        """
        if not isinstance(text, str):
            text = str(text)
        
        if plus_safe:
            return quote_plus(text, safe='')
        else:
            return quote(text, safe='')
    
    @staticmethod
    def sanitize_url(url: str) -> Optional[str]:
        """
        Validate and sanitize URLs to prevent javascript:, data:, and other dangerous protocols.
        
        Args:
            url: URL string to validate
            
        Returns:
            Sanitized URL if safe, None if dangerous
            
        Example:
            >>> sanitize_url("javascript:alert(1)")
            None
            >>> sanitize_url("https://example.com/page?id=123")
            "https://example.com/page?id=123"
        """
        if not isinstance(url, str):
            return None
        
        url_lower = url.lower().strip()
        
        # Check for dangerous protocols
        for pattern in OutputEncoder.DANGEROUS_URL_PATTERNS:
            if re.match(pattern, url_lower):
                logger.warning(f"Blocked dangerous URL protocol: {url}")
                return None
        
        # Allow only http, https, mailto, and relative URLs
        if url_lower.startswith(('http://', 'https://', 'mailto:', '/', '#')):
            return url
        
        # If no protocol, assume relative URL (safe)
        if not re.match(r'^\w+:', url):
            return url
        
        logger.warning(f"Blocked non-whitelisted URL protocol: {url}")
        return None
    
    @staticmethod
    def encode_css(text: str) -> str:
        """
        Encode text for safe output in CSS context (style attributes).
        
        Args:
            text: Raw text for CSS context
            
        Returns:
            CSS-escaped safe string
            
        Example:
            >>> encode_css("expression(alert('XSS'))")
            "expression\\28 alert\\28 \\'XSS\\'\\29 \\29 "
        """
        if not isinstance(text, str):
            text = str(text)
        
        result = ''
        for char in text:
            # Escape all non-alphanumeric characters
            if not char.isalnum():
                result += f'\\{ord(char):02x} '
            else:
                result += char
        
        return result
    
    @staticmethod
    def safe_format_html(template: str, **kwargs: Any) -> str:
        """
        Format HTML template with auto-escaping of all variables.
        
        Args:
            template: HTML template with {variable} placeholders
            **kwargs: Variables to substitute (all auto-escaped)
            
        Returns:
            Formatted HTML with escaped variables
            
        Example:
            >>> safe_format_html("<div>{name}</div>", name="<script>alert(1)</script>")
            "<div>&lt;script&gt;alert(1)&lt;/script&gt;</div>"
        """
        # Escape all kwargs
        escaped_kwargs = {
            key: OutputEncoder.encode_html(str(value))
            for key, value in kwargs.items()
        }
        
        return template.format(**escaped_kwargs)


class Jinja2SecurityExtension:
    """
    Security extensions for Jinja2 templates used in CORTEX dashboard.
    
    Provides additional filters for contextual output encoding beyond
    Jinja2's default autoescaping.
    """
    
    @staticmethod
    def get_filters() -> Dict[str, callable]:
        """
        Get dictionary of custom Jinja2 filters for security.
        
        Returns:
            Dict of filter_name → filter_function
            
        Usage in template:
            {{ user_input | js_escape }}
            {{ url_param | url_encode }}
            {{ json_data | json_safe }}
        """
        return {
            'js_escape': OutputEncoder.encode_javascript,
            'url_encode': OutputEncoder.encode_url,
            'json_safe': OutputEncoder.encode_json,
            'css_escape': OutputEncoder.encode_css,
            'sanitize_url': OutputEncoder.sanitize_url,
        }
    
    @staticmethod
    def configure_jinja_env(jinja_env):
        """
        Configure Jinja2 environment with security filters and settings.
        
        Args:
            jinja_env: Jinja2 Environment instance
            
        Returns:
            Configured environment (mutates in-place)
        """
        # Enable autoescape for HTML by default
        jinja_env.autoescape = True
        
        # Add custom filters
        jinja_env.filters.update(Jinja2SecurityExtension.get_filters())
        
        # Add global functions
        jinja_env.globals['safe_json'] = OutputEncoder.encode_json
        
        logger.info("Jinja2 environment configured with XSS prevention filters")
        
        return jinja_env


# Convenience functions for common use cases
def safe_html(text: str) -> str:
    """Shorthand for encode_html()"""
    return OutputEncoder.encode_html(text)


def safe_js(text: str) -> str:
    """Shorthand for encode_javascript()"""
    return OutputEncoder.encode_javascript(text)


def safe_url(text: str) -> str:
    """Shorthand for encode_url()"""
    return OutputEncoder.encode_url(text)


def safe_json(data: Any) -> str:
    """Shorthand for encode_json()"""
    return OutputEncoder.encode_json(data)


# Example usage patterns for dashboard integration
if __name__ == '__main__':
    # Test basic encoding
    xss_payload = "<script>alert('XSS')</script>"
    
    print("HTML Context:")
    print(f"  Input:  {xss_payload}")
    print(f"  Output: {safe_html(xss_payload)}")
    print()
    
    print("JavaScript Context:")
    js_payload = "'; alert('XSS'); //"
    print(f"  Input:  {js_payload}")
    print(f"  Output: {safe_js(js_payload)}")
    print()
    
    print("URL Context:")
    url_payload = "page?q=<script>alert(1)</script>"
    print(f"  Input:  {url_payload}")
    print(f"  Output: {safe_url(url_payload)}")
    print()
    
    print("JSON Context:")
    json_payload = {'name': '<script>alert(1)</script>', 'id': 123}
    print(f"  Input:  {json_payload}")
    print(f"  Output: {safe_json(json_payload)}")
    print()
    
    print("URL Sanitization:")
    dangerous_urls = [
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "https://example.com/safe",
        "vbscript:msgbox(1)"
    ]
    for url in dangerous_urls:
        result = OutputEncoder.sanitize_url(url)
        print(f"  {url} → {result}")
