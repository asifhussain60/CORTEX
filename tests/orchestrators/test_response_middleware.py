"""
Unit Tests for ResponseMiddleware

Tests system message injection:
- Token warnings (80%+ usage)
- Security alerts (validation failures)
- Deprecation notices (old APIs)
- Success enrichment (metadata)
- Priority ordering
- Message formatting

Target: 95% code coverage

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from src.orchestrators.response_middleware import (
    ResponseMiddleware,
    SystemMessage,
    MessagePriority
)


class TestTokenWarnings:
    """Test token warning injection."""
    
    @pytest.fixture
    def middleware(self):
        """Create ResponseMiddleware instance."""
        return ResponseMiddleware(token_warning_threshold=80)
    
    def test_token_warning_at_threshold(self, middleware):
        """Test token warning triggered at exactly 80%."""
        markdown = "## 🧠 CORTEX Response\n\n✅ Plan created successfully"
        context = {
            'token_usage_percentage': 80.0,
            'session_id': 'test-session-123',
            'total_tokens': 80000
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "⚠️ **Token Warning**" in result
        assert "80.0% used" in result
        assert "80,000 tokens" in result
        assert "cortex vacuum" in result
        assert "cortex continue test-session-123" in result
        assert "---" in result
        assert "## 🧠 CORTEX Response" in result
    
    def test_token_warning_above_threshold(self, middleware):
        """Test token warning triggered above 80%."""
        markdown = "## Response"
        context = {
            'token_usage_percentage': 92.5,
            'session_id': 'abc-456',
            'total_tokens': 92500
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "⚠️ **Token Warning**" in result
        assert "92.5% used" in result
        assert "92,500 tokens" in result
    
    def test_no_warning_below_threshold(self, middleware):
        """Test no token warning below 80%."""
        markdown = "## 🧠 CORTEX Response\n\nSuccess!"
        context = {
            'token_usage_percentage': 65.0,
            'session_id': 'test-session-789',
            'total_tokens': 65000
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        # Should return original markdown unchanged
        assert result == markdown
        assert "Token Warning" not in result
        assert "---" not in result
    
    def test_custom_threshold(self):
        """Test custom token warning threshold."""
        middleware = ResponseMiddleware(token_warning_threshold=70)
        markdown = "## Response"
        context = {
            'token_usage_percentage': 75.0,
            'session_id': 'test',
            'total_tokens': 75000
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        # Should trigger warning at 75% with 70% threshold
        assert "⚠️ **Token Warning**" in result
        assert "75.0% used" in result
    
    def test_missing_token_context(self, middleware):
        """Test graceful handling when token context missing."""
        markdown = "## Response"
        context = {}  # No token info
        
        result = middleware.inject_system_messages(markdown, context)
        
        # Should return original markdown
        assert result == markdown
        assert "Token Warning" not in result


class TestSecurityAlerts:
    """Test security alert injection."""
    
    @pytest.fixture
    def middleware(self):
        """Create ResponseMiddleware instance."""
        return ResponseMiddleware()
    
    def test_single_security_alert(self, middleware):
        """Test single security warning injection."""
        markdown = "## Response\n\nOperation completed"
        context = {
            'security_warnings': [
                "Unsafe file path detected: ../../../etc/passwd"
            ]
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "🚨 **Security Alert**" in result
        assert "Unsafe file path detected" in result
        assert "---" in result
    
    def test_multiple_security_alerts(self, middleware):
        """Test multiple security warnings."""
        markdown = "## Response"
        context = {
            'security_warnings': [
                "Unsafe file path detected: ../config",
                "SQL injection attempt blocked",
                "Cross-site scripting (XSS) detected"
            ]
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert result.count("🚨 **Security Alert**") == 3
        assert "Unsafe file path" in result
        assert "SQL injection" in result
        assert "Cross-site scripting" in result
    
    def test_security_priority_over_token_warning(self, middleware):
        """Test security alerts appear before token warnings (priority order)."""
        markdown = "## Response"
        context = {
            'token_usage_percentage': 85.0,
            'session_id': 'test',
            'total_tokens': 85000,
            'security_warnings': ["Critical security issue"]
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        # Security alert (CRITICAL) should appear before token warning (HIGH)
        security_pos = result.index("🚨 **Security Alert**")
        token_pos = result.index("⚠️ **Token Warning**")
        assert security_pos < token_pos


class TestDeprecationNotices:
    """Test deprecation notice injection."""
    
    @pytest.fixture
    def middleware(self):
        """Create ResponseMiddleware instance."""
        return ResponseMiddleware()
    
    def test_single_deprecation_notice(self, middleware):
        """Test single deprecation notice."""
        markdown = "## Response"
        context = {
            'deprecated_features_used': [
                {
                    'name': 'manual_token_appending',
                    'replacement': 'ResponseMiddleware.inject_system_messages()',
                    'deprecated_in': 'v5.0',
                    'removal_in': 'v6.0'
                }
            ]
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "⚠️ **Deprecation Notice**" in result
        assert "`manual_token_appending` is deprecated" in result
        assert "since v5.0" in result
        assert "will be removed in v6.0" in result
        assert "Use `ResponseMiddleware.inject_system_messages()` instead" in result
    
    def test_multiple_deprecation_notices(self, middleware):
        """Test multiple deprecation notices."""
        markdown = "## Response"
        context = {
            'deprecated_features_used': [
                {
                    'name': 'old_api_v1',
                    'replacement': 'new_api_v2',
                    'deprecated_in': 'v4.5',
                    'removal_in': 'v5.5'
                },
                {
                    'name': 'legacy_renderer',
                    'replacement': 'ResponseRenderer',
                    'deprecated_in': 'v5.0',
                    'removal_in': 'v6.0'
                }
            ]
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert result.count("⚠️ **Deprecation Notice**") == 2
        assert "`old_api_v1` is deprecated" in result
        assert "`legacy_renderer` is deprecated" in result


class TestSuccessEnrichment:
    """Test success metadata enrichment."""
    
    @pytest.fixture
    def middleware(self):
        """Create ResponseMiddleware instance."""
        return ResponseMiddleware()
    
    def test_files_modified_enrichment(self, middleware):
        """Test files modified count enrichment."""
        markdown = "## Response\n\nRefactoring complete"
        context = {
            'success_metadata': {
                'files_modified': 12
            }
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "ℹ️ **Metadata**" in result
        assert "📝 Modified 12 file(s)" in result
    
    def test_test_results_enrichment(self, middleware):
        """Test test results enrichment."""
        markdown = "## Response"
        context = {
            'success_metadata': {
                'tests_passed': 28,
                'tests_total': 29
            }
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "ℹ️ **Metadata**" in result
        assert "✅ Tests: 28/29 passed" in result
    
    def test_coverage_enrichment(self, middleware):
        """Test coverage percentage enrichment."""
        markdown = "## Response"
        context = {
            'success_metadata': {
                'coverage_percentage': 95
            }
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "ℹ️ **Metadata**" in result
        assert "📊 Coverage: 95%" in result
    
    def test_combined_enrichment(self, middleware):
        """Test multiple metadata items combined."""
        markdown = "## Response"
        context = {
            'success_metadata': {
                'files_modified': 5,
                'tests_passed': 42,
                'tests_total': 42,
                'coverage_percentage': 98
            }
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "ℹ️ **Metadata**" in result
        assert "📝 Modified 5 file(s)" in result
        assert "✅ Tests: 42/42 passed" in result
        assert "📊 Coverage: 98%" in result
        # Should be combined with bullet separator
        assert "•" in result
    
    def test_enrichment_priority_last(self, middleware):
        """Test success enrichment appears last (LOW priority)."""
        markdown = "## Response"
        context = {
            'token_usage_percentage': 85.0,
            'session_id': 'test',
            'total_tokens': 85000,
            'success_metadata': {
                'files_modified': 3
            }
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        # Token warning (HIGH) should appear before metadata (LOW)
        token_pos = result.index("⚠️ **Token Warning**")
        metadata_pos = result.index("ℹ️ **Metadata**")
        assert token_pos < metadata_pos


class TestMessagePriority:
    """Test system message priority ordering."""
    
    @pytest.fixture
    def middleware(self):
        """Create ResponseMiddleware instance."""
        return ResponseMiddleware()
    
    def test_all_priorities_ordered(self, middleware):
        """Test all priority levels ordered correctly."""
        markdown = "## Response"
        context = {
            'security_warnings': ["Security issue"],  # CRITICAL (1)
            'token_usage_percentage': 85.0,  # HIGH (2)
            'session_id': 'test',
            'total_tokens': 85000,
            'deprecated_features_used': [{  # MEDIUM (3)
                'name': 'old_feature',
                'replacement': 'new_feature',
                'deprecated_in': 'v5.0',
                'removal_in': 'v6.0'
            }],
            'success_metadata': {  # LOW (4)
                'files_modified': 2
            }
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        # Find positions of each message type
        security_pos = result.index("🚨 **Security Alert**")
        token_pos = result.index("⚠️ **Token Warning**")
        deprecation_pos = result.index("⚠️ **Deprecation Notice**")
        metadata_pos = result.index("ℹ️ **Metadata**")
        
        # Verify correct order: CRITICAL < HIGH < MEDIUM < LOW
        assert security_pos < token_pos < deprecation_pos < metadata_pos


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def middleware(self):
        """Create ResponseMiddleware instance."""
        return ResponseMiddleware()
    
    def test_empty_context(self, middleware):
        """Test with empty context dict."""
        markdown = "## Response\n\nSuccess!"
        context = {}
        
        result = middleware.inject_system_messages(markdown, context)
        
        # Should return original markdown unchanged
        assert result == markdown
    
    def test_none_context_values(self, middleware):
        """Test with None values in context."""
        markdown = "## Response"
        context = {
            'security_warnings': None,
            'deprecated_features_used': None,
            'success_metadata': None
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        # Should handle None gracefully
        assert result == markdown
    
    def test_empty_lists(self, middleware):
        """Test with empty list values."""
        markdown = "## Response"
        context = {
            'security_warnings': [],
            'deprecated_features_used': []
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        # Should return original markdown
        assert result == markdown
    
    def test_partial_deprecation_data(self, middleware):
        """Test deprecation notice with missing fields."""
        markdown = "## Response"
        context = {
            'deprecated_features_used': [
                {
                    'name': 'old_feature'
                    # Missing replacement, versions
                }
            ]
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        # Should use defaults
        assert "⚠️ **Deprecation Notice**" in result
        assert "`old_feature` is deprecated" in result
        assert "See documentation" in result  # Default replacement
        assert "v5.0" in result  # Default deprecated_in
        assert "v6.0" in result  # Default removal_in
