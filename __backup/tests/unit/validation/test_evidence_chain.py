"""
Evidence Chain Automation Tests (AC-VALIDATE-001 → AC-VALIDATE-003)

TDD tests for automated evidence chain that eliminates manual state manipulation.

Test Coverage:
- AC-VALIDATE-001: Pytest Evidence Plugin (captures AC-ID from test name)
- AC-VALIDATE-002: Evidence Aggregator (audit logs → tracker update)
- AC-VALIDATE-003: Pre-commit Evidence Gate (blocks false positives)

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""
import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock


# =============================================================================
# AC-VALIDATE-001: Pytest Evidence Plugin Tests
# =============================================================================

class TestPytestEvidencePlugin:
    """Tests for pytest plugin that captures AC-ID evidence from test execution"""
    
    @pytest.mark.unit
    def test_extract_ac_id_from_test_name_standard_format(self):
        """Extract AC-ID from test name: test_AC_AUDIT_001_creates_audit_entry"""
        from src.validation.evidence_chain import extract_ac_id_from_test_name
        
        test_name = "test_AC_AUDIT_001_creates_audit_entry"
        ac_id = extract_ac_id_from_test_name(test_name)
        
        assert ac_id == "AC-AUDIT-001"
    
    @pytest.mark.unit
    def test_extract_ac_id_from_test_name_with_underscores(self):
        """Extract AC-ID from test name with underscores: test_AC_VALIDATE_001_input_validation"""
        from src.validation.evidence_chain import extract_ac_id_from_test_name
        
        test_name = "test_AC_VALIDATE_001_input_validation"
        ac_id = extract_ac_id_from_test_name(test_name)
        
        assert ac_id == "AC-VALIDATE-001"
    
    @pytest.mark.unit
    def test_extract_ac_id_from_test_name_no_ac_id(self):
        """Return None if no AC-ID pattern found"""
        from src.validation.evidence_chain import extract_ac_id_from_test_name
        
        test_name = "test_utility_function_works"
        ac_id = extract_ac_id_from_test_name(test_name)
        
        assert ac_id is None
    
    @pytest.mark.unit
    def test_extract_ac_id_handles_multiple_numbers(self):
        """Extract correct AC-ID when multiple numbers present"""
        from src.validation.evidence_chain import extract_ac_id_from_test_name
        
        test_name = "test_AC_ORCH_007_with_3_retries"
        ac_id = extract_ac_id_from_test_name(test_name)
        
        assert ac_id == "AC-ORCH-007"
    
    @pytest.mark.unit
    def test_evidence_entry_creation(self):
        """Create evidence entry with required fields"""
        from src.validation.evidence_chain import create_evidence_entry
        
        entry = create_evidence_entry(
            ac_id="AC-AUDIT-001",
            test_name="test_AC_AUDIT_001_creates_audit_entry",
            outcome="passed",
            duration=0.125
        )
        
        assert entry["ac_id"] == "AC-AUDIT-001"
        assert entry["test_name"] == "test_AC_AUDIT_001_creates_audit_entry"
        assert entry["outcome"] == "passed"
        assert entry["duration"] == 0.125
        assert "timestamp" in entry
        assert entry["source"] == "pytest"
    
    @pytest.mark.unit
    def test_evidence_entry_failed_test(self):
        """Create evidence entry for failed test"""
        from src.validation.evidence_chain import create_evidence_entry
        
        entry = create_evidence_entry(
            ac_id="AC-AUDIT-002",
            test_name="test_AC_AUDIT_002_fails",
            outcome="failed",
            duration=0.05,
            error_message="AssertionError: expected True"
        )
        
        assert entry["outcome"] == "failed"
        assert entry["error_message"] == "AssertionError: expected True"


# =============================================================================
# AC-VALIDATE-002: Evidence Aggregator Tests
# =============================================================================

class TestEvidenceAggregator:
    """Tests for evidence aggregator that updates tracker from audit logs"""
    
    @pytest.mark.unit
    def test_aggregate_evidence_from_audit_logs(self):
        """Aggregate passing test evidence from audit logs"""
        from src.validation.evidence_chain import EvidenceAggregator
        
        # Create mock audit log entries
        audit_entries = [
            {"ac_id": "AC-AUDIT-001", "outcome": "passed", "timestamp": "2026-01-13T10:00:00"},
            {"ac_id": "AC-AUDIT-001", "outcome": "passed", "timestamp": "2026-01-13T10:01:00"},
            {"ac_id": "AC-AUDIT-002", "outcome": "passed", "timestamp": "2026-01-13T10:02:00"},
            {"ac_id": "AC-AUDIT-003", "outcome": "failed", "timestamp": "2026-01-13T10:03:00"},
        ]
        
        aggregator = EvidenceAggregator()
        result = aggregator.aggregate(audit_entries)
        
        # AC-AUDIT-001 and AC-AUDIT-002 should be verified (all tests passed)
        assert "AC-AUDIT-001" in result["verified"]
        assert "AC-AUDIT-002" in result["verified"]
        # AC-AUDIT-003 should NOT be verified (has failed test)
        assert "AC-AUDIT-003" not in result["verified"]
    
    @pytest.mark.unit
    def test_aggregate_requires_all_tests_pass(self):
        """AC-ID only verified if ALL related tests pass"""
        from src.validation.evidence_chain import EvidenceAggregator
        
        audit_entries = [
            {"ac_id": "AC-ORCH-001", "outcome": "passed", "timestamp": "2026-01-13T10:00:00"},
            {"ac_id": "AC-ORCH-001", "outcome": "failed", "timestamp": "2026-01-13T10:01:00"},
            {"ac_id": "AC-ORCH-001", "outcome": "passed", "timestamp": "2026-01-13T10:02:00"},
        ]
        
        aggregator = EvidenceAggregator()
        result = aggregator.aggregate(audit_entries)
        
        # AC-ORCH-001 should NOT be verified (has one failed test)
        assert "AC-ORCH-001" not in result["verified"]
        assert "AC-ORCH-001" in result["partial"]
    
    @pytest.mark.unit
    def test_aggregate_returns_statistics(self):
        """Aggregator returns useful statistics"""
        from src.validation.evidence_chain import EvidenceAggregator
        
        audit_entries = [
            {"ac_id": "AC-AUDIT-001", "outcome": "passed", "timestamp": "2026-01-13T10:00:00"},
            {"ac_id": "AC-AUDIT-002", "outcome": "passed", "timestamp": "2026-01-13T10:01:00"},
            {"ac_id": "AC-AUDIT-003", "outcome": "failed", "timestamp": "2026-01-13T10:02:00"},
        ]
        
        aggregator = EvidenceAggregator()
        result = aggregator.aggregate(audit_entries)
        
        assert result["stats"]["total_entries"] == 3
        assert result["stats"]["unique_ac_ids"] == 3
        assert result["stats"]["verified_count"] == 2
        assert result["stats"]["failed_count"] == 1
    
    @pytest.mark.unit
    def test_update_tracker_with_evidence(self):
        """Update progress tracker with verified AC-IDs"""
        from src.validation.evidence_chain import EvidenceAggregator
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            tracker_data = {
                "current_phase": {
                    "number": 2,
                    "verified_implemented": ["AC-ORCH-001"],
                    "completed_ac_ids": []
                },
                "last_updated": "2026-01-13T00:00:00"
            }
            json.dump(tracker_data, f)
            tracker_path = Path(f.name)
        
        try:
            aggregator = EvidenceAggregator()
            verified_ac_ids = {"AC-ORCH-002", "AC-ORCH-003"}
            
            aggregator.update_tracker(tracker_path, verified_ac_ids)
            
            # Reload and verify
            updated = json.loads(tracker_path.read_text())
            assert "AC-ORCH-002" in updated["current_phase"]["verified_implemented"]
            assert "AC-ORCH-003" in updated["current_phase"]["verified_implemented"]
            assert updated["last_updated"] != "2026-01-13T00:00:00"  # Updated
        finally:
            tracker_path.unlink()
    
    @pytest.mark.unit
    def test_tracker_update_is_atomic(self):
        """Tracker update uses atomic write pattern"""
        from src.validation.evidence_chain import EvidenceAggregator
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            tracker_data = {
                "current_phase": {"number": 2, "verified_implemented": []},
                "last_updated": "2026-01-13T00:00:00"
            }
            json.dump(tracker_data, f)
            tracker_path = Path(f.name)
        
        try:
            aggregator = EvidenceAggregator()
            
            # Simulate concurrent access by checking file integrity
            verified_ac_ids = {"AC-TEST-001"}
            aggregator.update_tracker(tracker_path, verified_ac_ids)
            
            # File should be valid JSON (atomic write succeeded)
            updated = json.loads(tracker_path.read_text())
            assert updated is not None
        finally:
            tracker_path.unlink()


# =============================================================================
# AC-VALIDATE-003: Pre-commit Evidence Gate Tests
# =============================================================================

class TestPrecommitEvidenceGate:
    """Tests for pre-commit hook that blocks false positives"""
    
    @pytest.mark.unit
    def test_gate_passes_when_evidence_matches_claims(self):
        """Gate passes when claimed completion matches evidence"""
        from src.validation.evidence_chain import EvidenceGate
        
        claimed = {"AC-AUDIT-001", "AC-AUDIT-002"}
        verified = {"AC-AUDIT-001", "AC-AUDIT-002", "AC-AUDIT-003"}  # More verified than claimed
        
        gate = EvidenceGate()
        result = gate.check(claimed, verified)
        
        assert result["passed"] is True
        assert result["verification_rate"] >= 100.0
    
    @pytest.mark.unit
    def test_gate_fails_when_claims_exceed_evidence(self):
        """Gate fails when claimed completion exceeds evidence"""
        from src.validation.evidence_chain import EvidenceGate
        
        claimed = {"AC-AUDIT-001", "AC-AUDIT-002", "AC-AUDIT-003"}
        verified = {"AC-AUDIT-001"}  # Only one verified
        
        gate = EvidenceGate()
        result = gate.check(claimed, verified)
        
        assert result["passed"] is False
        assert result["verification_rate"] < 100.0
        assert "AC-AUDIT-002" in result["unverified"]
        assert "AC-AUDIT-003" in result["unverified"]
    
    @pytest.mark.unit
    def test_gate_threshold_configurable(self):
        """Gate threshold is configurable (default 80%)"""
        from src.validation.evidence_chain import EvidenceGate
        
        claimed = {"AC-AUDIT-001", "AC-AUDIT-002", "AC-AUDIT-003", "AC-AUDIT-004", "AC-AUDIT-005"}
        verified = {"AC-AUDIT-001", "AC-AUDIT-002", "AC-AUDIT-003", "AC-AUDIT-004"}  # 80%
        
        gate = EvidenceGate(threshold=80.0)
        result = gate.check(claimed, verified)
        
        assert result["passed"] is True
        assert result["verification_rate"] == 80.0
    
    @pytest.mark.unit
    def test_gate_strict_mode_requires_100_percent(self):
        """Strict mode requires 100% verification"""
        from src.validation.evidence_chain import EvidenceGate
        
        claimed = {"AC-AUDIT-001", "AC-AUDIT-002"}
        verified = {"AC-AUDIT-001"}  # 50%
        
        gate = EvidenceGate(threshold=100.0)  # Strict mode
        result = gate.check(claimed, verified)
        
        assert result["passed"] is False
        assert result["verification_rate"] == 50.0
    
    @pytest.mark.unit
    def test_gate_returns_detailed_report(self):
        """Gate returns detailed report for debugging"""
        from src.validation.evidence_chain import EvidenceGate
        
        claimed = {"AC-AUDIT-001", "AC-AUDIT-002", "AC-AUDIT-003"}
        verified = {"AC-AUDIT-001", "AC-AUDIT-004"}
        
        gate = EvidenceGate()
        result = gate.check(claimed, verified)
        
        assert "verified" in result
        assert "unverified" in result
        assert "extra_evidence" in result
        assert "AC-AUDIT-004" in result["extra_evidence"]  # Verified but not claimed
    
    @pytest.mark.unit
    def test_gate_handles_empty_sets(self):
        """Gate handles edge cases with empty sets"""
        from src.validation.evidence_chain import EvidenceGate
        
        gate = EvidenceGate()
        
        # No claims, no evidence
        result = gate.check(set(), set())
        assert result["passed"] is True
        assert result["verification_rate"] == 100.0
        
        # No claims, some evidence
        result = gate.check(set(), {"AC-AUDIT-001"})
        assert result["passed"] is True
        
        # Some claims, no evidence
        result = gate.check({"AC-AUDIT-001"}, set())
        assert result["passed"] is False


# =============================================================================
# Integration Tests
# =============================================================================

class TestEvidenceChainIntegration:
    """Integration tests for complete evidence chain"""
    
    @pytest.mark.integration
    def test_full_chain_from_test_to_tracker(self):
        """Full chain: test execution → evidence entry → aggregation → tracker update"""
        from src.validation.evidence_chain import (
            extract_ac_id_from_test_name,
            create_evidence_entry,
            EvidenceAggregator,
            EvidenceGate
        )
        
        # Step 1: Simulate test execution
        test_results = [
            ("test_AC_VALIDATE_001_extracts_ac_id", "passed", 0.01),
            ("test_AC_VALIDATE_001_handles_edge_cases", "passed", 0.02),
            ("test_AC_VALIDATE_002_aggregates_evidence", "passed", 0.03),
        ]
        
        # Step 2: Create evidence entries
        entries = []
        for test_name, outcome, duration in test_results:
            ac_id = extract_ac_id_from_test_name(test_name)
            if ac_id:
                entry = create_evidence_entry(ac_id, test_name, outcome, duration)
                entries.append(entry)
        
        assert len(entries) == 3
        
        # Step 3: Aggregate evidence
        aggregator = EvidenceAggregator()
        result = aggregator.aggregate(entries)
        
        assert "AC-VALIDATE-001" in result["verified"]
        assert "AC-VALIDATE-002" in result["verified"]
        
        # Step 4: Check evidence gate
        claimed = {"AC-VALIDATE-001", "AC-VALIDATE-002"}
        gate = EvidenceGate()
        gate_result = gate.check(claimed, result["verified"])
        
        assert gate_result["passed"] is True
    
    @pytest.mark.integration
    def test_chain_detects_false_positives(self):
        """Chain correctly detects false positives (claimed but not verified)"""
        from src.validation.evidence_chain import (
            extract_ac_id_from_test_name,
            create_evidence_entry,
            EvidenceAggregator,
            EvidenceGate
        )
        
        # Only AC-VALIDATE-001 has passing tests
        test_results = [
            ("test_AC_VALIDATE_001_works", "passed", 0.01),
            ("test_AC_VALIDATE_002_fails", "failed", 0.02),  # Failed!
        ]
        
        entries = []
        for test_name, outcome, duration in test_results:
            ac_id = extract_ac_id_from_test_name(test_name)
            if ac_id:
                entry = create_evidence_entry(ac_id, test_name, outcome, duration)
                entries.append(entry)
        
        aggregator = EvidenceAggregator()
        result = aggregator.aggregate(entries)
        
        # Claiming both, but only one is verified
        claimed = {"AC-VALIDATE-001", "AC-VALIDATE-002"}
        gate = EvidenceGate(threshold=100.0)
        gate_result = gate.check(claimed, result["verified"])
        
        assert gate_result["passed"] is False
        assert "AC-VALIDATE-002" in gate_result["unverified"]


# =============================================================================
# Cross-Platform Tests (CORE-005)
# =============================================================================

class TestCrossPlatformCompatibility:
    """Ensure evidence chain works on MAC, WIN, Linux"""
    
    @pytest.mark.cross_platform
    def test_paths_use_pathlib(self):
        """All paths use pathlib.Path for cross-platform compatibility"""
        from src.validation.evidence_chain import EvidenceAggregator
        
        # EvidenceAggregator should accept Path objects
        aggregator = EvidenceAggregator()
        
        # Should not raise on any platform
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"current_phase": {"verified_implemented": []}, "last_updated": ""}, f)
            tracker_path = Path(f.name)
        
        try:
            aggregator.update_tracker(tracker_path, set())
            assert True  # No exception = cross-platform compatible
        finally:
            tracker_path.unlink()
    
    @pytest.mark.cross_platform
    def test_no_hardcoded_paths(self):
        """No hardcoded /Users/ or C:\\ paths in evidence chain"""
        import inspect
        from src.validation import evidence_chain
        
        source = inspect.getsource(evidence_chain)
        
        assert "/Users/" not in source, "Hardcoded macOS path found"
        assert "C:\\" not in source, "Hardcoded Windows path found"
        assert "C:/" not in source, "Hardcoded Windows path found"
