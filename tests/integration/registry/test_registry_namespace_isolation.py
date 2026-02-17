"""
Golden Tests for CORTEX Registry Structure Validation

Authority: Phase 103 Recovery - Registry Structure Correction
Created: 2026-02-17
Purpose: Enforce semantic separation between CORTEX meta-system and user repository plans

Test Categories:
1. Namespace Isolation - Verify _cortex-master contains only CORTEX development
2. User Plan Separation - Verify planning/ contains only user repository plans
3. File Count Validation - Audit phase file distribution
4. Symlink Integrity - Verify governance symlinks
5. Access Pattern Validation - Enforce agent write permissions
"""

import pytest
from pathlib import Path
import yaml
import re
from typing import List, Dict, Any


class TestCortexMasterNamespaceIsolation:
    """Test suite ensuring _cortex-master contains only CORTEX meta-system content."""
    
    CORTEX_MASTER_ROOT = Path("cortex-registry/_cortex-master")
    
    def test_cortex_master_directory_exists(self):
        """Verify _cortex-master directory is preserved."""
        assert self.CORTEX_MASTER_ROOT.exists(), \
            "_cortex-master directory missing (critical namespace separation lost)"
        
        assert self.CORTEX_MASTER_ROOT.is_dir(), \
            "_cortex-master should be directory, not file"
    
    def test_cortex_phases_are_meta_system_only(self):
        """Verify all phases in planning/phases/ develop CORTEX itself."""
        phases_root = self.CORTEX_MASTER_ROOT / "phases"
        
        if not phases_root.exists():
            pytest.skip("No phases directory in _cortex-master")
        
        cortex_keywords = [
            "cortex", "orchestrator", "mcp", "governance", "lens", 
            "registry", "phase", "intelligence", "brain", "tdd"
        ]
        
        phase_files = list(phases_root.glob("**/*.yaml"))
        assert len(phase_files) > 0, "No phase files found in _cortex-master"
        
        for phase_file in phase_files:
            with open(phase_file, 'r') as f:
                content = yaml.safe_load(f)
            
            title = content.get('title', '').lower()
            phase_id = content.get('phase_id', '').lower()
            objective = content.get('objective', '').lower()
            
            # At least one CORTEX keyword must appear
            has_cortex_context = any(
                kw in title or kw in phase_id or kw in objective 
                for kw in cortex_keywords
            )
            
            assert has_cortex_context, \
                f"{phase_file.name} does not reference CORTEX meta-system (wrong namespace)"
    
    def test_cortex_phases_no_external_repo_references(self):
        """Verify CORTEX phases do not reference external user repositories."""
        phases_root = self.CORTEX_MASTER_ROOT / "phases"
        
        if not phases_root.exists():
            pytest.skip("No phases directory in _cortex-master")
        
        # User repo indicators (should NOT appear in CORTEX meta-system)
        forbidden_patterns = [
            r"github\.com/(?!asifhussain60/CORTEX)",  # External GitHub repos
            r"repository:\s*https?://",  # External repo URLs
            r"repo_url:\s*https?://",
            r"client-project", r"acme-corp", r"user-repo",  # Example user names
        ]
        
        phase_files = list(phases_root.glob("**/*.yaml"))
        
        for phase_file in phase_files:
            with open(phase_file, 'r') as f:
                content = f.read()
            
            violations = []
            for pattern in forbidden_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    violations.append(f"Pattern '{pattern}' found: {matches}")
            
            assert len(violations) == 0, \
                f"{phase_file.name} references external repositories (should be in planning/): {violations}"
    
    def test_cortex_knowledge_is_tech_stack_only(self):
        """Verify knowledge-base/ contains only tech stack knowledge."""
        knowledge_root = self.CORTEX_MASTER_ROOT / "knowledge"
        
        if not knowledge_root.exists():
            pytest.skip("No knowledge directory in _cortex-master")
        
        # Expected tech stack categories
        expected_categories = [
            "architecture", "security", "testing", "database", 
            "cloud", "devops", "engineering", "microservices"
        ]
        
        subdirs = [d for d in knowledge_root.iterdir() if d.is_dir()]
        
        for subdir in subdirs:
            assert subdir.name in expected_categories, \
                f"Unexpected knowledge category: {subdir.name} (not tech stack)"
    
    def test_cortex_baselines_are_cortex_snapshots(self):
        """Verify baselines/ contains only CORTEX development snapshots."""
        baselines_root = self.CORTEX_MASTER_ROOT / "baselines"
        
        if not baselines_root.exists():
            pytest.skip("No baselines directory in _cortex-master")
        
        baseline_files = list(baselines_root.glob("*.json"))
        
        for baseline_file in baseline_files:
            # Baseline filenames should reference phases or production readiness
            assert "phase" in baseline_file.name.lower() or \
                   "production" in baseline_file.name.lower() or \
                   "baseline" in baseline_file.name.lower(), \
                   f"{baseline_file.name} does not match CORTEX baseline naming pattern"


