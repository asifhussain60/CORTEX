"""
Tests for Output Encoding Module - XSS Prevention Validation

Validates all encoding contexts and OWASP compliance.

Author: Asif Hussain
Created: 2025-11-30
"""

import pytest
import json
from src.dashboard.security.output_encoder import (
    OutputEncoder,
    Jinja2SecurityExtension,
    safe_html,
    safe_js,
    safe_url,
    safe_json
)


class TestHTMLEncoding:
    """Test HTML context encoding (OWASP: HTML Body Context)"""
    
    def test_basic_html_entities(self):
        """Test encoding of dangerous HTML characters"""
        assert OutputEncoder.encode_html("<script>") == "&lt;script&gt;"
        assert OutputEncoder.encode_html("&") == "&amp;"
        assert OutputEncoder.encode_html('"') == "&quot;"
        assert OutputEncoder.encode_html("'") == "&#x27;"
    
    def test_script_tag_injection(self):
        """Test prevention of <script> injection"""
        payload = "<script>alert('XSS')</script>"
        encoded = OutputEncoder.encode_html(payload)
        
        assert "<script>" not in encoded
        assert "&lt;script&gt;" in encoded
        assert "&#x27;" in encoded  # Single quote escaped
    
    def test_event_handler_injection(self):
        """Test prevention of event handler injection"""
        payload = '<img src=x onerror="alert(1)">'
        encoded = OutputEncoder.encode_html(payload)
        
        assert "<img" not in encoded
        assert "&lt;img" in encoded
        assert '&quot;' in encoded
    
    def test_forward_slash_escape(self):
        """Test that forward slashes are escaped (prevents </script> breakout)"""
        payload = "</script><script>alert(1)</script>"
        encoded = OutputEncoder.encode_html(payload)
        
        assert "/" not in encoded
        assert "&#x2F;" in encoded
    
    def test_non_string_input(self):
        """Test encoding of non-string inputs"""
        assert OutputEncoder.encode_html(123) == "123"
        assert OutputEncoder.encode_html(None) == "None"
        assert OutputEncoder.encode_html(True) == "True"
    
    def test_unicode_preservation(self):
        """Test that Unicode characters are preserved correctly"""
        text = "Hello 世界 🌍"
        encoded = OutputEncoder.encode_html(text)
        
        # Unicode should be preserved (not entity-encoded)
        assert "世界" in encoded
        assert "🌍" in encoded
    
    def test_empty_string(self):
        """Test encoding of empty string"""
        assert OutputEncoder.encode_html("") == ""
    
    def test_safe_html_shorthand(self):
        """Test convenience function"""
        assert safe_html("<script>") == "&lt;script&gt;"


class TestHTMLAttributeEncoding:
    """Test HTML attribute context encoding"""
    
    def test_quote_breaking(self):
        """Test prevention of quote-based attribute breakout"""
        payload = '"><script>alert(1)</script>'
        encoded = OutputEncoder.encode_html_attribute(payload)
        
        assert '"' not in encoded
        assert "&quot;" in encoded
        assert "&lt;script&gt;" in encoded
    
    def test_single_quote_breaking(self):
        """Test prevention of single-quote attribute breakout"""
        payload = "'><script>alert(1)</script>"
        encoded = OutputEncoder.encode_html_attribute(payload)
        
        assert "'" not in encoded
        assert "&#x27;" in encoded
    
    def test_non_printable_characters(self):
        """Test encoding of non-printable ASCII"""
        # Null byte, tab, newline
        payload = "\x00\t\n"
        encoded = OutputEncoder.encode_html_attribute(payload)
        
        assert "&#x00;" in encoded
        assert "&#x09;" in encoded  # Tab
        assert "&#x0a;" in encoded  # Newline
    
    def test_high_ascii_characters(self):
        """Test encoding of characters > 126"""
        payload = "test\x7f\x80\xff"
        encoded = OutputEncoder.encode_html_attribute(payload)
        
        # Characters outside printable ASCII should be hex-encoded
        assert "&#x7f;" in encoded
        assert "&#x80;" in encoded
        assert "&#xff;" in encoded


