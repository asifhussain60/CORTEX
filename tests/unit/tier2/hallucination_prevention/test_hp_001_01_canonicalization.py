"""
Test suite for HP-001-01: Intent Canonicalization Engine

AC-HP-001-01: Extended canonicalization with AC-ID, phase, and action type extraction
- Target: 36/36 tests passing
- Governance: Full audit trail (AC_START, AC_EXECUTE, AC_COMPLETE)
"""

import pytest
from pathlib import Path
import sys
from datetime import datetime

# Add cortex_brain to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "cortex_brain"))

from tier2.hallucination_prevention.canonicalization_engine import (
    CanonicalIntentEngine,
    IntentCanonicalForm,
    ACIDExtraction,
    PhaseClassification,
    ActionTypeClassifier,
)


class TestIntentCanonicalForm:
    """Tests for IntentCanonicalForm data structure"""

    def test_intent_canonical_form_creation(self):
        """Should create a valid canonical form"""
        form = IntentCanonicalForm(
            ac_id="AC-HP-001-01",
            phase="PHASE-11",
            action_type="IMPLEMENT",
            original_text="Implement HP-001-01 for AC-HP-001-01 in PHASE-11"
        )
        assert form.ac_id == "AC-HP-001-01"
        assert form.phase == "PHASE-11"
        assert form.action_type == "IMPLEMENT"

    def test_intent_canonical_form_with_metadata(self):
        """Should preserve metadata in canonical form"""
        form = IntentCanonicalForm(
            ac_id="AC-HP-001-01",
            phase="PHASE-11",
            action_type="VERIFY",
            original_text="Verify tests",
            confidence_score=0.95,
            normalized_text="verify tests for hp-001-01"
        )
        assert form.confidence_score == 0.95
        assert form.normalized_text == "verify tests for hp-001-01"

    def test_intent_canonical_form_serialization(self):
        """Should serialize to dict"""
        form = IntentCanonicalForm(
            ac_id="AC-HP-001-01",
            phase="PHASE-11",
            action_type="EXECUTE"
        )
        data = form.to_dict()
        assert isinstance(data, dict)
        assert data["ac_id"] == "AC-HP-001-01"


class TestACIDExtraction:
    """Tests for AC-ID extraction from varied formats"""

    def test_extract_strict_ac_id_format(self):
        """Should extract AC-ID from strict format (AC-XXX-XXX-XX)"""
        engine = CanonicalIntentEngine()
        result = engine.extract_ac_id("AC-HP-001-01")
        assert result == "AC-HP-001-01"

    def test_extract_ac_id_from_text(self):
        """Should extract AC-ID from natural text"""
        engine = CanonicalIntentEngine()
        result = engine.extract_ac_id("Please implement AC-HP-001-01 for hallucination prevention")
        assert result == "AC-HP-001-01"

    def test_extract_ac_id_multiple_in_text(self):
        """Should extract first AC-ID when multiple present"""
        engine = CanonicalIntentEngine()
        result = engine.extract_ac_id("AC-HP-001-01 and AC-HP-001-02 work together")
        assert result == "AC-HP-001-01"

    def test_extract_ac_id_loose_format(self):
        """Should extract AC-ID from loose format"""
        engine = CanonicalIntentEngine()
        # Handles variations like "HP-001-01" without "AC-"
        result = engine.extract_ac_id("HP-001-01")
        assert result == "AC-HP-001-01"

    def test_extract_ac_id_case_insensitive(self):
        """Should normalize AC-ID case"""
        engine = CanonicalIntentEngine()
        result = engine.extract_ac_id("ac-hp-001-01")
        assert result == "AC-HP-001-01"

    def test_extract_ac_id_with_special_chars(self):
        """Should handle AC-ID with various separators"""
        engine = CanonicalIntentEngine()
        result = engine.extract_ac_id("AC_HP_001_01")
        assert result == "AC-HP-001-01"

    def test_extract_ac_id_not_found(self):
        """Should return None when AC-ID not found"""
        engine = CanonicalIntentEngine()
        result = engine.extract_ac_id("No AC-ID in this text")
        assert result is None

    def test_extract_ac_id_malformed_rejects(self):
        """Should reject malformed AC-IDs"""
        engine = CanonicalIntentEngine()
        # Invalid length
        result = engine.extract_ac_id("AC-HP-001")
        assert result is None

    def test_extract_ac_id_with_validation(self):
        """Should validate AC-ID format strictly"""
        engine = CanonicalIntentEngine()
        result = engine.extract_ac_id("AC-HP-001-01", validate=True)
        assert result == "AC-HP-001-01"


