"""
PersonaInjector Tests: Apply persona-specific formatting to responses
Authority: Phase 37 S2, CORE-008 (TDD-first)

Tests persona-aware response formatting including:
- Word limits per depth level
- Code visibility rules
- Metric filtering and presentation
- BLUF (Bottom-Line-Up-Front) vs. detailed output
"""

from unittest.mock import MagicMock
import pytest

from cortex.orchestrators.persona.models import PersonaId, DepthLevel
from cortex.orchestrators.persona.persona_injector import PersonaInjector
from cortex.orchestrators.persona.persona_loader import PersonaLoader


class TestPersonaInjectorInitialization:
    """T1-T2: PersonaInjector initialization and setup"""

    def test_initialize_with_persona_loader(self):
        """T1: Initialize PersonaInjector with PersonaLoader"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        assert injector is not None
        assert injector.loader == loader

    def test_persona_injector_has_format_method(self):
        """T2: PersonaInjector has format_response method"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        assert hasattr(injector, 'format_response')
        assert callable(injector.format_response)


class TestWordLimitEnforcement:
    """T3-T6: Word limit enforcement per depth level and persona"""

    def test_apply_word_limit_executive_depth(self):
        """T3: Enforce strict word limits for executive depth"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        # Executive depth should limit to ~100 words
        long_response = " ".join(["word"] * 200)
        formatted = injector.format_response(
            long_response, 
            PersonaId.ENGINEER,
            DepthLevel.EXECUTIVE
        )
        
        word_count = len(formatted.split())
        assert word_count <= 120  # Allow 20% margin
        assert "..." in formatted or word_count < len(long_response.split())

    def test_apply_word_limit_standard_depth(self):
        """T4: Apply moderate word limits for standard depth"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        # Standard depth: ~300 words
        long_response = " ".join(["word"] * 500)
        formatted = injector.format_response(
            long_response,
            PersonaId.PRODUCT_OWNER,
            DepthLevel.STANDARD
        )
        
        word_count = len(formatted.split())
        assert word_count <= 360  # Allow 20% margin

    def test_apply_word_limit_detailed_depth(self):
        """T5: Allow larger responses for detailed depth"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        # Detailed depth: ~800 words
        long_response = " ".join(["word"] * 1000)
        formatted = injector.format_response(
            long_response,
            PersonaId.ENGINEER,
            DepthLevel.DETAILED
        )
        
        word_count = len(formatted.split())
        assert word_count <= 960  # Allow 20% margin

    def test_apply_word_limit_full_depth(self):
        """T6: No word limit for full depth"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        # Full depth: no limit
        long_response = " ".join(["word"] * 2000)
        formatted = injector.format_response(
            long_response,
            PersonaId.TECH_LEAD,
            DepthLevel.FULL
        )
        
        # Should not be truncated
        assert len(formatted) >= len(long_response) - 100  # Allow small margin


class TestCodeVisibility:
    """T7-T10: Code visibility rules per persona"""

    def test_engineer_sees_full_code(self):
        """T7: Engineers get full code blocks"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response_with_code = """
The implementation looks good.

```python
def calculate_roi(revenue, cost):
    return (revenue - cost) / cost * 100

result = calculate_roi(1000, 500)
```

This function calculates ROI efficiently.
"""
        formatted = injector.format_response(
            response_with_code,
            PersonaId.ENGINEER,
            DepthLevel.STANDARD
        )
        
        # Engineer should see full code
        assert "def calculate_roi" in formatted
        assert "return (revenue - cost)" in formatted

    def test_product_owner_sees_minimal_code(self):
        """T8: Product owners get code summaries instead of full code"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response_with_code = """
The implementation looks good.

```python
def calculate_roi(revenue, cost):
    return (revenue - cost) / cost * 100
```

This function calculates ROI efficiently.
"""
        formatted = injector.format_response(
            response_with_code,
            PersonaId.PRODUCT_OWNER,
            DepthLevel.STANDARD
        )
        
        # Product owner should not see code details
        # Either code is removed or replaced with summary
        assert ("def calculate_roi" not in formatted or 
                "[Code snippet: calculate_roi]" in formatted or
                "Code summary" in formatted)

    def test_business_leader_no_code(self):
        """T9: Business leaders get no code blocks"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response_with_code = """
Here's the efficiency analysis:

```python
efficiency = optimized_time / original_time
```

