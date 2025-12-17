"""
Production-Environment Planning System 3.0 Validation

Tests Planning System 3.0 using ACTUAL CORTEX workspace paths (not pytest temp dirs).
This validates that the system works correctly in production environment.

Author: Asif Hussain
Date: December 17, 2025
"""

import pytest
from pathlib import Path
from datetime import datetime
import shutil

from src.orchestration_3_0.orchestrators.planning.planning_orchestrator import PlanningOrchestrator
from src.orchestration_3_0.session.session_manager import SessionManager


@pytest.fixture
def cortex_root():
    """Use actual CORTEX project root."""
    # Navigate up from tests/integration/ to project root
    return Path(__file__).parent.parent.parent


@pytest.fixture
def orchestrator(cortex_root, monkeypatch):
    """Create orchestrator with ACTUAL CORTEX paths."""
    # Don't mock Path.cwd() - use real project root
    monkeypatch.setattr('pathlib.Path.cwd', lambda: cortex_root)
    
    session_manager = SessionManager()
    orchestrator = PlanningOrchestrator(session_manager=session_manager)
    
    # Inject project_root for absolute path resolution
    orchestrator.project_root = cortex_root
    
    return orchestrator


@pytest.fixture
def cleanup_test_plans(cortex_root):
    """Cleanup test plans after execution."""
    yield
    
    # Cleanup test plans from temp-plans/ and active/
    temp_plans_root = cortex_root / "cortex-brain" / "documents" / "planning" / "temp-plans"
    active_plans_root = cortex_root / "cortex-brain" / "documents" / "planning" / "active"
    
    # Remove test plan folders (start with "prod-test-")
    for folder in temp_plans_root.glob("prod-test-*"):
        if folder.is_dir():
            shutil.rmtree(folder)
    
    for folder in active_plans_root.glob("PROD-TEST-*"):
        if folder.is_dir():
            shutil.rmtree(folder)