class TestPhaseClassification:
    """Tests for phase identification from context"""

    def test_classify_phase_explicit(self):
        """Should classify phase from explicit text"""
        engine = CanonicalIntentEngine()
        result = engine.classify_phase("PHASE-11 implementation task")
        assert result == "PHASE-11"

    def test_classify_phase_from_ac_id(self):
        """Should infer phase from AC-ID"""
        engine = CanonicalIntentEngine()
        result = engine.classify_phase("AC-HP-001-01", infer_from_ac_id=True)
        assert result == "PHASE-11"

    def test_classify_phase_multiple_contexts(self):
        """Should use context hierarchy"""
        engine = CanonicalIntentEngine()
        result = engine.classify_phase("In PHASE-11, implement AC-HP-001-01")
        assert result == "PHASE-11"

    def test_classify_phase_case_insensitive(self):
        """Should normalize phase names"""
        engine = CanonicalIntentEngine()
        result = engine.classify_phase("phase-11")
        assert result == "PHASE-11"

    def test_classify_phase_with_number_only(self):
        """Should handle numeric phase format"""
        engine = CanonicalIntentEngine()
        result = engine.classify_phase("11")
        assert result == "PHASE-11"

    def test_classify_phase_not_found(self):
        """Should return None if phase not identifiable"""
        engine = CanonicalIntentEngine()
        result = engine.classify_phase("No phase context here")
        assert result is None

    def test_classify_phase_validation(self):
        """Should validate phase format"""
        engine = CanonicalIntentEngine()
        result = engine.classify_phase("PHASE-11", validate=True)
        assert result == "PHASE-11"


class TestActionTypeClassifier:
    """Tests for action type classification"""

    def test_classify_implement_action(self):
        """Should classify IMPLEMENT actions"""
        engine = CanonicalIntentEngine()
        result = engine.classify_action("Implement the feature")
        assert result == "IMPLEMENT"

    def test_classify_verify_action(self):
        """Should classify VERIFY actions"""
        engine = CanonicalIntentEngine()
        result = engine.classify_action("Verify all tests pass")
        assert result == "VERIFY"

    def test_classify_create_action(self):
        """Should classify CREATE actions"""
        engine = CanonicalIntentEngine()
        result = engine.classify_action("Create new module")
        assert result == "CREATE"

    def test_classify_modify_action(self):
        """Should classify MODIFY actions"""
        engine = CanonicalIntentEngine()
        result = engine.classify_action("Modify existing code")
        assert result == "MODIFY"

    def test_classify_delete_action(self):
        """Should classify DELETE actions"""
        engine = CanonicalIntentEngine()
        result = engine.classify_action("Delete old files")
        assert result == "DELETE"

    def test_classify_action_case_insensitive(self):
        """Should normalize action case"""
        engine = CanonicalIntentEngine()
        result = engine.classify_action("implement feature")
        assert result == "IMPLEMENT"

    def test_classify_action_with_modifiers(self):
        """Should handle action modifiers"""
        engine = CanonicalIntentEngine()
        result = engine.classify_action("Please implement feature carefully")
        assert result == "IMPLEMENT"

    def test_classify_action_not_recognized(self):
        """Should return UNKNOWN for unrecognized actions"""
        engine = CanonicalIntentEngine()
        result = engine.classify_action("Foobarify the system")
        assert result == "UNKNOWN"


class TestCanonicalIntentEngine:
    """Integration tests for CanonicalIntentEngine"""

    def test_engine_initialization(self):
        """Should initialize engine with governance registry"""
        engine = CanonicalIntentEngine()
        assert engine is not None
        assert hasattr(engine, 'extract_ac_id')
        assert hasattr(engine, 'classify_phase')
        assert hasattr(engine, 'classify_action')

    def test_canonicalize_simple_intent(self):
        """Should canonicalize simple intent"""
        engine = CanonicalIntentEngine()
        intent = "Implement AC-HP-001-01 in PHASE-11"
        result = engine.canonicalize(intent)
        
        assert result.ac_id == "AC-HP-001-01"
        assert result.phase == "PHASE-11"
        assert result.action_type == "IMPLEMENT"

    def test_canonicalize_complex_intent(self):
        """Should canonicalize complex multi-part intent"""
        engine = CanonicalIntentEngine()
        intent = "Please modify the code for AC-HP-001-01 in PHASE-11 to add better error handling"
        result = engine.canonicalize(intent)
        
        assert result.ac_id == "AC-HP-001-01"
        assert result.phase == "PHASE-11"
        assert result.action_type == "MODIFY"

    def test_canonicalize_loose_format(self):
        """Should canonicalize loosely formatted intent"""
        engine = CanonicalIntentEngine()
        intent = "hp-001-01, phase 11, create test"
        result = engine.canonicalize(intent)
        
        assert result.ac_id == "AC-HP-001-01"
        assert result.phase == "PHASE-11"
        assert result.action_type == "CREATE"

    def test_canonicalize_backward_compatible(self):
        """Should maintain backward compatibility with PHASE-07"""
        engine = CanonicalIntentEngine()
        # Should handle intents from PHASE-07 canonicalization
        intent = "AC-IR-002-01"  # From PHASE-07
        result = engine.canonicalize(intent)
        assert result.ac_id == "AC-IR-002-01"

    def test_canonicalize_with_confidence(self):
        """Should include confidence scores"""
        engine = CanonicalIntentEngine()
        result = engine.canonicalize("Implement AC-HP-001-01 in PHASE-11")
        
        assert hasattr(result, 'confidence_score')
        assert 0.0 <= result.confidence_score <= 1.0

    def test_canonicalize_with_normalization(self):
        """Should normalize text during canonicalization"""
        engine = CanonicalIntentEngine()
        result = engine.canonicalize("IMPLEMENT  AC-HP-001-01   IN   PHASE-11")
        
        assert result.original_text is not None
        assert result.normalized_text is not None
        assert len(result.normalized_text) <= len(result.original_text)

    def test_canonicalize_batch_processing(self):
        """Should handle batch canonicalization"""
        engine = CanonicalIntentEngine()
        intents = [
            "Implement AC-HP-001-01 in PHASE-11",
            "Verify AC-HP-001-02 in PHASE-11",
            "Create AC-HP-002-01 in PHASE-11",
        ]
        results = engine.canonicalize_batch(intents)
        
        assert len(results) == 3
        assert results[0].action_type == "IMPLEMENT"
        assert results[1].action_type == "VERIFY"
        assert results[2].action_type == "CREATE"

    def test_canonicalize_preserves_metadata(self):
        """Should preserve custom metadata"""
        engine = CanonicalIntentEngine()
        intent = "Implement AC-HP-001-01"
        result = engine.canonicalize(intent, metadata={"user": "test", "timestamp": "2026-01-17"})
        
        assert result.metadata.get("user") == "test"


