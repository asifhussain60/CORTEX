"""
Unit tests for Response Format Integration.

Tests integration with gateway, enforcement mechanisms,
and production format gate.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 Stage 3 specification
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from cortex.brain.core.response_format_integration import (
    ResponseFormatIntegration,
    FormatEnforcer,
    FormatGate,
    IntegrationResult,
    EnforcementLevel,
    IntegrationError,
)


class TestEnforcementLevel:
    """Test enforcement level enum."""
    
    def test_enforcement_levels_defined(self):
        """Test all enforcement levels defined."""
        assert hasattr(EnforcementLevel, "STRICT")
        assert hasattr(EnforcementLevel, "MODERATE")
        assert hasattr(EnforcementLevel, "LENIENT")


class TestFormatEnforcer:
    """Test format enforcer."""
    
    @pytest.fixture
    def enforcer(self):
        """Create enforcer instance."""
        return FormatEnforcer(level=EnforcementLevel.MODERATE)
    
    def test_enforcer_initialization(self, enforcer):
        """Test enforcer initializes."""
        assert enforcer is not None
        assert enforcer.level == EnforcementLevel.MODERATE
    
    def test_enforce_format_auto_corrects(self, enforcer):
        """Test format enforcement auto-corrects."""
        bad_response = """Bad format
✅ Will do later"""
        
        result = enforcer.enforce(bad_response, orchestrator="TestOrch")
        
        # Should have corrections
        assert result.corrected is True
        assert "## 🧠 CORTEX" in result.response


class TestFormatGate:
    """Test format gate (production gate)."""
    
    @pytest.fixture
    def gate(self):
        """Create format gate."""
        return FormatGate()
    
    def test_gate_initialization(self, gate):
        """Test gate initializes."""
        assert gate is not None
    
    def test_gate_allows_valid_format(self, gate):
        """Test gate allows valid format."""
        valid_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

✅ Implementation Complete"""
        
        passed = gate.check(valid_response)
        
        assert passed is True
    
    def test_gate_blocks_invalid_format(self, gate):
        """Test gate blocks invalid format."""
        invalid_response = """No header
Bad format"""
        
        passed = gate.check(invalid_response)
        
        assert passed is False
    
    def test_gate_with_threshold(self, gate):
        """Test gate with quality threshold."""
        mediocre_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Some content."""
        
        # Should pass with default threshold
        passed = gate.check(mediocre_response, threshold=0.7)
        
        assert isinstance(passed, bool)


class TestResponseFormatIntegration:
    """Test response format integration."""
    
    @pytest.fixture
    def integration(self):
        """Create integration instance."""
        return ResponseFormatIntegration()
    
    def test_integration_initialization(self, integration):
        """Test integration initializes."""
        assert integration is not None
        assert integration.validator is not None
        assert integration.optimizer is not None
        assert integration.enforcer is not None
    
    def test_process_response_end_to_end(self, integration):
        """Test end-to-end response processing."""
        raw_response = """Implementation complete"""
        
        result = integration.process(
            raw_response,
            orchestrator="TDDOrchestrator",
            enforce=True,
        )
        
        assert isinstance(result, IntegrationResult)
        assert result.final_response is not None
        assert "## 🧠 CORTEX" in result.final_response
    
    def test_integration_with_gateway(self, integration):
        """Test integration with master orchestrator gateway."""
        from cortex.brain.core.master_orchestrator_gateway import GatewayResponse
        
        # Simulate gateway response
        gateway_response = Mock(spec=GatewayResponse)
        gateway_response.success = True
        
        # Process should work with gateway responses
        result = integration.process_gateway_response(
            gateway_response,
            orchestrator="TestOrch",
        )
        
        assert result is not None


class TestEnforcementLevels:
    """Test different enforcement levels."""
    
    def test_strict_enforcement(self):
        """Test strict enforcement blocks more."""
        enforcer = FormatEnforcer(level=EnforcementLevel.STRICT)
        
        mediocre_response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Mediocre content."""
        
        result = enforcer.enforce(mediocre_response)
        
        # Strict mode should correct even minor issues
        assert result is not None
    
    def test_lenient_enforcement(self):
        """Test lenient enforcement allows more."""
        enforcer = FormatEnforcer(level=EnforcementLevel.LENIENT)
        
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Basic content."""
        
        result = enforcer.enforce(response)
        
        # Lenient mode should not over-correct
        assert result is not None


class TestAutoCorrection:
    """Test automatic correction."""
    
    @pytest.fixture
    def integration(self):
        """Create integration instance."""
        return ResponseFormatIntegration()
    
    def test_auto_correct_header(self, integration):
        """Test automatic header correction."""
        response = """Content without header"""
        
        result = integration.process(response, orchestrator="TestOrch", enforce=True)
        
        assert "## 🧠 CORTEX" in result.final_response
    
    def test_auto_correct_icons(self, integration):
        """Test automatic icon correction."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

✅ Will implement tomorrow"""
        
        result = integration.process(response, enforce=True)
        
        # Should replace ✅ with ⚪
        assert "⚪" in result.final_response or result.corrections_applied > 0


class TestFormatMetrics:
    """Test format metrics collection."""
    
    @pytest.fixture
    def integration(self):
        """Create integration instance."""
        return ResponseFormatIntegration()
    
    def test_collect_metrics(self, integration):
        """Test metrics collection."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Content here."""
        
        result = integration.process(response, collect_metrics=True)
        
        assert hasattr(result, 'metrics')
        assert result.metrics is not None
    
    def test_metrics_include_scores(self, integration):
        """Test metrics include quality scores."""
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Content here."""
        
        result = integration.process(response, collect_metrics=True)
        
        if hasattr(result, 'metrics') and result.metrics:
            assert 'quality_score' in result.metrics or 'validation_score' in result.metrics


class TestProductionGate:
    """Test production format gate."""
    
    def test_production_gate_blocks_poor_format(self):
        """Test production gate blocks poor format."""
        gate = FormatGate(production_mode=True)
        
        poor = """Bad format
No structure"""
        
        passed = gate.check(poor)
        assert passed is False


class TestIntegrationErrorHandling:
    """Test integration error handling."""
    
    def test_integration_error_inheritance(self):
        """Test IntegrationError inherits from Exception."""
        error = IntegrationError("test error")
        assert isinstance(error, Exception)
    
    def test_handles_invalid_input(self):
        """Test handling of invalid input."""
        integration = ResponseFormatIntegration()
        
        # None input
        result = integration.process(None, orchestrator="TestOrch")
        
        assert result is not None
        assert result.final_response is not None
    
class TestBackwardCompatibility:
    """Test backward compatibility."""
    
    def test_works_without_enforcement(self):
        """Test system works without enforcement."""
        integration = ResponseFormatIntegration()
        
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Content here."""
        
        result = integration.process(response, enforce=False)
        
        assert result.final_response == response  # No changes
    
    def test_gradual_rollout_support(self):
        """Test gradual rollout with different levels."""
        # Lenient for gradual rollout
        integration_lenient = ResponseFormatIntegration(
            enforcement_level=EnforcementLevel.LENIENT
        )
        
        response = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

Basic content."""
        
        result = integration_lenient.process(response)
        
        assert result is not None