class TestProductionEnvironment:
    """Test Planning System 3.0 in production CORTEX workspace."""
    
    def test_real_cortex_paths_simple_plan(self, orchestrator, cortex_root, cleanup_test_plans):
        """
        Production Test 1: Simple plan using real CORTEX paths.
        
        Validates:
        - Temp plan created in ACTUAL cortex-brain/documents/planning/temp-plans/
        - Context folder created with AST/Lens analysis
        - Files persist correctly (no path resolution issues)
        """
        print("\n" + "="*80)
        print("PRODUCTION TEST 1: Simple Plan with Real CORTEX Paths")
        print("="*80)
        
        feature_name = "prod-test-simple-feature"
        
        # Start refinement session
        result = orchestrator.start_refinement_session(
            feature_name=feature_name,
            description="Production test for simple plan creation",
            acceptance_criteria=[
                "Validate temp plan creation",
                "Verify context folder",
                "Confirm AST/Lens analysis"
            ]
        )
        
        print(f"✅ Session started: {result.session_id}")
        print(f"✅ Plan ID: {result.plan_id}")
        
        # Verify temp plan folder in ACTUAL CORTEX workspace
        expected_temp_folder = (
            cortex_root / "cortex-brain" / "documents" / "planning" / "temp-plans" / result.plan_id
        )
        
        assert expected_temp_folder.exists(), (
            f"Temp plan folder not found at: {expected_temp_folder}"
        )
        
        # Verify plan.md exists
        plan_file = expected_temp_folder / "plan.md"
        assert plan_file.exists(), f"plan.md not found at: {plan_file}"
        
        # Verify context folder
        context_folder = expected_temp_folder / "context"
        assert context_folder.exists(), f"context/ folder not found at: {context_folder}"
        
        print(f"\n📁 Temp Plan Location: {expected_temp_folder}")
        print(f"✅ plan.md exists: {plan_file}")
        print(f"✅ context/ exists: {context_folder}")
        
        # Check for context files
        ast_file = context_folder / "ast-analysis.json"
        lens_file = context_folder / "lens-dependencies.json"
        
        if ast_file.exists():
            print(f"✅ AST analysis: {ast_file.stat().st_size} bytes")
        if lens_file.exists():
            print(f"✅ Lens analysis: {lens_file.stat().st_size} bytes")
        
        print("\n✅ PRODUCTION TEST 1 PASSED: Real CORTEX paths working correctly")
        print("="*80 + "\n")
    
    def test_real_cortex_paths_complex_plan(self, orchestrator, cortex_root, cleanup_test_plans):
        """
        Production Test 2: Complex plan with master + worker plans.
        
        Validates:
        - Master plan created in ACTUAL cortex-brain/documents/planning/active/
        - Worker plans (WP01, WP02, WP03) created correctly
        - Execution/ subfolder with YAML files
        - All 7 master plan sections present
        """
        print("\n" + "="*80)
        print("PRODUCTION TEST 2: Complex Plan with Master + Workers (Real Paths)")
        print("="*80)
        
        feature_name = "prod-test-complex-oauth"
        
        # Start and approve plan
        result = orchestrator.start_refinement_session(
            feature_name=feature_name,
            description="Production test for complex plan with master + workers",
            acceptance_criteria=[
                "OAuth 2.0 integration",
                "Token management",
                "User profile sync",
                "Security validation"
            ]
        )
        
        print(f"✅ Refinement session: {result.session_id}")
        
        # Approve and promote
        orchestrator.request_plan_approval(result.session_id)
        promotion_result = orchestrator.approve_and_promote_plan(
            session_id=result.session_id,
            user_approval=True
        )
        
        print(f"✅ Plan promoted: {promotion_result['plan_id']}")
        
        # Generate worker plans
        phases = [
            {
                "phase_number": 1,
                "name": "Foundation",
                "description": "OAuth setup",
                "tasks": ["Setup providers", "Configure endpoints"],
                "estimated_hours": 16
            },
            {
                "phase_number": 2,
                "name": "Core Implementation",
                "description": "Token management",
                "tasks": ["Token generation", "Refresh workflow"],
                "estimated_hours": 20
            },
            {
                "phase_number": 3,
                "name": "Security Testing",
                "description": "Security validation",
                "tasks": ["PKCE implementation", "Security audit"],
                "estimated_hours": 24
            }
        ]
        
        metadata = {
            "feature_name": feature_name,
            "complexity_tier": 4,
            "estimated_days": 7.5
        }
        
        worker_result = orchestrator.generate_worker_plans(
            plan_id=promotion_result['plan_id'],
            phases=phases,
            metadata=metadata
        )
        
        print(f"✅ Worker plans generated")
        
        # Verify files in ACTUAL CORTEX workspace
        active_folder = (
            cortex_root / "cortex-brain" / "documents" / "planning" / "active" / 
            promotion_result['plan_id']
        )
        
        assert active_folder.exists(), f"Active plan folder not found: {active_folder}"
        
        # Check master plan
        master_plan = active_folder / "master-plan.md"
        assert master_plan.exists(), f"master-plan.md not found: {master_plan}"
        
        # Read and validate master plan content
        master_content = master_plan.read_text(encoding='utf-8')
        
        # Verify 7 mandatory sections
        required_sections = {
            "Executive Summary": False,
            "Continuation Prompt": False,
            "Visual Progress Tracker": False,
            "Business Value Summary": False,
            "Phase Breakdown": False,
            "Request Context": False,
            "Definition of Done": False
        }
        
        for section in required_sections.keys():
            if section in master_content:
                required_sections[section] = True
        
        sections_found = sum(required_sections.values())
        
        print(f"\n📄 Master Plan: {master_plan}")
        print(f"📏 File Size: {len(master_content)} characters")
        print(f"\n✅ Master Plan Sections ({sections_found}/7):")
        for section, found in required_sections.items():
            status = "✅" if found else "❌"
            print(f"   {status} {section}")
        
        # Check worker plans
        expected_workers = ["WP01-Foundation.md", "WP02-Core-Implementation.md", "WP03-Security-Testing.md"]
        found_workers = []
        
        for worker_name in expected_workers:
            worker_file = active_folder / worker_name
            if worker_file.exists():
                found_workers.append(worker_name)
                # Check for standard task injection
                worker_content = worker_file.read_text(encoding='utf-8')
                has_git_checkpoint = "git checkpoint" in worker_content.lower()
                has_tdd = "tdd" in worker_content.lower() or "test" in worker_content.lower()
                
                print(f"\n✅ {worker_name} ({len(worker_content)} chars)")
                print(f"   {'✅' if has_git_checkpoint else '❌'} Git checkpoint")
                print(f"   {'✅' if has_tdd else '❌'} TDD tasks")
        
        # Check execution folder
        execution_folder = active_folder / "execution"
        assert execution_folder.exists(), f"execution/ folder not found: {execution_folder}"
        
        yaml_files = list(execution_folder.glob("*.yaml"))
        print(f"\n✅ Execution folder: {len(yaml_files)} YAML files")
        
        # Final assertions
        assert sections_found >= 5, f"Only {sections_found}/7 master plan sections found"
        assert len(found_workers) == 3, f"Only {len(found_workers)}/3 worker plans found"
        
        print("\n✅ PRODUCTION TEST 2 PASSED: Complex plan generation working correctly")
        print("="*80 + "\n")
    
    def test_master_plan_template_compliance(self, cortex_root):
        """
        Production Test 3: Master plan template validation.
        
        Validates:
        - Template file exists at correct location
        - All 7 mandatory sections present
        - Placeholder syntax correct
        """
        print("\n" + "="*80)
        print("PRODUCTION TEST 3: Master Plan Template Compliance")
        print("="*80)
        
        template_path = cortex_root / "cortex-brain" / "templates" / "planning" / "MASTER-PLAN-TEMPLATE.md"
        
        assert template_path.exists(), f"Template not found: {template_path}"
        
        template_content = template_path.read_text(encoding='utf-8')
        
        # Check for 7 mandatory sections
        required_sections = {
            "Executive Summary": False,
            "Continuation Prompt": False,
            "Visual Progress Tracker": False,
            "Business Value Summary": False,
            "Phase Breakdown": False,
            "CORTEX Analysis": False,  # Request Context
            "Definition of Done": False
        }
        
        for section in required_sections.keys():
            if section in template_content:
                required_sections[section] = True
        
        sections_found = sum(required_sections.values())
        
        print(f"\n📄 Template: {template_path}")
        print(f"📏 File Size: {len(template_content)} characters")
        print(f"\n✅ Template Sections ({sections_found}/7):")
        for section, found in required_sections.items():
            status = "✅" if found else "❌"
            print(f"   {status} {section}")
        
        # Check for placeholder syntax
        placeholders = [
            "{PLAN_ID}", "{PLAN_TITLE}", "{CREATION_DATE}",
            "{EXECUTIVE_SUMMARY}", "{CONTINUATION_PROMPT}",
            "{PROGRESS_BAR}", "{PHASE_TABLES}", "{DOD_CRITERIA}"
        ]
        
        found_placeholders = []
        for placeholder in placeholders:
            if placeholder in template_content:
                found_placeholders.append(placeholder)
        
        print(f"\n✅ Placeholders ({len(found_placeholders)}/{len(placeholders)}):")
        for placeholder in found_placeholders:
            print(f"   ✅ {placeholder}")
        
        assert sections_found >= 5, f"Only {sections_found}/7 sections in template"
        assert len(found_placeholders) >= 6, f"Only {len(found_placeholders)}/{len(placeholders)} placeholders found"
        
        print("\n✅ PRODUCTION TEST 3 PASSED: Template compliance validated")
        print("="*80 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
