"""
File Organization Validator - CORTEX Boundary Detection & Test Location Validation

Validates that:
1. CORTEX files stay in CORTEX/ folder (no leakage to application repo)
2. Application tests stay in app repo (git-committable)
3. CORTEX tests stay in CORTEX/tests/ (isolated)
4. .gitignore rules properly configured

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: IMPLEMENTATION
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OrganizationViolation:
    """Represents a file organization violation."""
    violation_type: str  # 'cortex_leak', 'test_misplacement', 'gitignore_missing'
    file_path: Path
    expected_location: Path
    severity: str  # 'critical', 'warning', 'info'
    remediation: str


class FileOrganizationValidator:
    """
    Validates file organization following CORTEX isolation rules.
    
    Rules:
    - CORTEX files must be in CORTEX/ or .github/prompts/
    - Application tests must be in app repo tests/
    - CORTEX tests must be in CORTEX/tests/
    - .gitignore must exclude CORTEX/ in application repos
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.cortex_root = self._find_cortex_root()
        self.violations: List[OrganizationViolation] = []
        
    def _find_cortex_root(self) -> Path:
        """Find CORTEX root directory."""
        # Check if we're in standalone CORTEX repo
        if (self.workspace_root / "cortex-brain").exists():
            return self.workspace_root
            
        # Check if CORTEX is embedded in application
        cortex_path = self.workspace_root / "CORTEX"
        if cortex_path.exists():
            return cortex_path
            
        # Fallback: assume embedded structure
        return self.workspace_root / "CORTEX"
    
    def validate(self) -> Dict[str, Any]:
        """
        Run all file organization validations.
        
        Returns:
            Dict with validation results and violations
        """
        self.violations = []
        
        # Run validations
        self._check_cortex_boundary()
        self._check_test_locations()
        self._check_gitignore_rules()
        
        # Calculate scores
        total_checks = 3
        passed_checks = total_checks - len([v for v in self.violations if v.severity == 'critical'])
        score = (passed_checks / total_checks) * 100
        
        return {
            'score': score,
            'status': 'pass' if score >= 80 else 'fail',
            'violations': self.violations,
            'critical_count': len([v for v in self.violations if v.severity == 'critical']),
            'warning_count': len([v for v in self.violations if v.severity == 'warning']),
            'checks_passed': passed_checks,
            'total_checks': total_checks
        }
    
    def _check_cortex_boundary(self):
        """Check for CORTEX files leaked into application repo."""
        if not self.cortex_root.exists():
            return
            
        # CORTEX file patterns that should NOT be in app repo
        cortex_patterns = [
            'cortex-brain/**/*.py',
            'src/agents/**/*.py',
            'src/orchestrators/**/*.py',
            'src/operations/modules/**/*.py',
            '.github/prompts/modules/**/*.md'
        ]
        
        # Scan application repo for CORTEX files
        app_root = self.workspace_root
        if app_root == self.cortex_root:
            # Standalone CORTEX repo, no boundary check needed
            return
            
        for pattern in cortex_patterns:
            for file_path in app_root.glob(pattern):
                # Skip if file is within CORTEX/ or .github/prompts/
                if self._is_within_cortex_boundary(file_path):
                    continue
                    
                # Found leaked CORTEX file
                expected_path = self.cortex_root / file_path.relative_to(app_root)
                self.violations.append(OrganizationViolation(
                    violation_type='cortex_leak',
                    file_path=file_path,
                    expected_location=expected_path,
                    severity='critical',
                    remediation=f"Move to {expected_path}"
                ))
    
    def _check_test_locations(self):
        """Validate test file locations (app tests in repo, CORTEX tests in CORTEX/)."""
        if not self.cortex_root.exists():
            return
            
        # Check CORTEX tests are in CORTEX/tests/
        cortex_test_dir = self.cortex_root / "tests"
        if not cortex_test_dir.exists():
            self.violations.append(OrganizationViolation(
                violation_type='test_misplacement',
                file_path=self.cortex_root,
                expected_location=cortex_test_dir,
                severity='warning',
                remediation=f"Create {cortex_test_dir} for CORTEX unit tests"
            ))
        
        # Check for CORTEX tests in application test directory
        app_test_dir = self.workspace_root / "tests"
        if app_test_dir.exists() and app_test_dir != cortex_test_dir:
            cortex_test_patterns = [
                '**/test_*_orchestrator.py',
                '**/test_*_agent.py',
                '**/test_brain_*.py',
                '**/test_system_alignment*.py'
            ]
            
            for pattern in cortex_test_patterns:
                for test_file in app_test_dir.glob(pattern):
                    if self._is_cortex_test(test_file):
                        expected_path = cortex_test_dir / test_file.relative_to(app_test_dir)
                        self.violations.append(OrganizationViolation(
                            violation_type='test_misplacement',
                            file_path=test_file,
                            expected_location=expected_path,
                            severity='warning',
                            remediation=f"Move CORTEX test to {expected_path}"
                        ))
    
    def _check_gitignore_rules(self):
        """Validate .gitignore excludes CORTEX/ in application repos."""
        if self.workspace_root == self.cortex_root:
            # Standalone CORTEX repo, no .gitignore check needed
            return
            
        gitignore_path = self.workspace_root / ".gitignore"
        if not gitignore_path.exists():
            self.violations.append(OrganizationViolation(
                violation_type='gitignore_missing',
                file_path=self.workspace_root,
                expected_location=gitignore_path,
                severity='critical',
                remediation="Create .gitignore with CORTEX/ exclusion rule"
            ))
            return
            
        # Check if CORTEX/ is excluded
        gitignore_content = gitignore_path.read_text()
        if 'CORTEX/' not in gitignore_content and 'CORTEX' not in gitignore_content:
            self.violations.append(OrganizationViolation(
                violation_type='gitignore_missing',
                file_path=gitignore_path,
                expected_location=gitignore_path,
                severity='critical',
                remediation="Add 'CORTEX/' to .gitignore exclusion rules"
            ))
    
    def _is_within_cortex_boundary(self, file_path: Path) -> bool:
        """Check if file is within CORTEX boundary."""
        try:
            # Check if file is in CORTEX/ or .github/prompts/
            rel_path = file_path.relative_to(self.workspace_root)
            parts = rel_path.parts
            return parts[0] in ('CORTEX', '.github')
        except ValueError:
            return False
    
    def _is_cortex_test(self, test_file: Path) -> bool:
        """Check if test file is a CORTEX test (not application test)."""
        content = test_file.read_text()
        
        # CORTEX test indicators
        cortex_indicators = [
            'from src.agents',
            'from src.orchestrators',
            'from src.operations.modules',
            'cortex-brain',
            'SystemAlignmentOrchestrator',
            'BrainIngestionAgent',
            'TDDWorkflowOrchestrator'
        ]
        
        return any(indicator in content for indicator in cortex_indicators)
    
    def generate_remediation_templates(self) -> List[Dict[str, Any]]:
        """
        Generate auto-remediation templates for organization violations.
        
        Returns:
            List of remediation templates with file moves and .gitignore updates
        """
        templates = []
        
        for violation in self.violations:
            if violation.violation_type == 'cortex_leak':
                templates.append({
                    'type': 'file_move',
                    'source': str(violation.file_path),
                    'destination': str(violation.expected_location),
                    'command': f"git mv {violation.file_path} {violation.expected_location}",
                    'description': f"Move leaked CORTEX file to proper location"
                })
            
            elif violation.violation_type == 'test_misplacement':
                templates.append({
                    'type': 'file_move',
                    'source': str(violation.file_path),
                    'destination': str(violation.expected_location),
                    'command': f"git mv {violation.file_path} {violation.expected_location}",
                    'description': f"Move CORTEX test to isolated location"
                })
            
            elif violation.violation_type == 'gitignore_missing':
                templates.append({
                    'type': 'gitignore_update',
                    'file_path': str(violation.expected_location),
                    'content': '\n# CORTEX AI Assistant (local only, not committed)\nCORTEX/\n',
                    'description': 'Add CORTEX exclusion rule to .gitignore'
                })
        
        return templates
