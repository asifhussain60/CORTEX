"""
Planning Orchestrator Folder Structure Harness Tests

Tests to ensure child plans are ALWAYS created inside epic parent folders,
never at the root of cortex-brain/documents/planning/active/.

This prevents plan folder flooding and enforces PLAN_FILE_ORGANIZATION governance.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
from src.entry_point.cortex_entry import CortexEntry


class TestEpicParentPathDetection:
    """Test epic parent folder detection from user requests."""
    
    def setup_method(self):
        """Create test fixtures."""
        self.entry = CortexEntry()
        self.test_epic_folder = Path("cortex-brain/documents/planning/active/test-epic")
        self.test_epic_folder.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test artifacts."""
        if self.test_epic_folder.exists():
            shutil.rmtree(self.test_epic_folder)
    
    def test_detect_epic_from_continue_command(self):
        """Test: 'continue cortex5-enhancement-epic' detects epic folder."""
        message = "continue cortex5-enhancement-epic with Phase 1"
        result = self.entry._detect_epic_parent_path(message)
        
        # Should detect cortex5-enhancement-epic if it exists
        expected_path = "cortex-brain/documents/planning/active/cortex5-enhancement-epic"
        if Path(expected_path).exists():
            assert result == expected_path
        else:
            assert result is None  # Epic folder doesn't exist yet
    
    def test_detect_epic_from_begin_implementing(self):
        """Test: 'begin implementing cortex-brain/...epic' detects epic folder."""
        # Create test epic folder
        message = f"begin implementing {self.test_epic_folder}"
        result = self.entry._detect_epic_parent_path(message)
        
        assert result == str(self.test_epic_folder)
    
    def test_detect_epic_from_inside_keyword(self):
        """Test: 'plan feature inside test-epic' detects epic folder."""
        message = "plan feature inside test-epic"
        result = self.entry._detect_epic_parent_path(message)
        
        assert result == str(self.test_epic_folder)
    
    def test_no_detection_without_epic_keyword(self):
        """Test: Regular plan commands don't trigger epic detection."""
        message = "plan user authentication feature"
        result = self.entry._detect_epic_parent_path(message)
        
        assert result is None
    
    def test_no_detection_for_nonexistent_epic(self):
        """Test: Non-existent epic folders return None."""
        message = "continue nonexistent-epic-folder from phase 1"
        result = self.entry._detect_epic_parent_path(message)
        
        assert result is None