class TestJavaScriptEncoding:
    """Test JavaScript string context encoding"""
    
    def test_quote_escaping(self):
        """Test escaping of quotes in JS strings"""
        assert OutputEncoder.encode_javascript("'") == "\\'"
        assert OutputEncoder.encode_javascript('"') == '\\"'
    
    def test_script_breakout(self):
        """Test prevention of script breakout via string injection"""
        payload = "'; alert('XSS'); //"
        encoded = OutputEncoder.encode_javascript(payload)
        
        assert "\\'" in encoded
        assert encoded.count("\\'") == 3  # Three single quotes escaped (initial, inside XSS, final)
        assert ";" in encoded  # Semicolon not escaped (safe in string)
    
    def test_backslash_escaping(self):
        """Test that backslashes are properly escaped"""
        assert OutputEncoder.encode_javascript("\\") == "\\\\"
    
    def test_control_characters(self):
        """Test encoding of control characters"""
        assert OutputEncoder.encode_javascript("\n") == "\\n"
        assert OutputEncoder.encode_javascript("\r") == "\\r"
        assert OutputEncoder.encode_javascript("\t") == "\\t"
        assert OutputEncoder.encode_javascript("\b") == "\\b"
        assert OutputEncoder.encode_javascript("\f") == "\\f"
        assert OutputEncoder.encode_javascript("\v") == "\\v"
        assert OutputEncoder.encode_javascript("\0") == "\\0"
    
    def test_line_terminators(self):
        """Test encoding of Unicode line terminators (prevent breakout)"""
        assert OutputEncoder.encode_javascript("\u2028") == "\\u2028"
        assert OutputEncoder.encode_javascript("\u2029") == "\\u2029"
    
    def test_non_ascii_unicode(self):
        """Test Unicode escape for non-ASCII characters"""
        encoded = OutputEncoder.encode_javascript("世界")
        
        # Should be Unicode-escaped
        assert "\\u4e16" in encoded  # 世
        assert "\\u754c" in encoded  # 界
    
    def test_safe_js_shorthand(self):
        """Test convenience function"""
        assert safe_js("'test'") == "\\'test\\'"


class TestJSONEncoding:
    """Test JSON encoding for HTML embedding"""
    
    def test_basic_json_encoding(self):
        """Test standard JSON encoding"""
        data = {'name': 'John', 'age': 30}
        encoded = OutputEncoder.encode_json(data)
        
        # Should be valid JSON
        assert json.loads(encoded) == data
    
    def test_script_tag_in_json(self):
        """Test that <script> tags in JSON are escaped for HTML context"""
        data = {'payload': '<script>alert(1)</script>'}
        encoded = OutputEncoder.encode_json(data)
        
        # < and > should be Unicode-escaped
        assert "\\u003cscript\\u003e" in encoded
        assert "\\u003c/script\\u003e" in encoded
        assert "<script>" not in encoded
    
    def test_ampersand_escaping(self):
        """Test that & is escaped to prevent HTML entity confusion"""
        data = {'text': 'A & B'}
        encoded = OutputEncoder.encode_json(data)
        
        assert "\\u0026" in encoded
        assert "&" not in encoded
    
    def test_json_with_unicode(self):
        """Test JSON encoding with Unicode (should use ensure_ascii)"""
        data = {'text': '世界'}
        encoded = OutputEncoder.encode_json(data)
        
        # Should be ASCII-safe (Unicode escaped)
        assert "\\u" in encoded
        assert "世界" not in encoded
    
    def test_nested_json(self):
        """Test complex nested JSON structures"""
        data = {
            'users': [
                {'name': '<script>alert(1)</script>', 'id': 1},
                {'name': 'Safe Name', 'id': 2}
            ],
            'meta': {'count': 2}
        }
        encoded = OutputEncoder.encode_json(data)
        
        # Should still be valid JSON
        decoded = json.loads(encoded)
        assert len(decoded['users']) == 2
        
        # Should have escaped script tags
        assert "\\u003cscript\\u003e" in encoded
    
    def test_safe_json_shorthand(self):
        """Test convenience function"""
        data = {'test': '<script>'}
        encoded = safe_json(data)
        assert "\\u003cscript\\u003e" in encoded


class TestURLEncoding:
    """Test URL context encoding"""
    
    def test_basic_url_encoding(self):
        """Test standard URL encoding"""
        assert OutputEncoder.encode_url("hello world") == "hello%20world"
        assert OutputEncoder.encode_url("a&b") == "a%26b"
    
    def test_special_characters(self):
        """Test encoding of URL-special characters"""
        assert OutputEncoder.encode_url("?") == "%3F"
        assert OutputEncoder.encode_url("=") == "%3D"
        assert OutputEncoder.encode_url("#") == "%23"
    
    def test_plus_encoding(self):
        """Test space encoding with plus_safe=True"""
        encoded = OutputEncoder.encode_url("hello world", plus_safe=True)
        assert encoded == "hello+world"
    
    def test_script_tag_in_url(self):
        """Test URL encoding of XSS payloads"""
        payload = "<script>alert(1)</script>"
        encoded = OutputEncoder.encode_url(payload)
        
        assert "<" not in encoded
        assert ">" not in encoded
        assert "%3C" in encoded  # <
        assert "%3E" in encoded  # >
    
    def test_safe_url_shorthand(self):
        """Test convenience function"""
        assert safe_url("hello world") == "hello%20world"


