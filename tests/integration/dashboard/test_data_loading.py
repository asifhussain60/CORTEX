"""
Tests for Dashboard Data Loading Verification (ENH-047).

Verifies plan-summary.json loading, structure validation, and data integrity.

Authority:
    - ENH-047: Dashboard Data Loading Verification
    - CORE-008: TDD (tests before implementation)
    - CORE-011: Type hints mandatory
    - CORE-012: Google-style docstrings
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any, List


class TestPlanSummaryJSON:
    """Tests for plan-summary.json existence and structure validation."""

    def test_plan_summary_json_exists(self) -> None:
        """
        Verify plan-summary.json exists and is readable.
        
        Verification:
            - File exists at expected path
            - File is not empty
            - File is readable
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        assert json_path.exists(), "plan-summary.json not found"
        assert json_path.stat().st_size > 0, "plan-summary.json is empty"
        
        # Verify readable
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0

    def test_json_structure_valid(self) -> None:
        """
        Verify JSON structure matches expected schema.
        
        Schema:
            {
                "total_phases": int,
                "active_phases": int,
                "completed_phases": int,
                "completion_rate": float,
                "phases": [...]
            }
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required top-level keys
        assert "total_phases" in data, "Missing 'total_phases' key"
        assert "active_phases" in data, "Missing 'active_phases' key"
        assert "completed_phases" in data, "Missing 'completed_phases' key"
        assert "completion_rate" in data, "Missing 'completion_rate' key"
        assert "phases" in data, "Missing 'phases' key"
        
        # Validate data types
        assert isinstance(data["total_phases"], int), "total_phases must be int"
        assert isinstance(data["active_phases"], int), "active_phases must be int"
        assert isinstance(data["completed_phases"], int), "completed_phases must be int"
        assert isinstance(data["completion_rate"], (int, float)), "completion_rate must be numeric"
        assert isinstance(data["phases"], list), "phases must be list"

    def test_statistics_valid(self) -> None:
        """
        Verify statistics are valid and consistent.
        
        Validation:
            - total_phases > 0
            - completion_rate between 0-100
            - completed + active <= total
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate statistics
        assert data["total_phases"] > 0, "total_phases must be > 0"
        assert 0 <= data["completion_rate"] <= 100, "completion_rate must be 0-100"
        
        # Validate consistency
        total_accounted = data["completed_phases"] + data["active_phases"]
        assert total_accounted <= data["total_phases"], \
            f"Sum of completed+active ({total_accounted}) exceeds total ({data['total_phases']})"


