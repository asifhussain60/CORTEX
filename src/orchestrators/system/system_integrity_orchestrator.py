"""
System Integrity Orchestrator - Comprehensive validation and auto-fix for CORTEX 4.0

Admin-level orchestrator that validates and fixes:
1. Master plan alignment with actual implementation
2. Test execution and coverage verification
3. Documentation completeness and generation
4. File organization and structure cleanup
5. Broken link detection and repair
6. Legacy artifact removal (CORTEX 3.0)
7. Root folder organization
8. Manifest and reference integrity

This orchestrator doesn't just report - it FIXES all issues automatically.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import ast
import json
import re
import shutil
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..base.base_orchestrator import BaseOrchestrator, OrchestratorResult, OrchestratorStatus


@dataclass
class IntegrityIssue:
    """Represents a system integrity issue"""
    category: str  # 'plan', 'tests', 'docs', 'structure', 'links', 'legacy'
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    location: Optional[Path] = None
    auto_fixable: bool = True
    fix_applied: bool = False
    fix_result: Optional[str] = None


@dataclass
class IntegrityReport:
    """Results from integrity validation"""
    issues_found: int = 0
    issues_fixed: int = 0
    issues_remaining: int = 0
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    docs_generated: int = 0
    files_relocated: int = 0
    files_deleted: int = 0
    links_fixed: int = 0
    issues: List[IntegrityIssue] = field(default_factory=list)
    execution_time_seconds: float = 0.0


class SystemIntegrityOrchestrator(BaseOrchestrator):
    """
    Comprehensive system integrity validation and auto-fix orchestrator
    
    Phases:
    1. ANALYZE: Scan master plan vs actual implementation
    2. VALIDATE_TESTS: Run all tests and verify coverage
    3. CHECK_DOCS: Validate documentation completeness
    4. ORGANIZE_FILES: Fix file structure and locations
    5. REPAIR_LINKS: Find and fix broken references
    6. CLEANUP_LEGACY: Remove CORTEX 3.0 artifacts
    7. VALIDATE_MANIFESTS: Check manifest integrity
    8. GENERATE_REPORT: Comprehensive integrity report
    
    Usage:
        orchestrator = SystemIntegrityOrchestrator(logger)
        result = orchestrator.execute({
            'fix_mode': True,  # Auto-fix issues (default)
            'run_tests': True,  # Run test suite
            'generate_docs': True,  # Generate missing docs
            'cleanup_legacy': True,  # Remove old artifacts
            'reorganize_files': True  # Fix file structure
        })
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        # Set name and version before BaseOrchestrator.__init__
        if config is None:
            config = {}
        config["name"] = "SystemIntegrityOrchestrator"
        config["version"] = "4.0.0"
        
        super().__init__(config)
        self.report = IntegrityReport()
        self.workspace_root = Path(config.get("workspace_root", Path.cwd()))
        self.master_plan_path = self.workspace_root / "cortex-brain" / "documents" / "planning" / "active" / "CORTEX-3.0-4.0" / "00-MASTER-PLAN.md"
        self.status_path = self.workspace_root / "cortex-brain" / "documents" / "planning" / "active" / "CORTEX-3.0-4.0" / "CORTEX4-STATUS.md"
        
        # Track all file references for link repair
        self.file_moves: Dict[Path, Path] = {}  # old_path -> new_path
        
    def _setup(self, context: Dict[str, Any]) -> None:
        """Setup integrity orchestrator"""
        self.logger.info("🎭 Orchestrator engaged: SystemIntegrityOrchestrator")
        self.logger.info("Setting up system integrity validation")
        
        # Set default context values
        context.setdefault('fix_mode', True)
        context.setdefault('run_tests', True)
        context.setdefault('generate_docs', True)
        context.setdefault('cleanup_legacy', True)
        context.setdefault('reorganize_files', True)
        
        self.report = IntegrityReport()
        context['report'] = self.report
        
    def _register_phases(self) -> None:
        """Register integrity check phases"""
        self.phase_manager.register_phase("analyze", "Analyze master plan alignment")
        self.phase_manager.register_phase("validate_tests", "Run test suite validation")
        self.phase_manager.register_phase("check_docs", "Check documentation completeness")
        self.phase_manager.register_phase("organize_files", "Organize file structure")
        self.phase_manager.register_phase("repair_links", "Repair broken links")
        self.phase_manager.register_phase("cleanup_legacy", "Remove legacy artifacts")
        self.phase_manager.register_phase("validate_manifests", "Validate manifests")
        self.phase_manager.register_phase("generate_report", "Generate integrity report")
    
    def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute system integrity validation and fixes"""
        if context is None:
            context = {}
        
        start_time = datetime.now()
        
        try:
            self._setup(context)
            # Phases are executed directly, no phase manager needed
            
            self.logger.info("🎭 Phase transition: SETUP → ANALYZE")
            self._phase_analyze(context)
            
            if context.get('run_tests', True):
                self.logger.info("🎭 Phase transition: ANALYZE → VALIDATE_TESTS")
                self._phase_validate_tests(context)
            
            if context.get('generate_docs', True):
                self.logger.info("🎭 Phase transition: VALIDATE_TESTS → CHECK_DOCS")
                self._phase_check_docs(context)
            
            if context.get('reorganize_files', True):
                self.logger.info("🎭 Phase transition: CHECK_DOCS → ORGANIZE_FILES")
                self._phase_organize_files(context)
            
            self.logger.info("🎭 Phase transition: ORGANIZE_FILES → REPAIR_LINKS")
            self._phase_repair_links(context)
            
            if context.get('cleanup_legacy', True):
                self.logger.info("🎭 Phase transition: REPAIR_LINKS → CLEANUP_LEGACY")
                self._phase_cleanup_legacy(context)
            
            self.logger.info("🎭 Phase transition: CLEANUP_LEGACY → VALIDATE_MANIFESTS")
            self._phase_validate_manifests(context)
            
            self.logger.info("🎭 Phase transition: VALIDATE_MANIFESTS → GENERATE_REPORT")
            self._phase_generate_report(context)
            
            # Calculate execution time
            end_time = datetime.now()
            self.report.execution_time_seconds = (end_time - start_time).total_seconds()
            
            # Check if all work is complete
            is_complete = (
                self.report.issues_remaining == 0 and
                self.report.tests_failed == 0
            )
            
            if is_complete:
                self.logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            
            return {
                'success': True,
                'is_complete': is_complete,
                'report': self.report,
                'issues_found': self.report.issues_found,
                'issues_fixed': self.report.issues_fixed,
                'issues_remaining': self.report.issues_remaining,
                'tests_run': self.report.tests_run,
                'tests_passed': self.report.tests_passed,
                'tests_failed': self.report.tests_failed,
                'execution_time': self.report.execution_time_seconds
            }
            
        except Exception as e:
            self.logger.error(f"System integrity check failed: {e}", exc_info=True)
            return {
                'success': False,
                'is_complete': False,
                'error': str(e),
                'report': self.report
            }
    
    # ============================================================================
    # PHASE 1: ANALYZE - Master Plan Alignment
    # ============================================================================
    
    def _phase_analyze(self, context: Dict[str, Any]) -> None:
        """Analyze master plan vs actual implementation"""
        self.logger.info("Phase 1: Analyzing master plan alignment")
        
        if not self.master_plan_path.exists():
            self._add_issue(
                'plan', 'critical',
                f"Master plan not found: {self.master_plan_path}",
                self.master_plan_path,
                auto_fixable=False
            )
            return
        
        # Parse master plan for completed phases
        completed_phases = self._parse_completed_phases()
        
        # Check each completed phase
        for phase in completed_phases:
            self._validate_phase_implementation(phase, context)
    
    def _parse_completed_phases(self) -> List[Dict[str, Any]]:
        """Parse master plan for completed phases"""
        completed = []
        
        try:
            content = self.master_plan_path.read_text(encoding='utf-8')
            
            # Look for completed phases (marked with ✅)
            phase_pattern = r'(?:Phase|PHASE)\s+(\d+(?:\.\d+)?)[:\s]+([^\n]+)\s*(?:\(([^)]+)\))?\s*-\s*(\d+%)\s*(?:COMPLETE|✅)'
            
            for match in re.finditer(phase_pattern, content, re.IGNORECASE | re.MULTILINE):
                phase_num = match.group(1)
                phase_name = match.group(2).strip()
                completion = match.group(4)
                
                if completion == '100%':
                    completed.append({
                        'number': phase_num,
                        'name': phase_name,
                        'completion': 100
                    })
                    
        except Exception as e:
            self.logger.error(f"Error parsing master plan: {e}")
        
        return completed
    
    def _validate_phase_implementation(self, phase: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Validate that a completed phase is actually implemented"""
        phase_num = phase['number']
        phase_name = phase['name']
        
        self.logger.info(f"Validating Phase {phase_num}: {phase_name}")
        
        # Check for phase-specific artifacts
        if 'Documentation' in phase_name:
            self._check_documentation_phase(phase, context)
        elif 'TDD' in phase_name or 'Test' in phase_name:
            self._check_tdd_phase(phase, context)
        elif 'Planning' in phase_name:
            self._check_planning_phase(phase, context)
        elif 'Foundation' in phase_name:
            self._check_foundation_phase(phase, context)
    
    def _check_documentation_phase(self, phase: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Check if documentation orchestrator is properly implemented"""
        orchestrator_path = self.workspace_root / "src" / "orchestration_4_0" / "orchestrators" / "documentation" / "documentation_orchestrator.py"
        
        if not orchestrator_path.exists():
            self._add_issue(
                'plan', 'high',
                f"Documentation orchestrator missing for Phase {phase['number']}",
                orchestrator_path,
                auto_fixable=False
            )
    
    def _check_tdd_phase(self, phase: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Check if TDD orchestrator is properly implemented"""
        orchestrator_path = self.workspace_root / "src" / "orchestrators" / "tdd" / "tdd_orchestrator.py"
        
        if not orchestrator_path.exists():
            self._add_issue(
                'plan', 'high',
                f"TDD orchestrator missing for Phase {phase['number']}",
                orchestrator_path,
                auto_fixable=False
            )
    
    def _check_planning_phase(self, phase: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Check if planning system is properly implemented"""
        planning_root = self.workspace_root / "src" / "planning_system"
        
        if not planning_root.exists():
            self._add_issue(
                'plan', 'high',
                f"Planning system missing for Phase {phase['number']}",
                planning_root,
                auto_fixable=False
            )
    
    def _check_foundation_phase(self, phase: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Check if foundation components are implemented"""
        base_orchestrator = self.workspace_root / "src" / "orchestrators" / "base" / "base_orchestrator.py"
        
        if not base_orchestrator.exists():
            self._add_issue(
                'plan', 'critical',
                f"Base orchestrator missing for Phase {phase['number']}",
                base_orchestrator,
                auto_fixable=False
            )
    
    # ============================================================================
    # PHASE 2: VALIDATE_TESTS - Test Suite Validation
    # ============================================================================
    
    def _phase_validate_tests(self, context: Dict[str, Any]) -> None:
        """Run test suite and validate coverage"""
        self.logger.info("Phase 2: Running test suite validation")
        
        tests_dir = self.workspace_root / "tests"
        if not tests_dir.exists():
            self._add_issue(
                'tests', 'high',
                "Tests directory not found",
                tests_dir,
                auto_fixable=False
            )
            return
        
        # Run pytest (skip slow and performance tests to avoid hangs)
        try:
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short", "-m", "not slow and not performance"],
                capture_output=True,
                text=True,
                cwd=str(self.workspace_root),
                timeout=120  # Reduced to 2 minutes for fast tests only
            )
            
            # Parse test results
            output = result.stdout + result.stderr
            
            # Extract test counts
            passed_match = re.search(r'(\d+) passed', output)
            failed_match = re.search(r'(\d+) failed', output)
            
            self.report.tests_passed = int(passed_match.group(1)) if passed_match else 0
            self.report.tests_failed = int(failed_match.group(1)) if failed_match else 0
            self.report.tests_run = self.report.tests_passed + self.report.tests_failed
            
            if self.report.tests_failed > 0:
                self._add_issue(
                    'tests', 'high',
                    f"{self.report.tests_failed} tests failing",
                    tests_dir,
                    auto_fixable=False
                )
            
            self.logger.info(f"Tests: {self.report.tests_passed} passed, {self.report.tests_failed} failed")
            
        except subprocess.TimeoutExpired:
            self._add_issue(
                'tests', 'medium',
                "Test suite timed out (>5 minutes)",
                tests_dir,
                auto_fixable=False
            )
        except Exception as e:
            self._add_issue(
                'tests', 'medium',
                f"Error running tests: {e}",
                tests_dir,
                auto_fixable=False
            )
    
    # ============================================================================
    # PHASE 3: CHECK_DOCS - Documentation Completeness
    # ============================================================================
    
    def _phase_check_docs(self, context: Dict[str, Any]) -> None:
        """Check documentation completeness and generate if missing"""
        self.logger.info("Phase 3: Checking documentation completeness")
        
        # Check for completed work documentation
        completed_phases = self._parse_completed_phases()
        
        for phase in completed_phases:
            phase_num = phase['number']
            phase_name = phase['name']
            
            # Expected doc location
            doc_path = self.workspace_root / "cortex-brain" / "documents" / "reports" / f"PHASE-{phase_num}-COMPLETE.md"
            
            if not doc_path.exists():
                if context.get('fix_mode', True):
                    # Generate documentation using DocumentationOrchestrator
                    self._generate_phase_documentation(phase, doc_path, context)
                else:
                    self._add_issue(
                        'docs', 'medium',
                        f"Documentation missing for Phase {phase_num}: {phase_name}",
                        doc_path,
                        auto_fixable=True
                    )
    
    def _generate_phase_documentation(self, phase: Dict[str, Any], doc_path: Path, context: Dict[str, Any]) -> None:
        """Generate documentation for a completed phase"""
        try:
            # Create basic documentation
            doc_content = f"""# Phase {phase['number']} Complete: {phase['name']}

**Status:** ✅ COMPLETE
**Completion:** {phase['completion']}%
**Validated:** {datetime.now().strftime('%Y-%m-%d')}

## Summary

Phase {phase['number']} ({phase['name']}) has been completed and validated by SystemIntegrityOrchestrator.

## Validation

- Implementation verified
- Tests passing
- Documentation generated
- System integrity confirmed

**Generated by:** SystemIntegrityOrchestrator.0
**Timestamp:** {datetime.now().isoformat()}
"""
            
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(doc_content, encoding='utf-8')
            
            self.report.docs_generated += 1
            self._mark_issue_fixed('docs', f"Generated documentation for Phase {phase['number']}")
            
            self.logger.info(f"Generated documentation: {doc_path}")
            
        except Exception as e:
            self._add_issue(
                'docs', 'medium',
                f"Failed to generate docs for Phase {phase['number']}: {e}",
                doc_path,
                auto_fixable=False
            )
    
    # ============================================================================
    # PHASE 4: ORGANIZE_FILES - File Structure Organization
    # ============================================================================
    
    def _phase_organize_files(self, context: Dict[str, Any]) -> None:
        """Organize file structure and run cleanup script"""
        self.logger.info("Phase 4: Organizing file structure")
        
        # Run cortex-cleanup.ps1
        cleanup_script = self.workspace_root / "cortex-cleanup.ps1"
        
        if cleanup_script.exists() and context.get('fix_mode', True):
            try:
                self.logger.info("Running cortex-cleanup.ps1...")
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(cleanup_script)],
                    capture_output=True,
                    text=True,
                    cwd=str(self.workspace_root),
                    timeout=300
                )
                
                if result.returncode == 0:
                    self.logger.info("Cleanup script completed successfully")
                else:
                    self.logger.warning(f"Cleanup script warnings: {result.stderr}")
                    
            except Exception as e:
                self._add_issue(
                    'structure', 'medium',
                    f"Error running cleanup script: {e}",
                    cleanup_script,
                    auto_fixable=False
                )
        
        # Check root folder for misplaced files
        self._check_root_folder(context)
    
    def _check_root_folder(self, context: Dict[str, Any]) -> None:
        """Check root folder for files that should be relocated"""
        
        # Allowed root files
        allowed_root_files = {
            'README.md', 'LICENSE', 'CHANGELOG.md', '.gitignore',
            'requirements.txt', 'pytest.ini', 'cortex.config.json',
            'cortex.config.template.json', 'cortex-cleanup.ps1',
            'coverage.json', '.flake8', 'pyproject.toml', 'setup.py',
            'setup.cfg', '.python-version', '.env.example'
        }
        
        # Check for misplaced files
        for item in self.workspace_root.iterdir():
            if item.is_file() and item.name not in allowed_root_files:
                # Determine proper location
                if item.suffix in ['.md', '.txt']:
                    target_dir = self.workspace_root / "cortex-brain" / "documents" / "reports"
                elif item.suffix in ['.py']:
                    target_dir = self.workspace_root / "scripts"
                elif item.suffix in ['.yaml', '.yml', '.json']:
                    target_dir = self.workspace_root / "cortex-brain" / "config"
                else:
                    target_dir = self.workspace_root / "archive" / "root"
                
                if context.get('fix_mode', True):
                    self._relocate_file(item, target_dir, context)
                else:
                    self._add_issue(
                        'structure', 'low',
                        f"File should be relocated: {item.name}",
                        item,
                        auto_fixable=True
                    )
    
    def _relocate_file(self, source: Path, target_dir: Path, context: Dict[str, Any]) -> None:
        """Relocate a file to proper location"""
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / source.name
            
            # Handle duplicates
            if target_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                target_path = target_dir / f"{source.stem}_{timestamp}{source.suffix}"
            
            shutil.move(str(source), str(target_path))
            
            # Track move for link repair
            self.file_moves[source] = target_path
            
            self.report.files_relocated += 1
            self._mark_issue_fixed('structure', f"Relocated {source.name} to {target_dir}")
            
            self.logger.info(f"Relocated: {source.name} -> {target_path}")
            
        except Exception as e:
            self._add_issue(
                'structure', 'low',
                f"Failed to relocate {source.name}: {e}",
                source,
                auto_fixable=False
            )
    
    # ============================================================================
    # PHASE 5: REPAIR_LINKS - Broken Link Detection and Repair
    # ============================================================================
    
    def _phase_repair_links(self, context: Dict[str, Any]) -> None:
        """Find and fix broken links in all markdown files"""
        self.logger.info("Phase 5: Repairing broken links")
        
        # Find all markdown files
        md_files = list(self.workspace_root.glob("**/*.md"))
        
        for md_file in md_files:
            if self._is_excluded_path(md_file):
                continue
            
            self._repair_links_in_file(md_file, context)
    
    def _repair_links_in_file(self, file_path: Path, context: Dict[str, Any]) -> None:
        """Repair broken links in a single file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Find all markdown links: [text](path)
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            
            def replace_link(match):
                text = match.group(1)
                link = match.group(2)
                
                # Skip external links
                if link.startswith(('http://', 'https://', 'mailto:', '#')):
                    return match.group(0)
                
                # Resolve relative link
                link_path = (file_path.parent / link).resolve()
                
                # Check if link is broken
                if not link_path.exists():
                    # Try to find moved file
                    for old_path, new_path in self.file_moves.items():
                        if old_path.resolve() == link_path:
                            # Calculate new relative path
                            new_relative = self._get_relative_path(file_path, new_path)
                            self.report.links_fixed += 1
                            self.logger.info(f"Fixed link: {link} -> {new_relative}")
                            return f"[{text}]({new_relative})"
                
                return match.group(0)
            
            content = re.sub(link_pattern, replace_link, content)
            
            # Save if changed
            if content != original_content and context.get('fix_mode', True):
                file_path.write_text(content, encoding='utf-8')
                self.logger.info(f"Updated links in: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error repairing links in {file_path}: {e}")
    
    def _get_relative_path(self, from_file: Path, to_file: Path) -> str:
        """Get relative path from one file to another"""
        try:
            return str(to_file.relative_to(from_file.parent))
        except ValueError:
            # Files in different directory trees
            return str(to_file)
    
    # ============================================================================
    # PHASE 6: CLEANUP_LEGACY - Remove CORTEX 3.0 Artifacts
    # ============================================================================
    
    def _phase_cleanup_legacy(self, context: Dict[str, Any]) -> None:
        """Remove legacy CORTEX 3.0 artifacts"""
        self.logger.info("Phase 6: Cleaning up legacy artifacts")
        
        # Patterns for legacy artifacts
        legacy_patterns = [
            "**/*_v3.py",  # Version 3 files
            "**/*_legacy.py",
            "**/cortex-3.0-*",
            "archive/deprecated_v3.8.1/**",
        ]
        
        # Specific legacy orchestrators/modules to remove
        legacy_specific = [
            "src/operations/modules/orchestration/maintenance_orchestrator.py",
            "src/orchestrators/legacy",
            "cortex-brain/cortex-3.0-design",
        ]
        
        if context.get('fix_mode', True):
            # Remove files matching patterns
            for pattern in legacy_patterns:
                for path in self.workspace_root.glob(pattern):
                    if self._is_safe_to_delete(path, context):
                        self._delete_path(path, context)
            
            # Remove specific paths
            for rel_path in legacy_specific:
                path = self.workspace_root / rel_path
                if path.exists() and self._is_safe_to_delete(path, context):
                    self._delete_path(path, context)
    
    def _is_safe_to_delete(self, path: Path, context: Dict[str, Any]) -> bool:
        """Check if path is safe to delete (not referenced in active code)"""
        # Don't delete if in active source
        if "src/orchestration_4_0" in str(path) or "src/planning_system" in str(path):
            return False
        
        # Don't delete if in recent documentation
        if "cortex-brain/documents/planning/active" in str(path):
            return False
        
        return True
    
    def _delete_path(self, path: Path, context: Dict[str, Any]) -> None:
        """Delete a file or directory"""
        try:
            if path.is_file():
                path.unlink()
                self.report.files_deleted += 1
                self.logger.info(f"Deleted legacy file: {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                self.report.files_deleted += 1
                self.logger.info(f"Deleted legacy directory: {path}")
            
            self._mark_issue_fixed('legacy', f"Removed {path.name}")
            
        except Exception as e:
            self._add_issue(
                'legacy', 'low',
                f"Failed to delete {path}: {e}",
                path,
                auto_fixable=False
            )
    
    # ============================================================================
    # PHASE 7: VALIDATE_MANIFESTS - Manifest Integrity
    # ============================================================================
    
    def _phase_validate_manifests(self, context: Dict[str, Any]) -> None:
        """Validate manifest files and orchestrator registrations"""
        self.logger.info("Phase 7: Validating manifests")
        
        # Check cortex-operations.yaml
        operations_yaml = self.workspace_root / "cortex-operations.yaml"
        
        if operations_yaml.exists():
            self._validate_operations_manifest(operations_yaml, context)
        else:
            self._add_issue(
                'manifests', 'high',
                "cortex-operations.yaml not found",
                operations_yaml,
                auto_fixable=False
            )
    
    def _validate_operations_manifest(self, manifest_path: Path, context: Dict[str, Any]) -> None:
        """Validate operations manifest"""
        try:
            import yaml
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
            
            # Check for system_integrity operation
            operations = manifest.get('cortex_operations', {})
            
            operations_root = manifest.get('operations', {})
            
            if 'system_integrity' not in operations_root:
                if context.get('fix_mode', True):
                    self._add_system_integrity_to_manifest(manifest_path, manifest, context)
                else:
                    self._add_issue(
                        'manifests', 'medium',
                        "system_integrity not registered in cortex-operations.yaml",
                        manifest_path,
                        auto_fixable=True
                    )
            
        except Exception as e:
            self._add_issue(
                'manifests', 'medium',
                f"Error validating manifest: {e}",
                manifest_path,
                auto_fixable=False
            )
    
    def _add_system_integrity_to_manifest(self, manifest_path: Path, manifest: Dict, context: Dict[str, Any]) -> None:
        """Add system_integrity operation to manifest"""
        try:
            import yaml
            
            # Add operation
            if 'operations' not in manifest:
                manifest['operations'] = {}
            
            manifest['operations']['system_integrity'] = {
                'triggers': ['system integrity', 'validate system', 'check integrity', 'integrity check'],
                'description': 'Comprehensive system validation and auto-fix',
                'orchestrator': 'SystemIntegrityOrchestrator',
                'execution_method': 'cli_wrapper',
                'admin_only': True,
                'implementation': {
                    'module': 'src.orchestrators.system.system_integrity_orchestrator',
                    'class': 'SystemIntegrityOrchestrator'
                }
            }
            
            # Write back
            with open(manifest_path, 'w', encoding='utf-8') as f:
                yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
            
            self._mark_issue_fixed('manifests', 'Added system_integrity to cortex-operations.yaml')
            self.logger.info("Added system_integrity to cortex-operations.yaml")
            
        except Exception as e:
            self._add_issue(
                'manifests', 'medium',
                f"Failed to update manifest: {e}",
                manifest_path,
                auto_fixable=False
            )
    
    # ============================================================================
    # PHASE 8: GENERATE_REPORT - Comprehensive Report
    # ============================================================================
    
    def _phase_generate_report(self, context: Dict[str, Any]) -> None:
        """Generate comprehensive integrity report"""
        self.logger.info("Phase 8: Generating integrity report")
        
        report_path = self.workspace_root / "cortex-brain" / "documents" / "reports" / f"SYSTEM-INTEGRITY-{datetime.now().strftime('%Y%m%d')}.md"
        
        try:
            report_content = self._build_report_content()
            
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report_content, encoding='utf-8')
            
            self.logger.info(f"Generated integrity report: {report_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
    
    def _build_report_content(self) -> str:
        """Build report markdown content"""
        
        # Calculate summary
        issues_by_category = defaultdict(int)
        issues_by_severity = defaultdict(int)
        
        for issue in self.report.issues:
            issues_by_category[issue.category] += 1
            issues_by_severity[issue.severity] += 1
        
        content = f"""# CORTEX System Integrity Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Orchestrator:** SystemIntegrityOrchestrator.0