We improved efficiency by 40%.
"""
        formatted = injector.format_response(
            response_with_code,
            PersonaId.BUSINESS_LEADER,
            DepthLevel.STANDARD
        )
        
        # Business leader should not see code
        assert "def " not in formatted
        assert "efficiency =" not in formatted
        # But should see the business metric
        assert "40%" in formatted or "efficiency" in formatted.lower()

    def test_tech_lead_sees_architecture_code(self):
        """T10: Tech leads see code for architectural relevance"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response_with_code = """
The architecture supports:

```python
@dataclass
class ServiceMesh:
    health_check_interval: int
    circuit_breaker_threshold: float
```

This enables resilient distributed systems.
"""
        formatted = injector.format_response(
            response_with_code,
            PersonaId.TECH_LEAD,
            DepthLevel.STANDARD
        )
        
        # Tech lead should see architecture-relevant code
        assert "@dataclass" in formatted
        assert "ServiceMesh" in formatted


class TestBlufFormatting:
    """T11-T13: BLUF (Bottom-Line-Up-Front) vs. detailed formatting"""

    def test_executive_gets_bluf_format(self):
        """T11: Executive depth uses BLUF format"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = """
After analyzing three approaches, we recommend approach B because:
- It reduces implementation time by 30%
- Lower maintenance costs long-term
- Better alignment with roadmap

Technical details involve database migration and API changes...
"""
        formatted = injector.format_response(
            response,
            PersonaId.BUSINESS_LEADER,
            DepthLevel.EXECUTIVE
        )
        
        # Should start with key finding (BLUF)
        lines = formatted.split('\n')
        first_substantive = next((l for l in lines if l.strip()), '')
        assert any(keyword in first_substantive.lower() 
                   for keyword in ['recommend', 'approach', 'key', 'main', 'result'])

    def test_engineer_gets_detailed_format(self):
        """T12: Standard/Detailed depth preserves technical flow"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = """
For the cache implementation:

Step 1: Use Redis for distributed caching
Step 2: Implement TTL of 1 hour
Step 3: Add cache invalidation on updates

Benefits include 5x throughput improvement.
"""
        formatted = injector.format_response(
            response,
            PersonaId.ENGINEER,
            DepthLevel.DETAILED
        )
        
        # Should preserve step-by-step technical detail
        assert "Step 1" in formatted or "Redis" in formatted
        assert "Step 2" in formatted or "TTL" in formatted

    def test_product_owner_gets_impact_focused_format(self):
        """T13: Product owner depth focuses on business impact"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = """
Technical approach:
- Implement GraphQL resolver caching
- Use Redis cluster configuration
- Deploy across 3 availability zones

Business impact:
- 3x faster API response time
- Support 10x more concurrent users
- Improve user satisfaction by reducing timeouts
"""
        formatted = injector.format_response(
            response,
            PersonaId.PRODUCT_OWNER,
            DepthLevel.STANDARD
        )
        
        # Should emphasize business impact
        assert "3x faster" in formatted or "concurrent users" in formatted
        assert ("GraphQL resolver" not in formatted or 
                "Business impact" in formatted)


class TestMetricFiltering:
    """T14-T17: Metric filtering and presentation per persona"""

    def test_engineer_sees_performance_metrics(self):
        """T14: Engineers see performance metrics (latency, throughput, memory)"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = """
Performance results:
- Latency: 50ms (p99)
- Throughput: 1000 req/s
- Memory usage: 512MB
- Cost per request: $0.0001
- Customer satisfaction: 95%
"""
        formatted = injector.format_response(
            response,
            PersonaId.ENGINEER,
            DepthLevel.STANDARD
        )
        
        # Engineer should see technical metrics
        assert "Latency" in formatted
        assert "Throughput" in formatted
        assert "Memory" in formatted

    def test_business_leader_sees_business_metrics(self):
        """T15: Business leaders see business metrics (cost, revenue, satisfaction)"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = """
Performance results:
- Latency: 50ms (p99)
- Throughput: 1000 req/s
- Memory usage: 512MB
- Cost per request: $0.0001
- Customer satisfaction: 95%
- Revenue impact: +$500K annually
"""
        formatted = injector.format_response(
            response,
            PersonaId.BUSINESS_LEADER,
            DepthLevel.STANDARD
        )
        
        # Business leader should see business metrics
        assert ("Cost" in formatted or "Revenue" in formatted or 
                "satisfaction" in formatted.lower())
        # May not see technical metrics
        # (implementation can filter them out)

    def test_product_owner_sees_user_impact_metrics(self):
        """T16: Product owners see user impact metrics"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = """
Analysis shows:
- API latency: 45ms
- Database queries: 3.2 per request
- Error rate: 0.01%
- User churn rate: 2% → 1.5% (improvement)
- Feature adoption: 68% of new users
- Net Promoter Score: 42
"""
        formatted = injector.format_response(
            response,
            PersonaId.PRODUCT_OWNER,
            DepthLevel.STANDARD
        )
        
        # Product owner should see user metrics
        assert ("churn" in formatted.lower() or "adoption" in formatted.lower() or 
                "NPS" in formatted or "Promoter" in formatted)

    def test_tech_lead_sees_system_health_metrics(self):
        """T17: Tech leads see system health metrics"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = """
System health:
- Uptime: 99.95%
- Database replication lag: 50ms
- Cache hit ratio: 88%
- CPU utilization: 65%
- Memory utilization: 72%
- P99 latency: 120ms
- Error budget consumed: 30%
"""
        formatted = injector.format_response(
            response,
            PersonaId.TECH_LEAD,
            DepthLevel.STANDARD
        )
        
        # Tech lead should see architecture/health metrics
        assert any(metric in formatted for metric in 
                   ["Uptime", "replication", "cache", "CPU", "Memory", "latency"])


class TestResponseHeaderFormatting:
    """T18-T20: Response header formatting per CORE-029"""

    def test_response_includes_persona_aware_header(self):
        """T18: Formatted response is persona-aware"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = "Here's the analysis of the system architecture."
        formatted = injector.format_response(
            response,
            PersonaId.TECH_LEAD,
            DepthLevel.STANDARD
        )
        
        # Formatted response should be valid and contain the content
        assert formatted is not None
        assert "architecture" in formatted.lower()

    def test_response_preserves_core_content(self):
        """T19: Core content is preserved during formatting"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = "Key finding: The system has 40% latency improvement."
        formatted = injector.format_response(
            response,
            PersonaId.PRODUCT_OWNER,
            DepthLevel.STANDARD
        )
        
        # Core meaning should be preserved
        assert "40%" in formatted
        assert ("latency" in formatted.lower() or 
                "improvement" in formatted.lower())

    def test_response_handles_empty_input(self):
        """T20: Handle empty response gracefully"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        formatted = injector.format_response(
            "",
            PersonaId.ENGINEER,
            DepthLevel.STANDARD
        )
        
        # Should return something valid (not error)
        assert isinstance(formatted, str)
        assert len(formatted) == 0 or formatted.strip() != ""


class TestEdgeCases:
    """T21-T24: Edge cases and special scenarios"""

    def test_handle_none_depth_defaults_to_standard(self):
        """T21: None depth level defaults to standard"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = " ".join(["word"] * 500)
        formatted = injector.format_response(
            response,
            PersonaId.ENGINEER,
            None  # No depth specified
        )
        
        # Should not error, and should apply some default limits
        assert formatted is not None

    def test_format_unicode_content(self):
        """T22: Handle unicode content safely"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = "Performance improved by 42%. Also: 📊 📈 ✨"
        formatted = injector.format_response(
            response,
            PersonaId.BUSINESS_LEADER,
            DepthLevel.STANDARD
        )
        
        # Should preserve unicode
        assert "42%" in formatted
        # Emoji may or may not be preserved, but no error

    def test_format_html_special_characters(self):
        """T23: Escape or handle HTML special characters"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        response = "Cost < $100, Revenue > $500K, Ratio = 80%"
        formatted = injector.format_response(
            response,
            PersonaId.BUSINESS_LEADER,
            DepthLevel.STANDARD
        )
        
        # Should preserve or safely escape special characters
        assert ("$100" in formatted or "$" in formatted)
        assert ("500" in formatted)

    def test_format_very_long_response(self):
        """T24: Format responses much longer than depth limit"""
        from cortex.orchestrators.persona.persona_injector import PersonaInjector
        
        loader = MagicMock(spec=PersonaLoader)
        injector = PersonaInjector(loader)
        
        # Create very long response (10K words)
        long_response = " ".join(["word"] * 10000)
        formatted = injector.format_response(
            long_response,
            PersonaId.ENGINEER,
            DepthLevel.EXECUTIVE
        )
        
        # Should be truncated appropriately
        word_count = len(formatted.split())
        assert word_count < 5000  # Not the full 10K
        assert word_count > 50  # But not empty
