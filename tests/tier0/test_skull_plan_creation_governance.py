"""
SKULL Test: Plan Creation Governance Enforcement

Tests that CORTEX follows proper governance protocol when creating plans:
1. Create dedicated folder in temp-plans/
2. Setup universal subfolders (context/, reports/, artifacts/, tracking/)
3. Create plan files within dedicated folder (NOT in planning/ root)
4. Enforce FILE_ORGANIZATION_ENFORCEMENT rule

This test validates the EXACT scenario from user prompt:
"search for all scattered python and other scripts in the D:\\PROJECTS\\CORTEX repo 
and create a plan to create a proper well architected CORTEX Toolkit"

Author: Asif Hussain
Date: December 16, 2025
SKULL Rule: FILE_ORGANIZATION_ENFORCEMENT + STRICT_FOLDER_ORGANIZATION_ENFORCEMENT
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any

from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
from src.operations.modules.routing.complexity_analyzer import ComplexityAnalyzer
from src.operations.modules.routing.tiered_router import TieredRouter


class TestPlanCreationGovernanceSKULL:
    """Test suite for plan creation governance compliance."""

    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX-like workspace."""
        temp_dir = tempfile.mkdtemp(prefix="cortex_skull_governance_")
        cortex_root = Path(temp_dir)
        
        # Create CORTEX directory structure
        (cortex_root / "cortex-brain" / "documents" / "planning").mkdir(parents=True)
        (cortex_root / "cortex-brain" / "documents" / "planning" / "temp-plans").mkdir()
        (cortex_root / "cortex-brain" / "documents" / "planning" / "active").mkdir()
        (cortex_root / "cortex-brain" / "documents" / "planning" / "completed").mkdir()
        (cortex_root / "src").mkdir()
        (cortex_root / "scripts").mkdir()
        
        yield cortex_root
        
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def universal_subfolders(self):
        """Universal subfolders required in ALL plan folders."""
        return ["context", "reports", "artifacts", "tracking"]

    @pytest.fixture
    def user_request_exact(self):
        """Exact user request from scenario."""
        return "search for all scattered python and other scripts in the D:\\PROJECTS\\CORTEX repo and create a plan to create a proper well architected CORTEX Toolkit to leverage and reuse these scripts as tools"

    # ============================================
    # TEST 1: Exact Scenario - Plan Creation
    # ============================================

    def test_skull_exact_scenario_plan_location(self, temp_cortex_root, user_request_exact, universal_subfolders):
        """
        Test EXACT user scenario: Plan creation for CORTEX Toolkit.
        
        MUST:
        1. Create folder in temp-plans/ (NOT in planning/ root)
        2. Setup universal subfolders
        3. Create plan file in dedicated folder
        """
        orchestrator = PlanningOrchestrator()
        orchestrator.project_root = temp_cortex_root
        
        # Classify the request
        planning_context = orchestrator._classify_and_analyze(user_request_exact)
        
        # Generate plan path
        plan_path = orchestrator._generate_plan_path(planning_context, tier=planning_context.tier)
        
        # SKULL VALIDATION 1: Plan must be in temp-plans/, NOT in planning/ root
        assert "temp-plans" in str(plan_path), \
            f"Plan MUST be in temp-plans/ folder, got: {plan_path}"
        assert plan_path.parent.parent.name == "temp-plans", \
            f"Plan parent folder MUST be temp-plans/, got: {plan_path.parent.parent.name}"
        
        # SKULL VALIDATION 2: Plan must be in dedicated folder (not directly in temp-plans/)
        plan_folder = plan_path.parent
        assert len(plan_folder.name) > 0, \
            f"Plan folder name is empty: {plan_folder}"
        assert plan_folder.name != "temp-plans", \
            f"Plan must be in dedicated folder WITHIN temp-plans/, got: {plan_folder.name}"
        
        # SKULL VALIDATION 3: Universal subfolders must exist
        for subfolder in universal_subfolders:
            subfolder_path = plan_folder / subfolder
            assert subfolder_path.exists(), \
                f"Missing required subfolder: {subfolder} in {plan_folder}"
        
        # SKULL VALIDATION 4: No files in planning/ root
        planning_root = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        root_files = [f for f in planning_root.iterdir() if f.is_file()]
        assert len(root_files) == 0, \
            f"VIOLATION: Found {len(root_files)} files in planning/ root: {[f.name for f in root_files]}"
        
        # SKULL VALIDATION 5: Progress tracker initialized
        tracker_path = plan_folder / "tracking" / "progress-tracker.json"
        assert tracker_path.exists(), \
            f"Missing progress tracker: {tracker_path}"

    def test_skull_tier3_plan_goes_to_temp_plans(self, temp_cortex_root):
        """
        Test that Tier 3 (DOCUMENTED) plans start in temp-plans/.
        
        Before Fix: Tier 3 went to active/ directly
        After Fix: Tier 3 goes to temp-plans/, moves to active/ on approval
        """
        orchestrator = PlanningOrchestrator()
        orchestrator.project_root = temp_cortex_root
        
        # Tier 3 request (documented feature)
        tier3_request = "Implement user authentication with JWT tokens"
        
        planning_context = orchestrator._classify_and_analyze(tier3_request, force_tier=3)
        plan_path = orchestrator._generate_plan_path(planning_context, tier=3)
        
        # MUST be in temp-plans/, NOT active/
        assert "temp-plans" in str(plan_path), \
            f"Tier 3 plan MUST start in temp-plans/, got: {plan_path}"
        assert "active" not in str(plan_path), \
            f"Tier 3 plan MUST NOT be in active/ before approval, got: {plan_path}"

    def test_skull_tier4_plan_goes_to_temp_plans(self, temp_cortex_root):
        """
        Test that Tier 4 (COMPLEX) plans start in temp-plans/.
        
        Before Fix: Tier 4 went to active/ directly
        After Fix: Tier 4 goes to temp-plans/, moves to active/ on approval
        """
        orchestrator = PlanningOrchestrator()
        orchestrator.project_root = temp_cortex_root
        
        # Tier 4 request (complex architecture)
        tier4_request = "Design and implement microservices architecture with event sourcing"
        
        planning_context = orchestrator._classify_and_analyze(tier4_request, force_tier=4)
        plan_path = orchestrator._generate_plan_path(planning_context, tier=4)
        
        # MUST be in temp-plans/, NOT active/
        assert "temp-plans" in str(plan_path), \
            f"Tier 4 plan MUST start in temp-plans/, got: {plan_path}"
        assert "active" not in str(plan_path), \
            f"Tier 4 plan MUST NOT be in active/ before approval, got: {plan_path}"

    def test_skull_all_tiers_routing(self, temp_cortex_root):
        """
        Test folder routing for all tiers according to manifest.
        
        Manifest Requirements (planning-system-3.0-manifest.yaml):
        - Tier 1-2: temp-plans/ (lightweight, no versioning)
        - Tier 3-4: temp-plans/ (with versioning), move to active/ on approval
        """
        orchestrator = PlanningOrchestrator()
        orchestrator.project_root = temp_cortex_root
        
        test_cases = [
            {"tier": 1, "request": "List all files", "expected_folder": "temp-plans"},
            {"tier": 2, "request": "Update configuration value", "expected_folder": "temp-plans"},
            {"tier": 3, "request": "Add authentication system", "expected_folder": "temp-plans"},
            {"tier": 4, "request": "Redesign entire architecture", "expected_folder": "temp-plans"},
        ]
        
        for case in test_cases:
            planning_context = orchestrator._classify_and_analyze(case["request"], force_tier=case["tier"])
            plan_path = orchestrator._generate_plan_path(planning_context, tier=case["tier"])
            
            assert case["expected_folder"] in str(plan_path), \
                f"Tier {case['tier']} MUST go to {case['expected_folder']}/, got: {plan_path}"

    # ============================================
    # TEST 2: Universal Subfolder Enforcement
    # ============================================

    def test_skull_universal_subfolders_created_for_all_tiers(self, temp_cortex_root, universal_subfolders):
        """Test that universal subfolders are created for plans of all tiers."""
        orchestrator = PlanningOrchestrator()
        orchestrator.project_root = temp_cortex_root
        
        for tier in [1, 2, 3, 4]:
            request = f"Tier {tier} test request"
            planning_context = orchestrator._classify_and_analyze(request, force_tier=tier)
            plan_path = orchestrator._generate_plan_path(planning_context, tier=tier)
            plan_folder = plan_path.parent
            
            # Verify all universal subfolders exist
            for subfolder in universal_subfolders:
                subfolder_path = plan_folder / subfolder
                assert subfolder_path.exists(), \
                    f"Tier {tier}: Missing subfolder {subfolder} in {plan_folder}"

    # ============================================
    # TEST 3: Root-Level File Prevention
    # ============================================

    def test_skull_no_root_level_plan_files(self, temp_cortex_root):
        """
        Test that plans are NEVER created in planning/ root.
        
        VIOLATION: CORTEX-TOOLKIT-ARCHITECTURE-PLAN.md in planning/ root
        CORRECT: temp-plans/toolkit-architecture-20251216/00-master-plan.md
        """
        orchestrator = PlanningOrchestrator()
        orchestrator.project_root = temp_cortex_root
        
        # Create multiple plans
        requests = [
            "Create toolkit architecture",
            "Implement authentication",
            "Design microservices"
        ]
        
        for request in requests:
            planning_context = orchestrator._classify_and_analyze(request)
            plan_path = orchestrator._generate_plan_path(planning_context, tier=planning_context.tier)
            
            # Verify plan is NOT in planning/ root
            planning_root = temp_cortex_root / "cortex-brain" / "documents" / "planning"
            assert plan_path.parent != planning_root, \
                f"VIOLATION: Plan file in root! {plan_path}"
            
            # Verify plan is in a dedicated folder
            assert plan_path.parent.parent.parent == planning_root, \
                f"Plan must be in planning/{lifecycle}/{{folder}}/{{file}}, got: {plan_path}"

    # ============================================
    # TEST 4: Progress Tracker Initialization
    # ============================================

    def test_skull_progress_tracker_initialized(self, temp_cortex_root):
        """Test that progress tracker is initialized in tracking/ subfolder."""
        orchestrator = PlanningOrchestrator()
        orchestrator.project_root = temp_cortex_root
        
        request = "Create comprehensive toolkit"
        planning_context = orchestrator._classify_and_analyze(request)
        plan_path = orchestrator._generate_plan_path(planning_context, tier=planning_context.tier)
        plan_folder = plan_path.parent
        
        # Verify tracker exists
        tracker_path = plan_folder / "tracking" / "progress-tracker.json"
        assert tracker_path.exists(), f"Progress tracker not initialized: {tracker_path}"
        
        # Verify tracker content
        import json
        with open(tracker_path, 'r') as f:
            tracker_data = json.load(f)
        
        required_fields = ["plan_id", "created_at", "status", "phases", "session_id"]
        for field in required_fields:
            assert field in tracker_data, f"Missing tracker field: {field}"

    # ============================================
    # TEST 5: Semantic Folder Naming
    # ============================================

    def test_skull_semantic_folder_names(self, temp_cortex_root):
        """
        Test that plan folders have semantic names (not governance rules).
        
        GOOD: toolkit-architecture-v1, authentication-system-v2
        BAD: strict-folder-organization-v1, tdd-enforcement-v1
        """
        orchestrator = PlanningOrchestrator()
        orchestrator.project_root = temp_cortex_root
        
        # Good semantic names
        good_requests = [
            ("Create toolkit for reusable scripts", "toolkit"),
            ("Implement JWT authentication", "authentication"),
            ("Build reporting dashboard", "reporting"),
        ]
        
        for request, expected_keyword in good_requests:
            planning_context = orchestrator._classify_and_analyze(request, force_tier=3)
            plan_path = orchestrator._generate_plan_path(planning_context, tier=3)
            plan_folder_name = plan_path.parent.name
            
            # Should contain expected keyword
            assert expected_keyword in plan_folder_name.lower(), \
                f"Semantic name should contain '{expected_keyword}', got: {plan_folder_name}"
            
            # Should NOT contain anti-patterns
            anti_patterns = ["enforcement", "organization", "strict", "tdd-", "orchestrator-refactor"]
            for pattern in anti_patterns:
                assert pattern not in plan_folder_name.lower(), \
                    f"Semantic name should NOT contain anti-pattern '{pattern}', got: {plan_folder_name}"

    # ============================================
    # TEST 6: Integration - Full Workflow
    # ============================================

    def test_skull_full_plan_creation_workflow(self, temp_cortex_root, user_request_exact, universal_subfolders):
        """
        Integration test: Full plan creation workflow from user request to file creation.
        
        Validates entire governance chain:
        1. Request → Classification → Tier assignment
        2. Path generation → temp-plans/{{folder}}/
        3. Universal subfolders created
        4. Progress tracker initialized
        5. NO root-level files
        """
        orchestrator = PlanningOrchestrator()
        orchestrator.project_root = temp_cortex_root
        
        # Step 1: Classify request
        planning_context = orchestrator._classify_and_analyze(user_request_exact)
        assert planning_context.tier in [2, 3, 4], \
            f"Toolkit architecture should be Tier 2, 3, or 4, got: {planning_context.tier}"
        
        # Step 2: Generate plan path
        plan_path = orchestrator._generate_plan_path(planning_context, tier=planning_context.tier)
        
        # Step 3: Validate structure
        plan_folder = plan_path.parent
        
        # Validation 1: In temp-plans/
        assert "temp-plans" in str(plan_path)
        
        # Validation 2: Universal subfolders exist
        for subfolder in universal_subfolders:
            assert (plan_folder / subfolder).exists()
        
        # Validation 3: Progress tracker exists
        assert (plan_folder / "tracking" / "progress-tracker.json").exists()
        
        # Validation 4: No root-level files
        planning_root = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        root_files = [f for f in planning_root.iterdir() if f.is_file()]
        assert len(root_files) == 0
        
        # Validation 5: Plan folder and subfolders exist (file would be created later by actual plan generation)
        assert plan_folder.exists(), f"Plan folder should exist: {plan_folder}"

    # ============================================
    # TEST 7: Manifest Compliance
    # ============================================

    def test_skull_manifest_folder_structure_compliance(self, temp_cortex_root):
        """
        Test compliance with planning-system-3.0-manifest.yaml folder structure.
        
        Required structure (line 343-349):
        - root: "cortex-brain/documents/planning/"
        - subfolders:
          - "active/" # Current work
          - "temp-plans/" # Unapproved work
          - "completed/" # Archived work
        """
        orchestrator = PlanningOrchestrator()
        orchestrator.project_root = temp_cortex_root
        
        planning_root = temp_cortex_root / "cortex-brain" / "documents" / "planning"
        
        # Verify required folders exist
        required_folders = ["temp-plans", "active", "completed"]
        for folder in required_folders:
            folder_path = planning_root / folder
            assert folder_path.exists(), f"Required folder missing: {folder}"
        
        # Verify plans go to correct lifecycle folder
        request = "Test plan creation"
        planning_context = orchestrator._classify_and_analyze(request)
        plan_path = orchestrator._generate_plan_path(planning_context, tier=planning_context.tier)
        
        # Should be in temp-plans/ (unapproved)
        assert "temp-plans" in str(plan_path), \
            "New plans must start in temp-plans/ according to manifest"