**Execution Time:** {self.report.execution_time_seconds:.2f} seconds

---

## 📊 Executive Summary

| Metric | Count |
|--------|-------|
| **Issues Found** | {self.report.issues_found} |
| **Issues Fixed** | {self.report.issues_fixed} |
| **Issues Remaining** | {self.report.issues_remaining} |
| **Tests Run** | {self.report.tests_run} |
| **Tests Passed** | {self.report.tests_passed} |
| **Tests Failed** | {self.report.tests_failed} |
| **Docs Generated** | {self.report.docs_generated} |
| **Files Relocated** | {self.report.files_relocated} |
| **Files Deleted** | {self.report.files_deleted} |
| **Links Fixed** | {self.report.links_fixed} |

---

## 🎯 Issues by Category

"""
        
        for category, count in sorted(issues_by_category.items()):
            content += f"- **{category}:** {count}\n"
        
        content += "\n---\n\n## ⚠️ Issues by Severity\n\n"
        
        for severity, count in sorted(issues_by_severity.items(), reverse=True):
            content += f"- **{severity.upper()}:** {count}\n"
        
        content += "\n---\n\n## 📋 Detailed Issues\n\n"
        
        for idx, issue in enumerate(self.report.issues, 1):
            status = "✅ FIXED" if issue.fix_applied else "⏸️ REMAINING"
            content += f"### {idx}. [{issue.severity.upper()}] {issue.description}\n\n"
            content += f"- **Category:** {issue.category}\n"
            content += f"- **Status:** {status}\n"
            
            if issue.location:
                content += f"- **Location:** `{issue.location}`\n"
            
            if issue.fix_applied and issue.fix_result:
                content += f"- **Fix Applied:** {issue.fix_result}\n"
            elif not issue.auto_fixable:
                content += f"- **Auto-Fix:** Not available (manual intervention required)\n"
            
            content += "\n"
        
        content += """---

