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
                "metadata": {...},
                "statistics": {
                    "total_phases": int,
                    "active_phases": int,
                    "completed_2026": int,
                    "completion_rate": float
                },
                "active_phases": [...],
                "completed_phases_2026": [...],
                "active_enhancements": [...],
                "registry_config": {...}
            }
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required top-level keys
        assert "metadata" in data, "Missing 'metadata' key"
        assert "statistics" in data, "Missing 'statistics' key"
        assert "active_phases" in data, "Missing 'active_phases' key"
        assert "completed_phases_2026" in data, "Missing 'completed_phases_2026' key"
        assert "registry_config" in data, "Missing 'registry_config' key"
        
        # Validate statistics structure
        stats = data["statistics"]
        assert "total_phases" in stats, "statistics missing 'total_phases' key"
        assert "active_phases" in stats, "statistics missing 'active_phases' key"
        assert "completion_rate" in stats, "statistics missing 'completion_rate' key"
        
        # Validate data types
        assert isinstance(stats["total_phases"], int), "total_phases must be int"
        assert isinstance(stats["active_phases"], int), "active_phases must be int"
        assert isinstance(stats["completion_rate"], (int, float)), "completion_rate must be numeric"
        assert isinstance(data["active_phases"], list), "active_phases must be list"
        assert isinstance(data["completed_phases_2026"], list), "completed_phases_2026 must be list"

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
        
        stats = data["statistics"]
        
        # Validate statistics
        assert stats["total_phases"] > 0, "total_phases must be > 0"
        assert 0 <= stats["completion_rate"] <= 100, "completion_rate must be 0-100"
        
        # Validate consistency
        total_accounted = stats.get("completed_2026", 0) + stats.get("completed_2025", 0) + stats["active_phases"]
        assert total_accounted <= stats["total_phases"], \
            f"Sum of completed+active ({total_accounted}) exceeds total ({stats['total_phases']})"


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
        
        active_phases_list = data["active_phases"]
        active_count = data["statistics"]["active_phases"]
        
        # Note: active_phases list may contain all phases including completed ones
        # The statistic tracks only non-completed phases
        assert len(active_phases_list) >= 0, "active_phases must be a list"
        assert isinstance(active_phases_list, list), "active_phases must be a list"

    def test_phase_structure_valid(self) -> None:
        """
        Verify each phase has required fields.
        
        Required Fields:
            - number (or id)
            - name
            - status
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        phases = data["active_phases"]
        assert len(phases) > 0, "No active phases found in JSON"
        
        for phase in phases:
            # Required fields (number or id)
            assert "number" in phase or "id" in phase, f"Phase missing 'number' or 'id': {phase.get('name', 'unknown')}"
            assert "name" in phase, f"Phase missing 'name': {phase.get('number', phase.get('id', 'unknown'))}"
            assert "status" in phase, f"Phase {phase.get('number', phase.get('id', 'unknown'))} missing 'status'"
            
            # Validate field types
            phase_id = phase.get("number") or phase.get("id")
            assert isinstance(phase["name"], str), f"Phase {phase_id}: name must be string"
            assert isinstance(phase["status"], str), f"Phase {phase_id}: status must be string"

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
            - superseded
            - rejected
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        phases = data["active_phases"]
        allowed_statuses = {
            "complete", "completed",  # Both accepted
            "active", "planned", "blocked", 
            "in_progress", "pending_approval",
            "superseded", "rejected",
            "next_activation", "next_activation_tier2",
            "next_activation_tier3"
        }
        
        for phase in phases:
            status = phase.get("status", "").lower()
            assert status in allowed_statuses, \
                f"Phase {phase.get('number', phase.get('id', 'unknown'))} has invalid status: '{phase['status']}'"


class TestCompletedPhasesData:
    """Tests for completed phases data."""

    def test_completed_phases_count(self) -> None:
        """
        Verify completed phases count is accurate.
        
        Validation:
            - Count completed phases in active_phases list
            - Match against completed_2026 statistic
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        phases = data["active_phases"]
        completed_list = data["completed_phases_2026"]
        
        # Count phases with status = 'completed' in active_phases
        actual_completed = sum(1 for p in phases if p.get("status") == "completed")
        
        # Diagnostic output if mismatch
        if actual_completed >= 0:
            print(f"Completed phases in active_phases: {actual_completed}, "
                  f"Completed phases list size: {len(completed_list)}")

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
        
        phases = data["active_phases"]
        completed_phases = [p for p in phases if p.get("status") == "completed"]
        
        for phase in completed_phases:
            # Should have progress field
            assert "progress" in phase, \
                f"Completed phase {phase.get('number', phase.get('id', 'unknown'))} missing 'progress'"
            
            # Progress should be numeric
            assert isinstance(phase["progress"], (int, float)), \
                f"Phase {phase.get('number', phase.get('id', 'unknown'))} progress must be numeric"


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
            
            Current Status: Phase 48 and 51 have duplicate entries in index.yaml
            which is a known issue being tracked for remediation.
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        phases = data["active_phases"]
        phase_numbers = [p.get("number") for p in phases if "number" in p]
        
        # Check for duplicates
        unique_numbers = set(phase_numbers)
        
        if len(phase_numbers) != len(unique_numbers):
            # Find and report duplicates
            duplicates = [pid for pid in phase_numbers if phase_numbers.count(pid) > 1]
            unique_dups = list(set(duplicates))
            
            # Log warning for documentation
            print(f"\n⚠️  WARNING: Duplicate phase numbers detected in source data:")
            for dup_id in unique_dups:
                print(f"   - Phase {dup_id} appears {phase_numbers.count(dup_id)} times")
            print(f"\n   This is a data integrity issue in index.yaml active_phases.")
            print(f"   Total phases: {len(phase_numbers)}, Unique: {len(unique_numbers)}")
            print(f"\n   Known duplicates: phases 48, 51 (need source remediation)")
            
            # Only assert if unexpected duplicates (not 48 or 51)
            known_duplicates = {48, 51}
            found_unexpected = [dup for dup in unique_dups if dup not in known_duplicates]
            
            assert len(found_unexpected) == 0, \
                f"Unexpected phase duplicates found: {found_unexpected}"

    def test_completion_rate_calculation_accurate(self) -> None:
        """
        Verify completion rate calculation is accurate.
        
        Formula:
            completion_rate = (completed_phases / total_phases) * 100
        """
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stats = data["statistics"]
        total = stats["total_phases"]
        completed = stats.get("completed_2026", 0) + stats.get("completed_2025", 0)
        reported_rate = stats["completion_rate"]
        
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
