"""
Git History Analyzer for CORTEX Total Recall
Tracks changes since last pull to ensure prompt reflects current implementation.

AC-ID: AC-TOTAL-RECALL-GIT-001
Purpose: Auto-detect governance changes, orchestrator changes, AC-PERMANENT-FIX commits

This prevents stale prompt data like:
- Hardcoded "29 rules" when actually 21
- Missing governance simplification detection
- No post-sync validation
"""

import subprocess
import re
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class GitChangeAnalysis:
    """Analysis of git changes affecting CORTEX system state."""
    
    # Governance changes
    governance_changes: bool = False
    rules_before: int = 0
    rules_after: int = 0
    deleted_rules: List[str] = field(default_factory=list)
    added_rules: List[str] = field(default_factory=list)
    
    # Orchestrator changes
    orchestrator_changes: bool = False
    wired_before: int = 0
    wired_after: int = 0
    new_orchestrators: List[str] = field(default_factory=list)
    removed_orchestrators: List[str] = field(default_factory=list)
    
    # AC-PERMANENT-FIX commits
    ac_permanent_fix_commits: List[Dict[str, str]] = field(default_factory=list)
    
    # Validation triggers
    requires_revalidation: bool = False
    change_summary: str = ""


class GitHistoryAnalyzer:
    """
    Analyzes git history to detect changes requiring prompt updates.
    
    Usage:
        analyzer = GitHistoryAnalyzer()
        changes = analyzer.analyze_since_last_pull()
        if changes.requires_revalidation:
            # Trigger full system validation
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize analyzer with repository path."""
        self.repo_path = repo_path or Path.cwd()
        
    def analyze_since_last_pull(
        self,
        track_patterns: Optional[List[str]] = None,
        hours_back: int = 24
    ) -> GitChangeAnalysis:
        """
        Analyze git commits since last pull.
        
        Args:
            track_patterns: Patterns to search in commit messages
            hours_back: How many hours of history to analyze
            
        Returns:
            GitChangeAnalysis with detected changes
        """
        if track_patterns is None:
            track_patterns = [
                "governance simplification",
                "AC-PERMANENT-FIX",
                "orchestrator.*wiring",
                "CORE-\\d+",
                "rule.*delet",
                "VACUUM"
            ]
        
        analysis = GitChangeAnalysis()
        
        # Get recent commits
        since_time = f"{hours_back} hours ago"
        commits = self._get_commits_since(since_time)
        
        # Analyze commits for patterns
        for commit in commits:
            commit_msg = commit.get("message", "").lower()
            
            # Check for governance changes
            if any(re.search(pattern.lower(), commit_msg) for pattern in ["governance", "rule", "CORE-"]):
                analysis.governance_changes = True
                
            # Check for AC-PERMANENT-FIX commits
            if "ac-permanent-fix" in commit_msg:
                analysis.ac_permanent_fix_commits.append({
                    "commit_hash": commit.get("hash", "")[:8],
                    "title": commit.get("message", "").split('\n')[0],
                    "date": commit.get("date", "")
                })
                
            # Check for orchestrator changes
            if any(re.search(pattern.lower(), commit_msg) for pattern in ["orchestrator", "wiring", "wire-"]):
                analysis.orchestrator_changes = True
        
        # Get current state
        current_rules = self._get_current_rule_count()
        current_orchestrators = self._get_current_orchestrator_count()
        
        analysis.rules_after = current_rules
        analysis.wired_after = current_orchestrators
        
        # Determine if revalidation needed
        analysis.requires_revalidation = (
            analysis.governance_changes or
            analysis.orchestrator_changes or
            len(analysis.ac_permanent_fix_commits) > 0
        )
        
        # Generate summary
        summary_parts = []
        if analysis.governance_changes:
            summary_parts.append(f"Governance: {analysis.rules_after} rules active")
        if analysis.orchestrator_changes:
            summary_parts.append(f"Orchestrators: {analysis.wired_after} wired")
        if analysis.ac_permanent_fix_commits:
            summary_parts.append(f"AC-PERMANENT-FIX: {len(analysis.ac_permanent_fix_commits)} commits")
            
        analysis.change_summary = " | ".join(summary_parts) if summary_parts else "No significant changes"
        
        return analysis
    
    def _get_commits_since(self, since: str) -> List[Dict[str, str]]:
        """Get commits since specified time."""
        try:
            result = subprocess.run(
                ["git", "log", f"--since={since}", "--pretty=format:%H|%s|%ai"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 3:
                    commits.append({
                        "hash": parts[0],
                        "message": parts[1],
                        "date": parts[2]
                    })
            return commits
            
        except subprocess.CalledProcessError:
            return []
    
    def _get_current_rule_count(self) -> int:
        """Get current count of governance rules."""
        rules_file = self.repo_path / "cortex_brain" / "tier0" / "governance" / "core-rules.yaml"
        if not rules_file.exists():
            return 0
            
        try:
            content = rules_file.read_text()
            rules = re.findall(r'rule_id: (CORE-\d+)', content)
            return len(set(rules))
        except Exception:
            return 0
    
    def _get_current_orchestrator_count(self) -> int:
        """Get current count of wired orchestrators.
        
        Updated: 2026-01-25 - AC-PERMANENT-FIX-010: Use DatabaseBackedRegistry as primary
        """
        # Primary: Use DatabaseBackedRegistry (SSOT)
        try:
            from cortex.orchestrators import get_database_registry
            
            registry = get_database_registry()
            stats = registry.get_wiring_statistics()
            return stats.get('total_wired', 0)
        except ImportError:
            pass
        
        # Fallback: Read from YAML (legacy)
        registry_file = self.repo_path / "cortex_brain" / "tier0" / "repo-registry.yaml"
        if not registry_file.exists():
            return 0
            
        try:
            data = yaml.safe_load(registry_file.read_text())
            orchestrators = data.get('registered_orchestrators', [])
            wired = sum(1 for o in orchestrators if o.get('wiring_status') == 'wired')
            return wired
        except Exception:
            return 0
    
    def validate_ac_permanent_fixes(self) -> Dict[str, bool]:
        """
        Validate all AC-PERMANENT-FIX commits are still active.
        
        Updated: 2026-01-25 - AC-PERMANENT-FIX-010: Check DatabaseBackedRegistry first
        
        Returns:
            Dict mapping fix_id to validation status
        """
        validations = {}
        
        # AC-PERMANENT-FIX-001: Registry is healthy (check DB first)
        try:
            from cortex.orchestrators import get_database_registry
            
            registry = get_database_registry()
            stats = registry.get_wiring_statistics()
            validations['AC-PERMANENT-FIX-001'] = stats.get('total_wired', 0) >= 18
        except ImportError:
            # Fallback to YAML check
            registry_file = self.repo_path / "cortex_brain" / "tier0" / "repo-registry.yaml"
            if registry_file.exists():
                try:
                    data = yaml.safe_load(registry_file.read_text())
                    validations['AC-PERMANENT-FIX-001'] = not data.get('registry_template', True)
                except Exception:
                    validations['AC-PERMANENT-FIX-001'] = False
            else:
                validations['AC-PERMANENT-FIX-001'] = False
        
        # AC-PERMANENT-FIX-002: Verification files exist
        verify_files = [
            self.repo_path / "cortex" / "tools" / "verify_registry.py",
            self.repo_path / "cortex" / "tools" / "test_fix_verification.py"
        ]
        validations['AC-PERMANENT-FIX-002'] = all(f.exists() for f in verify_files)
        
        # AC-PERMANENT-FIX-003: Documentation exists
        doc_file = self.repo_path / "docs" / "ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md"
        validations['AC-PERMANENT-FIX-003'] = doc_file.exists()
        
        # AC-PERMANENT-FIX-004: Transformation complete
        validations['AC-PERMANENT-FIX-004'] = all(validations.values())
        
        # AC-PERMANENT-FIX-005: CORE-030 rule active (implementation truth enforcement)
        core_rules = self.repo_path / "cortex_brain" / "tier0" / "governance" / "core-rules.yaml"
        if core_rules.exists():
            try:
                content = core_rules.read_text()
                validations['AC-PERMANENT-FIX-005'] = 'CORE-030' in content and 'Implementation Truth Enforcement' in content
            except Exception:
                validations['AC-PERMANENT-FIX-005'] = False
        else:
            validations['AC-PERMANENT-FIX-005'] = False
        
        # AC-PERMANENT-FIX-006: Challenge system active in InteractionOrchestrator
        interaction_orch = self.repo_path / "cortex" / "orchestrators" / "core" / "interaction_orchestrator.py"
        challenge_engine = self.repo_path / "cortex" / "orchestrators" / "core" / "challenge_engine.py"
        if interaction_orch.exists() and challenge_engine.exists():
            try:
                orch_content = interaction_orch.read_text()
                # Check for challenge system integration
                has_challenge_import = 'from cortex.orchestrators.core.challenge_engine import' in orch_content
                has_challenge_method = 'execute_turn_with_challenge' in orch_content
                has_enable_flag = 'enable_challenges' in orch_content
                validations['AC-PERMANENT-FIX-006'] = all([
                    has_challenge_import,
                    has_challenge_method,
                    has_enable_flag,
                    challenge_engine.exists()
                ])
            except Exception:
                validations['AC-PERMANENT-FIX-006'] = False
        else:
            validations['AC-PERMANENT-FIX-006'] = False
        
        # AC-PERMANENT-FIX-007: Single Canonical Implementation (CORE-035)
        # Ensures no duplicate/competing implementations exist
        forbidden_patterns = [
            '*_unified.py', '*_refactored.py', '*_v2.py', '*_v3.py',
            '*_alternative.py', '*_new.py', '*_old.py', '*_legacy.py', '*_backup.py'
        ]
        cortex_dir = self.repo_path / "cortex"
        duplicate_files = []
        if cortex_dir.exists():
            for pattern in forbidden_patterns:
                # Use glob to find matching files
                matches = list(cortex_dir.rglob(pattern))
                duplicate_files.extend(matches)
        
        validations['AC-PERMANENT-FIX-007'] = len(duplicate_files) == 0
        
        return validations


# Convenience function for quick analysis
def analyze_recent_changes(hours_back: int = 24) -> GitChangeAnalysis:
    """Quick analysis of recent changes."""
    analyzer = GitHistoryAnalyzer()
    return analyzer.analyze_since_last_pull(hours_back=hours_back)


if __name__ == "__main__":
    # CLI usage
    import sys
    
    analyzer = GitHistoryAnalyzer()
    changes = analyzer.analyze_since_last_pull(hours_back=24)
    
    print("=" * 60)
    print("GIT HISTORY ANALYSIS - CORTEX Total Recall")
    print("=" * 60)
    print(f"\nChange Summary: {changes.change_summary}")
    print(f"Requires Revalidation: {changes.requires_revalidation}")
    
    if changes.governance_changes:
        print(f"\n⚠️  GOVERNANCE CHANGES DETECTED")
        print(f"  Current Rules: {changes.rules_after}")
        
    if changes.orchestrator_changes:
        print(f"\n⚠️  ORCHESTRATOR CHANGES DETECTED")
        print(f"  Current Wired: {changes.wired_after}")
        
    if changes.ac_permanent_fix_commits:
        print(f"\n⚠️  AC-PERMANENT-FIX COMMITS ({len(changes.ac_permanent_fix_commits)})")
        for fix in changes.ac_permanent_fix_commits:
            print(f"  - {fix['commit_hash']}: {fix['title']}")
    
    # Validate AC-PERMANENT-FIX status
    print(f"\n{'='*60}")
    print("AC-PERMANENT-FIX VALIDATION")
    print("=" * 60)
    validations = analyzer.validate_ac_permanent_fixes()
    for fix_id, is_valid in validations.items():
        status = "✅ ACTIVE" if is_valid else "❌ VIOLATED"
        print(f"{fix_id}: {status}")
    
    # Exit code based on validation
    if not all(validations.values()):
        print("\n❌ AC-PERMANENT-FIX REGRESSION DETECTED!")
        sys.exit(1)
    else:
        print("\n✅ ALL AC-PERMANENT-FIX VALIDATIONS PASSED")
        sys.exit(0)