class TestURLSanitization:
    """Test URL protocol validation and sanitization"""
    
    def test_javascript_protocol_blocked(self):
        """Test that javascript: URLs are blocked"""
        assert OutputEncoder.sanitize_url("javascript:alert(1)") is None
        assert OutputEncoder.sanitize_url("JavaScript:alert(1)") is None
        assert OutputEncoder.sanitize_url("JAVASCRIPT:alert(1)") is None
    
    def test_data_protocol_blocked(self):
        """Test that data: URLs are blocked"""
        assert OutputEncoder.sanitize_url("data:text/html,<script>alert(1)</script>") is None
        assert OutputEncoder.sanitize_url("DATA:text/html,<script>") is None
    
    def test_vbscript_protocol_blocked(self):
        """Test that vbscript: URLs are blocked"""
        assert OutputEncoder.sanitize_url("vbscript:msgbox(1)") is None
    
    def test_file_protocol_blocked(self):
        """Test that file: URLs are blocked"""
        assert OutputEncoder.sanitize_url("file:///etc/passwd") is None
    
    def test_about_protocol_blocked(self):
        """Test that about: URLs are blocked"""
        assert OutputEncoder.sanitize_url("about:blank") is None
    
    def test_http_allowed(self):
        """Test that HTTP URLs are allowed"""
        url = "http://example.com/page?id=123"
        assert OutputEncoder.sanitize_url(url) == url
    
    def test_https_allowed(self):
        """Test that HTTPS URLs are allowed"""
        url = "https://example.com/secure"
        assert OutputEncoder.sanitize_url(url) == url
    
    def test_mailto_allowed(self):
        """Test that mailto: URLs are allowed"""
        url = "mailto:user@example.com"
        assert OutputEncoder.sanitize_url(url) == url
    
    def test_relative_url_allowed(self):
        """Test that relative URLs are allowed"""
        assert OutputEncoder.sanitize_url("/page/123") == "/page/123"
        assert OutputEncoder.sanitize_url("../parent") == "../parent"
        assert OutputEncoder.sanitize_url("child/page") == "child/page"
    
    def test_anchor_url_allowed(self):
        """Test that anchor URLs are allowed"""
        assert OutputEncoder.sanitize_url("#section") == "#section"
    
    def test_non_string_input(self):
        """Test handling of non-string input"""
        assert OutputEncoder.sanitize_url(None) is None
        assert OutputEncoder.sanitize_url(123) is None


class TestCSSEncoding:
    """Test CSS context encoding"""
    
    def test_special_characters_escaped(self):
        """Test that CSS special characters are hex-escaped"""
        encoded = OutputEncoder.encode_css("()")
        
        # Parentheses should be escaped
        assert "(" not in encoded
        assert ")" not in encoded
        assert "\\28" in encoded  # (
        assert "\\29" in encoded  # )
    
    def test_expression_blocked(self):
        """Test encoding of CSS expression() (IE XSS vector)"""
        payload = "expression(alert('XSS'))"
        encoded = OutputEncoder.encode_css(payload)
        
        # Should be heavily escaped
        assert "expression" in encoded  # Alphanumeric preserved
        assert "(" not in encoded
        assert ")" not in encoded
        assert "'" not in encoded
    
    def test_alphanumeric_preserved(self):
        """Test that alphanumeric characters are not escaped"""
        encoded = OutputEncoder.encode_css("color123")
        
        # Letters and numbers should pass through
        assert "color123" == encoded.replace(' ', '')  # Remove trailing spaces


class TestSafeFormatHTML:
    """Test safe HTML templating with auto-escaping"""
    
    def test_basic_substitution(self):
        """Test basic variable substitution with escaping"""
        template = "<div>{name}</div>"
        result = OutputEncoder.safe_format_html(template, name="<script>alert(1)</script>")
        
        assert "&lt;script&gt;" in result
        assert "<script>" not in result
    
    def test_multiple_variables(self):
        """Test multiple variable substitution"""
        template = "<div>{first} {last}</div>"
        result = OutputEncoder.safe_format_html(
            template,
            first="<b>Bold</b>",
            last="<i>Italic</i>"
        )
        
        assert "&lt;b&gt;" in result
        assert "&lt;i&gt;" in result
        assert "<b>" not in result
    
    def test_non_string_variables(self):
        """Test that non-strings are converted and escaped"""
        template = "<div>{count}</div>"
        result = OutputEncoder.safe_format_html(template, count=123)
        
        assert "123" in result