class TestBackwardCompatibility:
    """Tests for backward compatibility with PHASE-07"""

    def test_compatibility_with_phase_07_format(self):
        """Should handle PHASE-07 IR-* AC-IDs"""
        engine = CanonicalIntentEngine()
        result = engine.extract_ac_id("AC-IR-002-01")
        assert result == "AC-IR-002-01"

    def test_compatibility_with_phase_07_canonicalization(self):
        """Should produce compatible output with PHASE-07"""
        engine = CanonicalIntentEngine()
        result = engine.canonicalize("AC-IR-002-01")
        assert result.ac_id == "AC-IR-002-01"


class TestErrorHandling:
    """Tests for error handling and edge cases"""

    def test_handle_empty_input(self):
        """Should handle empty input gracefully"""
        engine = CanonicalIntentEngine()
        result = engine.canonicalize("")
        assert result is None or result.ac_id is None

    def test_handle_none_input(self):
        """Should handle None input gracefully"""
        engine = CanonicalIntentEngine()
        result = engine.canonicalize(None)
        assert result is None

    def test_handle_unicode_input(self):
        """Should handle unicode characters"""
        engine = CanonicalIntentEngine()
        result = engine.canonicalize("Implement AC-HP-001-01 for 🎯 goal")
        assert result.ac_id == "AC-HP-001-01"

    def test_handle_very_long_input(self):
        """Should handle very long input"""
        engine = CanonicalIntentEngine()
        long_text = "Implement " + "X" * 10000 + " AC-HP-001-01 in PHASE-11"
        result = engine.canonicalize(long_text)
        assert result.ac_id == "AC-HP-001-01"


class TestAuditTrail:
    """Tests for audit trail integration"""

    def test_canonicalization_logs_to_audit(self):
        """Should create audit entries for canonicalization"""
        engine = CanonicalIntentEngine()
        result = engine.canonicalize("Implement AC-HP-001-01")
        
        # Verify audit entry was created
        audit_entries = engine.get_audit_entries(ac_id="AC-HP-001-01")
        assert len(audit_entries) > 0

    def test_audit_entry_contains_result(self):
        """Should include result in audit entry"""
        engine = CanonicalIntentEngine()
        result = engine.canonicalize("Implement AC-HP-001-01 in PHASE-11")
        
        audit_entries = engine.get_audit_entries(ac_id="AC-HP-001-01")
        assert any(entry.get("action_type") == "IMPLEMENT" for entry in audit_entries)


# =========================================================================
# PYTEST CONFIGURATION AND FIXTURES
# =========================================================================

@pytest.fixture
def engine():
    """Fixture for CanonicalIntentEngine"""
    return CanonicalIntentEngine()


@pytest.fixture
def sample_intents():
    """Fixture with sample intents"""
    return {
        "simple": "Implement AC-HP-001-01 in PHASE-11",
        "complex": "Please modify the code for AC-HP-001-01 in PHASE-11 to add better error handling",
        "loose": "hp-001-01, phase 11, create test",
        "minimal": "AC-HP-001-01",
    }


# =========================================================================
# SUMMARY
# =========================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
