"""
Test suite for ResponseStyler agent.

Tests persona-based response formatting.

AC_START: AC-PHASE37.2-004
"""

import pytest

# Import implemented classes
from cortex.orchestrators.core.response_styler import ResponseStyler


class TestResponseStyler:
    """Test ResponseStyler formatting logic."""
    
    def test_apply_word_limit(self):
        """Should truncate response to persona word limit."""
        styler = ResponseStyler()
        response = "This is a very long response " * 50  # 300 words
        
        formatted = styler.apply_style(
            response,
            persona_id="business_leader"  # 150 word limit
        )
        
        word_count = len(formatted.split())
        assert word_count <= 150
    
    def test_show_code_filtering(self):
        """Should filter code blocks based on persona show_code setting."""
        styler = ResponseStyler()
        response = "Here's the fix:\n```python\ncode here\n```\nDone."
        
        formatted = styler.apply_style(
            response,
            persona_id="business_leader"  # show_code: false
        )
        
        assert "```python" not in formatted
    
    def test_metric_filtering(self):
        """Should include/exclude metrics based on persona settings."""
        styler = ResponseStyler()
        response = "Coverage: 85%, Complexity: 12"
        
        formatted = styler.apply_style(
            response,
            persona_id="business_leader",  # show_metrics: true, metric_types: ["ROI"]
            available_metrics={"coverage": 85, "complexity": 12, "ROI": 150}
        )
        
        assert "ROI" in formatted
        assert "Coverage" not in formatted  # Not in metric_types
    
    def test_format_bluf(self):
        """Should apply BLUF format for business_leader persona."""
        styler = ResponseStyler()
        response = "Long explanation... The answer is yes."
        
        formatted = styler.apply_style(
            response,
            persona_id="business_leader"  # format: "BLUF"
        )
        
        # Bottom Line Up Front should be extracted
        assert formatted.startswith("**BLUF:**")
    
    def test_no_limit_for_engineer(self):
        """Should not limit response for engineer persona."""
        styler = ResponseStyler()
        response = "Long technical explanation " * 1000
        
        formatted = styler.apply_style(
            response,
            persona_id="engineer"  # word_limit: null
        )
        
        assert len(formatted.split()) > 500  # Not truncated


# AC_COMPLETE: AC-PHASE37.2-004 ✅ 5/5 tests enabled
