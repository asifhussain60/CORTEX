"""
Test suite for Phase 64 Priority 3: Tier Escalation Logic

AC-PHASE64-S2-001: Intelligent Tier Escalation
Tests the escalation logic that automatically promotes analysis tier based on findings.

12 test cases covering:
- Critical finding escalation
- Ambiguous result escalation
- Confidence threshold testing
- Tier characteristic validation
- Edge cases
"""

import pytest
from typing import Dict, Optional
from cortex.orchestrators.lens_orchestrator_integration import LensOrchestratorTierSelection


class TestTierEscalationLogic:
    """Test suite for FIX #2: Tier Escalation Logic"""
    
    @pytest.fixture
    def selection_engine(self):
        """Fixture: TierSelection engine"""
        return LensOrchestratorTierSelection()
    
    # ══════════════════════════════════════════════════════════════════════════════
    # TEST GROUP 1: Critical Finding Escalation (3 tests)
    # ══════════════════════════════════════════════════════════════════════════════
    
    def test_escalate_on_critical_finding(self, selection_engine):
        """Test: Critical findings trigger escalation to Tier 3"""
        tier_2_result = {
            "findings": [
                {"severity": "critical", "type": "security", "confidence": 0.95},
                {"severity": "warning", "type": "style", "confidence": 0.8}
            ]
        }
        
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=tier_2_result
        )
        
        assert selected_tier == "tier_3_targeted", "Critical findings should escalate to Tier 3"
    
    def test_escalate_on_multiple_critical_findings(self, selection_engine):
        """Test: Multiple critical findings trigger escalation"""
        tier_2_result = {
            "findings": [
                {"severity": "critical", "type": "performance", "confidence": 0.9},
                {"severity": "critical", "type": "security", "confidence": 0.95},
                {"severity": "info", "type": "style", "confidence": 0.7}
            ]
        }
        
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=tier_2_result
        )
        
        assert selected_tier == "tier_3_targeted"
    
    def test_no_escalate_on_non_critical_findings(self, selection_engine):
        """Test: Non-critical findings don't trigger escalation (if high confidence)"""
        tier_2_result = {
            "findings": [
                {"severity": "warning", "type": "style", "confidence": 0.9},
                {"severity": "info", "type": "documentation", "confidence": 0.85}
            ]
        }
        
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=tier_2_result
        )
        
        # Should stay with tier_2 since findings are low severity and high confidence
        assert selected_tier == "tier_2_quick"
    
    # ══════════════════════════════════════════════════════════════════════════════
    # TEST GROUP 2: Ambiguous Result Escalation (3 tests)
    # ══════════════════════════════════════════════════════════════════════════════
    
    def test_escalate_on_low_confidence_findings(self, selection_engine):
        """Test: Low confidence findings trigger escalation"""
        tier_2_result = {
            "findings": [
                {"severity": "warning", "type": "code", "confidence": 0.65},
                {"severity": "info", "type": "style", "confidence": 0.6}
            ]
        }
        
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=tier_2_result
        )
        
        # Average confidence = (0.65 + 0.6) / 2 = 0.625 < 0.7
        assert selected_tier == "tier_3_targeted", "Low confidence should escalate"
    
    def test_escalate_on_boundary_confidence(self, selection_engine):
        """Test: Confidence exactly at threshold"""
        tier_2_result = {
            "findings": [
                {"severity": "warning", "confidence": 0.70},  # Exactly at threshold
            ]
        }
        
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=tier_2_result
        )
        
        # 0.70 is not < 0.70, so should stay
        assert selected_tier == "tier_2_quick"
    
    def test_escalate_on_below_threshold_confidence(self, selection_engine):
        """Test: Confidence just below threshold"""
        tier_2_result = {
            "findings": [
                {"severity": "warning", "confidence": 0.69},  # Just below threshold
            ]
        }
        
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=tier_2_result
        )
        
        # 0.69 < 0.70, so should escalate
        assert selected_tier == "tier_3_targeted"
    
    # ══════════════════════════════════════════════════════════════════════════════
    # TEST GROUP 3: High Confidence Results (3 tests)
    # ══════════════════════════════════════════════════════════════════════════════
    
    def test_stay_on_high_confidence_results(self, selection_engine):
        """Test: High confidence results don't escalate"""
        tier_2_result = {
            "findings": [
                {"severity": "info", "type": "style", "confidence": 0.95},
                {"severity": "info", "type": "naming", "confidence": 0.92}
            ]
        }
        
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=tier_2_result
        )
        
        # Average = (0.95 + 0.92) / 2 = 0.935 > 0.7
        assert selected_tier == "tier_2_quick"
    
    def test_empty_findings_stays_on_initial_tier(self, selection_engine):
        """Test: Empty findings list (avg_confidence = 0) escalates"""
        tier_2_result = {
            "findings": []
        }
        
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=tier_2_result
        )
        
        # Empty findings = avg_confidence of 0.0, which is < 0.7, so escalates
        assert selected_tier == "tier_3_targeted"
    
    def test_single_finding_confidence_evaluation(self, selection_engine):
        """Test: Single finding confidence correctly evaluated"""
        tier_2_result = {
            "findings": [
                {"severity": "warning", "confidence": 0.72}
            ]
        }
        
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=tier_2_result
        )
        
        # 0.72 >= 0.7, stay with tier_2
        assert selected_tier == "tier_2_quick"
    
    # ══════════════════════════════════════════════════════════════════════════════
    # TEST GROUP 4: Edge Cases (3 tests)
    # ══════════════════════════════════════════════════════════════════════════════
    
    def test_none_tier_2_result(self, selection_engine):
        """Test: None tier_2_result returns initial tier"""
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=None
        )
        
        assert selected_tier == "tier_2_quick"
    
    def test_missing_findings_key(self, selection_engine):
        """Test: Missing 'findings' key treated as empty list (escalates)"""
        tier_2_result = {
            "timestamp": "2026-02-09T10:00:00",
            "status": "success"
        }
        
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=tier_2_result
        )
        
        # Missing findings key → empty list → avg_confidence 0.0 → escalates
        assert selected_tier == "tier_3_targeted"
    
    def test_mixed_severity_and_confidence(self, selection_engine):
        """Test: Critical + low confidence results (critical wins)"""
        tier_2_result = {
            "findings": [
                {"severity": "critical", "confidence": 0.5},  # Critical but low confidence
                {"severity": "info", "confidence": 0.9}
            ]
        }
        
        selected_tier = selection_engine.select_tier_with_escalation(
            initial_tier="tier_2_quick",
            tier_2_result=tier_2_result
        )
        
        # Critical severity should escalate
        assert selected_tier == "tier_3_targeted"


class TestTierCharacteristics:
    """Test tier characteristic retrieval"""
    
    def test_get_tier_2_characteristics(self):
        """Test: Tier 2 characteristics retrieved correctly"""
        chars = LensOrchestratorTierSelection.get_tier_characteristics("tier_2_quick")
        
        assert chars["latency_ms"] == 200
        assert chars["throughput_rps"] == 100
        assert chars["caching"] is True
        assert chars["cache_hit_target"] == 0.7
    
    def test_get_tier_3_targeted_characteristics(self):
        """Test: Tier 3 targeted characteristics"""
        chars = LensOrchestratorTierSelection.get_tier_characteristics("tier_3_targeted")
        
        assert chars["latency_ms"] == 2000
        assert chars["throughput_rps"] == 10
        assert chars["custom_capabilities"] is True
    
    def test_get_tier_4_characteristics(self):
        """Test: Tier 4 full analysis characteristics"""
        chars = LensOrchestratorTierSelection.get_tier_characteristics("tier_4_full")
        
        assert chars["latency_ms"] == 10000
        assert chars["throughput_rps"] == 1
        assert chars["comprehensive"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