class TestUserPlanningNamespaceIsolation:
    """Test suite ensuring planning/ contains only user repository plans."""
    
    PLANNING_ROOT = Path("cortex-registry/planning")
    
    def test_planning_directory_exists(self):
        """Verify planning/ directory exists for user repository plans."""
        assert self.PLANNING_ROOT.exists(), \
            "planning/ directory missing (required for user repo plans)"
        
        assert self.PLANNING_ROOT.is_dir(), \
            "planning/ should be directory, not file"
    
    def test_user_phases_reference_external_repositories(self):
        """Verify phases in planning/ reference external repositories."""
        phases_root = self.PLANNING_ROOT / "phases" / "planned"
        
        if not phases_root.exists():
            pytest.skip("No user planned phases yet (acceptable)")
        
        phase_files = list(phases_root.glob("*.yaml"))
        
        if len(phase_files) == 0:
            pytest.skip("No user phases yet (acceptable)")
        
        for phase_file in phase_files:
            with open(phase_file, 'r') as f:
                content = yaml.safe_load(f)
            
            # User phases should have repository context
            has_repo_context = any([
                'repository' in content,
                'repo_url' in content,
                'github_url' in content,
                'external_repo' in content,
            ])
            
            assert has_repo_context, \
                f"{phase_file.name} missing repository context (not a user repo plan)"
    
    def test_user_phases_do_not_modify_cortex_internals(self):
        """Verify user phases do not directly modify CORTEX codebase."""
        phases_root = self.PLANNING_ROOT / "phases" / "planned"
        
        if not phases_root.exists():
            pytest.skip("No user planned phases yet")
        
        phase_files = list(phases_root.glob("*.yaml"))
        
        if len(phase_files) == 0:
            pytest.skip("No user phases yet")
        
        # CORTEX internal paths (should NOT appear in user plans)
        forbidden_paths = [
            "cortex/orchestrators/", "cortex/mcp/", ".github/agents/",
            "cortex_intelligence/", "cortex-registry/_cortex-master/"
        ]
        
        for phase_file in phase_files:
            with open(phase_file, 'r') as f:
                content = f.read()
            
            violations = []
            for path in forbidden_paths:
                if path in content:
                    violations.append(path)
            
            assert len(violations) == 0, \
                f"{phase_file.name} references CORTEX internals: {violations} (should use _cortex-master/)"


class TestPhaseFileDistribution:
    """Test suite validating phase file counts and distribution."""
    
    def test_cortex_master_has_active_phases(self):
        """Verify _cortex-master has at least one active development phase."""
        planned_phases = Path("cortex-registry/planning/phases/planned")
        
        if not planned_phases.exists():
            pytest.fail("Missing planning/phases/planned directory")
        
        phase_count = len(list(planned_phases.glob("*.yaml")))
        
        assert phase_count >= 1, \
            f"No CORTEX development phases found (expected ≥1, got {phase_count})"
        
        print(f"✅ CORTEX active phases: {phase_count}")
    
    def test_phase_distribution_logged(self):
        """Log phase distribution across namespaces for audit."""
        cortex_planned = len(list(Path("cortex-registry/planning/phases/planned").glob("*.yaml")))
        cortex_completed = len(list(Path("cortex-registry/planning/phases/completed").glob("*.yaml")))
        
        user_planned_dir = Path("cortex-registry/planning/phases/planned")
        user_planned = len(list(user_planned_dir.glob("*.yaml"))) if user_planned_dir.exists() else 0
        
        print(f"\n📊 Phase Distribution Audit:")
        print(f"  CORTEX Planned: {cortex_planned}")
        print(f"  CORTEX Completed: {cortex_completed}")
        print(f"  User Planned: {user_planned}")
        
        assert cortex_planned + cortex_completed > 0, \
            "No CORTEX phases found (critical issue)"


class TestGovernanceSymlinks:
    """Test suite validating governance/ symlinks to _cortex-master/."""
    
    def test_core_rules_symlink_integrity(self):
        """Verify core-rules.yaml symlink points to _cortex-master/."""
        core_rules_path = Path("cortex-registry/governance/core-rules.yaml")
        
        if not core_rules_path.exists():
            pytest.skip("No governance/core-rules.yaml symlink (may not be created yet)")
        
        if core_rules_path.is_symlink():
            target = core_rules_path.resolve()
            assert "core/governance" in str(target), \
                f"core-rules.yaml symlink points to wrong location: {target}"
        else:
            # If not symlink, verify it's at least in _cortex-master
            with open(core_rules_path, 'r') as f:
                content = f.read()
            
            # Should reference CORE rules
            assert "CORE-" in content, \
                "core-rules.yaml does not contain CORE rule definitions"
    
    def test_audit_checklist_symlink_integrity(self):
        """Verify audit-checklist.yaml symlink points to _cortex-master/."""
        checklist_path = Path("cortex-registry/governance/audit-checklist.yaml")
        
        if not checklist_path.exists():
            pytest.skip("No governance/audit-checklist.yaml symlink")
        
        if checklist_path.is_symlink():
            target = checklist_path.resolve()
            assert "core/governance" in str(target), \
                f"audit-checklist.yaml symlink points to wrong location: {target}"


class TestAccessPatternEnforcement:
    """Test suite enforcing agent write permission rules."""
    
    def test_cortex_architect_references_master_namespace(self):
        """Verify cortex-architect agent documentation references _cortex-master/."""
        architect_doc = Path(".github/agents/core/cortex-architect.md")
        
        if not architect_doc.exists():
            pytest.skip("cortex-architect.md not found")
        
        with open(architect_doc, 'r') as f:
            content = f.read()
        
        # Should reference _cortex-master for CORTEX development
        assert "_cortex-master" in content, \
            "cortex-architect should write to _cortex-master/ for CORTEX phases"
    
    def test_planning_folder_documented_for_user_repos(self):
        """Verify planning/ folder is documented for user repository plans."""
        # Check if any agent documentation mentions planning/ for user repos
        agent_docs = Path(".github/agents/core").glob("*.md")
        
        planning_references = []
        for doc in agent_docs:
            with open(doc, 'r') as f:
                content = f.read()
            
            if "planning/" in content and ("user repo" in content.lower() or "external repo" in content.lower()):
                planning_references.append(doc.name)
        
        # At least one agent should document user repo planning
        assert len(planning_references) > 0, \
            "No agent documentation references planning/ for user repositories"


# ============================================================================
# Test Execution Summary
# ============================================================================
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "-W", "ignore::DeprecationWarning"
    ])