class TestJinja2Integration:
    """Test Jinja2 security extension"""
    
    def test_get_filters_returns_dict(self):
        """Test that get_filters returns all expected filters"""
        filters = Jinja2SecurityExtension.get_filters()
        
        assert 'js_escape' in filters
        assert 'url_encode' in filters
        assert 'json_safe' in filters
        assert 'css_escape' in filters
        assert 'sanitize_url' in filters
        
        # Filters should be callable
        assert callable(filters['js_escape'])
    
    def test_configure_jinja_env(self):
        """Test Jinja2 environment configuration"""
        from jinja2 import Environment
        
        env = Environment()
        Jinja2SecurityExtension.configure_jinja_env(env)
        
        # Autoescape should be enabled
        assert env.autoescape is True
        
        # Custom filters should be registered
        assert 'js_escape' in env.filters
        assert 'json_safe' in env.filters
        
        # Global functions should be registered
        assert 'safe_json' in env.globals


class TestRealWorldPayloads:
    """Test with real-world XSS attack vectors"""
    
    def test_svg_xss(self):
        """Test SVG-based XSS payload"""
        payload = '<svg onload="alert(1)">'
        encoded = OutputEncoder.encode_html(payload)
        
        assert "<svg" not in encoded
        assert "&lt;svg" in encoded
    
    def test_img_onerror_xss(self):
        """Test img tag with onerror handler"""
        payload = '<img src=x onerror="alert(document.cookie)">'
        encoded = OutputEncoder.encode_html(payload)
        
        # The string 'onerror=' will still appear in encoded output,
        # but the dangerous parts (< > ") are encoded, making it safe
        assert '<img' not in encoded
        assert '&lt;img' in encoded
        assert "&quot;" in encoded
    
    def test_nested_encoding_attack(self):
        """Test nested encoding attempts"""
        payload = '&lt;script&gt;alert(1)&lt;/script&gt;'
        encoded = OutputEncoder.encode_html(payload)
        
        # Should double-encode the &
        assert "&amp;lt;" in encoded
    
    def test_polyglot_payload(self):
        """Test polyglot XSS payload (works in multiple contexts)"""
        payload = "javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/\"/+/onmouseover=1/+/[*/[]/+alert(1)//'>"
        
        # Test in multiple contexts
        html_encoded = OutputEncoder.encode_html(payload)
        js_encoded = OutputEncoder.encode_javascript(payload)
        url_encoded = OutputEncoder.encode_url(payload)
        
        # The literal string 'onload=' may appear, but dangerous chars are encoded
        assert "<svg" not in html_encoded  # Tag start encoded
        assert "&lt;svg" in html_encoded
        assert "</script>" not in html_encoded  # Closing tag encoded
        
        # URL should be percent-encoded
        assert "%" in url_encoded


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_long_string(self):
        """Test encoding of very long strings (10KB)"""
        long_string = "<script>" * 1000
        encoded = OutputEncoder.encode_html(long_string)
        
        # Should complete without error
        assert len(encoded) > len(long_string)
        assert "<script>" not in encoded
    
    def test_repeated_encoding(self):
        """Test that repeated encoding is idempotent (safe to double-encode)"""
        text = "<script>alert(1)</script>"
        
        encoded_once = OutputEncoder.encode_html(text)
        encoded_twice = OutputEncoder.encode_html(encoded_once)
        
        # Second encoding should further escape the &
        assert encoded_twice != encoded_once
        assert "&amp;" in encoded_twice
    
    def test_mixed_contexts(self):
        """Test realistic mixed-context scenario"""
        user_name = '<script>alert("XSS")</script>'
        user_id = 123
        
        # HTML context
        html = f"<div id='{OutputEncoder.encode_html_attribute(str(user_id))}'>{OutputEncoder.encode_html(user_name)}</div>"
        assert "<script>" not in html
        
        # JS context
        js = f"var userName = '{OutputEncoder.encode_javascript(user_name)}';"
        assert '\\"XSS\\"' in js
        
        # JSON context
        json_str = OutputEncoder.encode_json({'name': user_name, 'id': user_id})
        assert "\\u003cscript\\u003e" in json_str


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