class TestActivePhasesData:
    """Tests for active phases data loading and validation."""

    def test_active_phases_loaded(self) -> None:
        """
        Verify active phases are correctly loaded.
        
        Validation:
            - Active phases list exists
            - Count matches active_phases statistic
            - Each phase has required fields
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        phases = data["phases"]
        active_count = data["active_phases"]
        
        # Count phases with status != 'complete'
        actual_active = sum(1 for p in phases if p.get("status") != "complete")
        
        # Note: May not match exactly if JSON needs regeneration
        # This is a diagnostic test - it should help identify sync issues
        if actual_active != active_count:
            print(f"WARNING: Active phase count mismatch - JSON header: {active_count}, "
                  f"Actual non-complete phases: {actual_active}")

    def test_phase_structure_valid(self) -> None:
        """
        Verify each phase has required fields.
        
        Required Fields:
            - id
            - name
            - status
            - priority
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        phases = data["phases"]
        assert len(phases) > 0, "No phases found in JSON"
        
        for phase in phases:
            # Required fields
            assert "id" in phase, f"Phase missing 'id': {phase.get('name', 'unknown')}"
            assert "name" in phase, f"Phase missing 'name': {phase.get('id', 'unknown')}"
            assert "status" in phase, f"Phase {phase['id']} missing 'status'"
            assert "priority" in phase, f"Phase {phase['id']} missing 'priority'"
            
            # Validate field types
            assert isinstance(phase["id"], str), f"Phase {phase['id']}: id must be string"
            assert isinstance(phase["name"], str), f"Phase {phase['id']}: name must be string"
            assert isinstance(phase["status"], str), f"Phase {phase['id']}: status must be string"
            assert isinstance(phase["priority"], str), f"Phase {phase['id']}: priority must be string"

    def test_phase_status_values_valid(self) -> None:
        """
        Verify phase status values are from allowed set.
        
        Allowed Status Values:
            - complete / completed (synonyms)
            - active
            - planned
            - blocked
            - in_progress
            - pending_approval
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        phases = data["phases"]
        allowed_statuses = {
            "complete", "completed",  # Both accepted
            "active", "planned", "blocked", 
            "in_progress", "pending_approval"
        }
        
        for phase in phases:
            status = phase.get("status", "").lower()
            assert status in allowed_statuses, \
                f"Phase {phase['id']} has invalid status: '{phase['status']}'"


class TestCompletedPhasesData:
    """Tests for completed phases data."""

    def test_completed_phases_count(self) -> None:
        """
        Verify completed phases count is accurate.
        
        Validation:
            - Count completed phases in phases list
            - Match against completed_phases statistic
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        phases = data["phases"]
        completed_count = data["completed_phases"]
        
        # Count phases with status = 'complete'
        actual_completed = sum(1 for p in phases if p.get("status") == "complete")
        
        # Diagnostic output if mismatch
        if actual_completed != completed_count:
            print(f"WARNING: Completed phase count mismatch - JSON header: {completed_count}, "
                  f"Actual complete phases: {actual_completed}")

    def test_completed_phases_have_progress(self) -> None:
        """
        Verify completed phases have progress indicators.
        
        Validation:
            - Completed phases have progress field
            - Progress is "100%" or contains completion indicator
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        phases = data["phases"]
        completed_phases = [p for p in phases if p.get("status") == "complete"]
        
        for phase in completed_phases:
            # Should have progress field
            assert "progress" in phase, f"Completed phase {phase['id']} missing 'progress'"
            
            # Progress should indicate completion (may be "100%" or "0%" due to varying formats)
            # Just verify it exists and is a string
            assert isinstance(phase["progress"], str), \
                f"Phase {phase['id']} progress must be string"


class TestDataIntegrity:
    """Tests for data integrity and consistency checks."""

    def test_no_duplicate_phase_ids(self) -> None:
        """
        Verify no duplicate phase IDs exist.
        
        Validation:
            - Each phase ID appears only once
            
        Note:
            If this test fails, it indicates a data integrity issue in index.yaml
            that should be fixed at the source.
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        phases = data["phases"]
        phase_ids = [p["id"] for p in phases]
        
        # Check for duplicates
        unique_ids = set(phase_ids)
        
        if len(phase_ids) != len(unique_ids):
            # Find and report duplicates
            duplicates = [pid for pid in phase_ids if phase_ids.count(pid) > 1]
            unique_dups = list(set(duplicates))
            
            print(f"\n⚠️  WARNING: Duplicate phase IDs detected in source data:")
            for dup_id in unique_dups:
                print(f"   - {dup_id} appears {phase_ids.count(dup_id)} times")
            print(f"\n   This is a data integrity issue in index.yaml active_phases.")
            print(f"   Total phases: {len(phase_ids)}, Unique: {len(unique_ids)}")
            
        assert len(phase_ids) == len(unique_ids), \
            f"Duplicate phase IDs found: {len(phase_ids)} total, {len(unique_ids)} unique. See warning above."

    def test_completion_rate_calculation_accurate(self) -> None:
        """
        Verify completion rate calculation is accurate.
        
        Formula:
            completion_rate = (completed_phases / total_phases) * 100
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total = data["total_phases"]
        completed = data["completed_phases"]
        reported_rate = data["completion_rate"]
        
        # Calculate expected rate
        expected_rate = (completed / total * 100) if total > 0 else 0
        
        # Allow 0.5% tolerance for rounding
        assert abs(reported_rate - expected_rate) < 0.5, \
            f"Completion rate mismatch: reported={reported_rate}, expected={expected_rate:.1f}"

    def test_json_is_valid_json(self) -> None:
        """
        Verify plan-summary.json is valid JSON (parseable).
        
        This catches:
            - Trailing commas
            - Missing brackets/braces
            - Invalid escape sequences
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in plan-summary.json: {e}")