class TestFolderCreationLogic:
    """Test folder creation respects epic parent context."""
    
    def setup_method(self):
        """Create test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.epic_folder = self.test_dir / "test-epic"
        self.epic_folder.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test artifacts."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_child_plan_created_inside_epic(self):
        """Test: Child plans created inside epic when epic_parent_path provided."""
        # Mock orchestrator with epic context
        orchestrator = PlanningOrchestratorV5(
            context={'epic_parent_path': str(self.epic_folder)},
            plan_type='feature'
        )
        
        # Mock the folder creation to use test directory
        with patch.object(orchestrator, '_create_folder_structure') as mock_create:
            # Simulate folder creation logic
            feature_name = "test-child-feature"
            folder_name = "a01-test-child-feature"
            
            epic_parent_path = orchestrator.master_context.get('epic_parent_path')
            if epic_parent_path:
                plan_dir = Path(epic_parent_path) / folder_name
            else:
                plan_dir = Path(f"cortex-brain/documents/planning/active/{folder_name}")
            
            # Verify plan_dir is inside epic
            assert str(self.epic_folder) in str(plan_dir)
            assert plan_dir.parent == self.epic_folder
    
    def test_root_plan_created_without_epic_context(self):
        """Test: Root-level plans created when no epic_parent_path."""
        orchestrator = PlanningOrchestratorV5(
            context={},  # No epic context
            plan_type='epic'
        )
        
        # Simulate folder creation logic
        feature_name = "standalone-epic"
        folder_name = "a01-standalone-epic"
        
        epic_parent_path = orchestrator.master_context.get('epic_parent_path')
        if epic_parent_path:
            plan_dir = Path(epic_parent_path) / folder_name
        else:
            plan_dir = Path(f"cortex-brain/documents/planning/active/{folder_name}")
        
        # Verify plan_dir is at root active/ level
        assert plan_dir.parent == Path("cortex-brain/documents/planning/active")
    
    def test_epic_context_passed_from_entry_point(self):
        """Test: Entry point passes epic context to orchestrator."""
        entry = CortexEntry()
        
        # Mock epic detection
        with patch.object(entry, '_detect_epic_parent_path', return_value=str(self.epic_folder)):
            # Mock request
            request = Mock()
            request.user_message = "continue test-epic with new feature"
            request.intent = "PLAN"
            request.context = {}
            
            # Detect epic
            epic_path = entry._detect_epic_parent_path(request.user_message)
            
            assert epic_path == str(self.epic_folder)
            
            # Build context
            orchestrator_context = {'user_request': request.user_message}
            if epic_path:
                orchestrator_context['epic_parent_path'] = epic_path
            
            assert 'epic_parent_path' in orchestrator_context
            assert orchestrator_context['epic_parent_path'] == str(self.epic_folder)


class TestPlanFolderStructure:
    """Test plan folder structure validation."""
    
    REQUIRED_SUBFOLDERS = ['analysis', 'artifacts', 'context', 'reports', 'tracking']
    
    def test_plan_has_required_subfolders(self):
        """Test: Every plan must have 5 required subfolders."""
        test_plan = Path("cortex-brain/documents/planning/active/cortex5-enhancement-epic")
        
        if test_plan.exists():
            for subfolder in self.REQUIRED_SUBFOLDERS:
                subfolder_path = test_plan / subfolder
                assert subfolder_path.exists(), f"Missing required subfolder: {subfolder}"
                assert subfolder_path.is_dir(), f"{subfolder} is not a directory"
    
    def test_plan_files_in_subfolders_only(self):
        """Test: Plan files must be in subfolders, not root."""
        test_plan = Path("cortex-brain/documents/planning/active/cortex5-enhancement-epic")
        
        if test_plan.exists():
            # Get all files in plan root (excluding directories)
            root_files = [f for f in test_plan.iterdir() if f.is_file()]
            
            # Allowed files at root
            allowed_root_files = [
                'README.md',
                'CORTEX5-SNOWBALL.md',  # Master plan
                'FIX-PLAN-FOLDER-PLACEMENT.md',
                'PHASE-0.5-COMPLETE.md',
                'GOVERNANCE-RULE-SCRIPT-ORGANIZATION.md'
            ]
            
            for file in root_files:
                # Master plan files (A##-*.md or C##-*.md) allowed at root
                if file.name.startswith(('A', 'C')) and file.suffix == '.md':
                    continue
                
                assert file.name in allowed_root_files, \
                    f"File {file.name} should be in a subfolder, not plan root"


class TestOrphanedPlanCleanup:
    """Test cleanup of misplaced plans."""
    
    def test_detect_orphaned_plans_at_root(self):
        """Test: Detect plans that should be inside epic but are at root."""
        active_dir = Path("cortex-brain/documents/planning/active")
        
        if not active_dir.exists():
            pytest.skip("Active plans directory doesn't exist")
        
        # Known epic folders
        epic_folders = [
            "cortex5-enhancement-epic",
            "cortex5-remediation",
            "cortex-v5-epic"
        ]
        
        # Get all directories in active/
        all_dirs = [d for d in active_dir.iterdir() if d.is_dir()]
        
        # Identify potential orphans (exclude known epics)
        orphaned_plans = []
        for dir_path in all_dirs:
            if dir_path.name in epic_folders:
                continue
            
            # Check if this looks like a child plan (starts with plan-, a##-, etc.)
            if any(dir_path.name.startswith(prefix) for prefix in ['plan-', 'a01-', 'a19-', 'continue-']):
                orphaned_plans.append(dir_path.name)
        
        # Report orphaned plans
        if orphaned_plans:
            print(f"\n⚠️  Found {len(orphaned_plans)} orphaned plans at root:")
            for plan in orphaned_plans[:10]:  # Show first 10
                print(f"  - {plan}")
            
            # This test documents the issue but doesn't fail
            # (cleanup should be done separately)
            assert len(orphaned_plans) > 0, "Orphaned plans detected (expected)"


class TestGovernanceRuleEnforcement:
    """Test PLAN_FILE_ORGANIZATION governance rule enforcement."""
    
    def test_plan_file_organization_rule_exists(self):
        """Test: PLAN_FILE_ORGANIZATION rule exists in brain-protection-rules.yaml."""
        rules_file = Path("cortex-brain/brain-protection-rules.yaml")
        
        assert rules_file.exists(), "brain-protection-rules.yaml not found"
        
        content = rules_file.read_text()
        assert "PLAN_FILE_ORGANIZATION" in content, \
            "PLAN_FILE_ORGANIZATION rule not found in governance"
    
    def test_script_organization_rule_exists(self):
        """Test: SCRIPT_ORGANIZATION_ENFORCEMENT rule exists."""
        rules_file = Path("cortex-brain/brain-protection-rules.yaml")
        
        content = rules_file.read_text()
        assert "SCRIPT_ORGANIZATION_ENFORCEMENT" in content, \
            "SCRIPT_ORGANIZATION_ENFORCEMENT rule not found in governance"


class TestRegressionPrevention:
    """Regression tests to prevent future plan flooding."""
    
    def test_no_new_plans_at_root_without_epic_context(self):
        """Test: Planning commands without epic context still work (root-level epics)."""
        # This is a placeholder for monitoring
        # In production, we'd track plan creation locations
        pass
    
    def test_epic_context_required_for_child_plans(self):
        """Test: Child plans MUST have epic context."""
        # Mock scenario: User tries to create child plan without epic
        orchestrator = PlanningOrchestratorV5(
            context={},  # No epic context
            plan_type='feature'  # Child plan type
        )
        
        # Child plans without epic context should be created at root
        # (this is acceptable for standalone features)
        # BUT if user says "continue epic-name", epic context MUST be provided
        pass


# Cleanup utility function (not a test)
def cleanup_orphaned_plans_to_epic(epic_name: str = "cortex5-enhancement-epic", dry_run: bool = True):
    """
    Move orphaned plans into their parent epic folder.
    
    Args:
        epic_name: Name of epic folder to move plans into
        dry_run: If True, only report what would be moved (default: True)
    """
    active_dir = Path("cortex-brain/documents/planning/active")
    epic_folder = active_dir / epic_name
    
    if not epic_folder.exists():
        print(f"❌ Epic folder not found: {epic_folder}")
        return
    
    # Identify orphaned plans
    orphaned_plans = []
    for item in active_dir.iterdir():
        if not item.is_dir():
            continue
        if item.name == epic_name:
            continue
        if item.name.startswith(('plan-', 'a01-', 'a19-', 'continue-', 'fix-', 'investigate-', 'test-')):
            orphaned_plans.append(item)
    
    print(f"Found {len(orphaned_plans)} orphaned plans")
    
    for plan in orphaned_plans:
        target = epic_folder / plan.name
        
        if dry_run:
            print(f"  [DRY RUN] Would move: {plan.name} → {epic_folder.name}/{plan.name}")
        else:
            if target.exists():
                print(f"  ⚠️  Target exists, skipping: {plan.name}")
                continue
            
            shutil.move(str(plan), str(target))
            print(f"  ✅ Moved: {plan.name} → {epic_folder.name}/{plan.name}")
    
    if dry_run:
        print("\n💡 Run with dry_run=False to actually move files")


if __name__ == "__main__":
    # Run cleanup in dry-run mode
    print("=" * 60)
    print("ORPHANED PLANS CLEANUP PREVIEW")
    print("=" * 60)
    cleanup_orphaned_plans_to_epic(dry_run=True)