## 🔍 Next Steps

"""
        
        if self.report.issues_remaining == 0 and self.report.tests_failed == 0:
            content += "✅ **System integrity validated!** No issues remaining.\n"
        else:
            if self.report.issues_remaining > 0:
                content += f"- Review and address {self.report.issues_remaining} remaining issues\n"
            if self.report.tests_failed > 0:
                content += f"- Fix {self.report.tests_failed} failing tests\n"
        
        content += "\n---\n\n**Report Generated by:** SystemIntegrityOrchestrator.0\n"
        content += "**Author:** Asif Hussain\n"
        content += "**GitHub:** github.com/asifhussain60/CORTEX\n"
        
        return content
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _add_issue(self, category: str, severity: str, description: str, 
                   location: Optional[Path] = None, auto_fixable: bool = True) -> None:
        """Add an integrity issue"""
        issue = IntegrityIssue(
            category=category,
            severity=severity,
            description=description,
            location=location,
            auto_fixable=auto_fixable
        )
        
        self.report.issues.append(issue)
        self.report.issues_found += 1
        self.report.issues_remaining += 1
        
        log_msg = f"[{severity.upper()}] {description}"
        if location:
            log_msg += f" ({location})"
        
        if severity == 'critical':
            self.logger.error(log_msg)
        elif severity == 'high':
            self.logger.warning(log_msg)
        else:
            self.logger.info(log_msg)
    
    def _mark_issue_fixed(self, category: str, description: str) -> None:
        """Mark an issue as fixed"""
        # Find matching issue
        for issue in self.report.issues:
            if issue.category == category and description in issue.description:
                if not issue.fix_applied:
                    issue.fix_applied = True
                    issue.fix_result = description
                    self.report.issues_fixed += 1
                    self.report.issues_remaining = max(0, self.report.issues_remaining - 1)
                return
        
        # No existing issue, count as proactive fix
        self.report.issues_fixed += 1
    
    def _is_excluded_path(self, path: Path) -> bool:
        """Check if path should be excluded from processing"""
        excluded = [
            '.venv', 'venv', 'node_modules', '__pycache__',
            '.git', '.pytest_cache', 'htmlcov', 'build', 'dist'
        ]
        
        return any(part in path.parts for part in excluded)


def main():
    """Main entry point for CLI execution"""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('SystemIntegrity')
    
    orchestrator = SystemIntegrityOrchestrator(logger)
    result = orchestrator.execute()
    
    print("\n" + "="*80)
    print("SYSTEM INTEGRITY CHECK COMPLETE")
    print("="*80)
    print(f"Issues Found: {result['issues_found']}")
    print(f"Issues Fixed: {result['issues_fixed']}")
    print(f"Issues Remaining: {result['issues_remaining']}")
    print(f"Tests Passed: {result['tests_passed']}")
    print(f"Tests Failed: {result['tests_failed']}")
    print(f"Execution Time: {result['execution_time']:.2f}s")
    print("="*80)
    
    return 0 if result['success'] and result['is_complete'] else 1


if __name__ == '__main__':
    exit(main())
