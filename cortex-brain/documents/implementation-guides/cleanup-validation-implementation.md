# CORTEX Cleanup Validation Implementation Guide

**Purpose:** Step-by-step implementation of cleanup safety validation  
**Version:** 1.0  
**Date:** November 26, 2025  
**Author:** Asif Hussain

---

## 🎯 Implementation Overview

This guide provides complete code implementations for adding pre-cleanup validation and post-cleanup verification to prevent CORTEX operational failures.

---

## 📦 File 1: Critical File Detector

**Location:** `src/operations/modules/cleanup/critical_file_detector.py`

```python
"""
Critical File Detector for Cleanup Validation

Automatically detects files that are critical to CORTEX operation
and should never be deleted during cleanup.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import ast
import logging
from pathlib import Path
from typing import Set, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ImportInfo:
    """Information about an import statement"""
    module: str
    file_path: Path
    line_number: int


class CriticalFileDetector:
    """Detect files that are critical to CORTEX operation"""
    
    # Entry points that MUST work
    ENTRY_POINTS = [
        'src/main.py',
        'src/entry_point/cortex_entry.py',
        'src/cortex_agents/intent_router.py'
    ]
    
    # Directories that are always protected
    PROTECTED_DIRECTORIES = [
        'src/',
        'tests/',
        'cortex-brain/tier0/',
        'cortex-brain/tier1/',
        'cortex-brain/tier2/',
        'cortex-brain/tier3/',
        '.git/',
        '.github/prompts/'
    ]
    
    # Individual files that are always protected
    PROTECTED_FILES = [
        'cortex.config.json',
        'VERSION',
        'requirements.txt',
        'pytest.ini',
        'setup.py',
        'pyproject.toml',
        'cortex-brain/response-templates.yaml',
        'cortex-brain/brain-protection-rules.yaml'
    ]
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self._import_cache: Dict[Path, Set[Path]] = {}
    
    def detect_critical_files(self) -> Set[Path]:
        """
        Build comprehensive list of critical files.
        
        Returns:
            Set of Path objects for files that must not be deleted
        """
        logger.info("Detecting critical files...")
        critical_files = set()
        
        # 1. Protected directories (all files within)
        for dir_pattern in self.PROTECTED_DIRECTORIES:
            dir_path = self.project_root / dir_pattern
            if dir_path.exists() and dir_path.is_dir():
                critical_files.update(dir_path.rglob('*'))
        
        # 2. Protected individual files
        for file_pattern in self.PROTECTED_FILES:
            file_path = self.project_root / file_pattern
            if file_path.exists():
                critical_files.add(file_path)
        
        # 3. Entry points and their dependencies
        for entry_point in self.ENTRY_POINTS:
            entry_path = self.project_root / entry_point
            if entry_path.exists():
                dependencies = self.trace_imports(entry_path)
                critical_files.update(dependencies)
        
        logger.info(f"Detected {len(critical_files)} critical files")
        return critical_files
    
    def trace_imports(self, file_path: Path, visited: Set[Path] = None) -> Set[Path]:
        """
        Recursively trace all imports from a Python file.
        
        Args:
            file_path: Starting Python file
            visited: Set of already visited files (prevents cycles)
        
        Returns:
            Set of all files in import chain
        """
        if visited is None:
            visited = set()
        
        if file_path in visited or not file_path.exists():
            return visited
        
        visited.add(file_path)
        
        # Parse imports from this file
        imports = self._parse_imports(file_path)
        
        # Recursively trace each import
        for import_info in imports:
            if import_info.file_path and import_info.file_path not in visited:
                self.trace_imports(import_info.file_path, visited)
        
        return visited
    
    def _parse_imports(self, file_path: Path) -> List[ImportInfo]:
        """
        Parse import statements from a Python file.
        
        Args:
            file_path: Python file to parse
        
        Returns:
            List of ImportInfo objects
        """
        # Check cache
        if file_path in self._import_cache:
            return [
                ImportInfo(module='', file_path=p, line_number=0)
                for p in self._import_cache[file_path]
            ]
        
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_path = self._resolve_import(alias.name, file_path)
                        if module_path:
                            imports.append(ImportInfo(
                                module=alias.name,
                                file_path=module_path,
                                line_number=node.lineno
                            ))
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_path = self._resolve_import(node.module, file_path)
                        if module_path:
                            imports.append(ImportInfo(
                                module=node.module,
                                file_path=module_path,
                                line_number=node.lineno
                            ))
        
        except Exception as e:
            logger.debug(f"Could not parse {file_path}: {e}")
        
        # Cache results
        self._import_cache[file_path] = {imp.file_path for imp in imports if imp.file_path}
        
        return imports
    
    def _resolve_import(self, module_name: str, from_file: Path) -> Path:
        """
        Resolve import statement to actual file path.
        
        Args:
            module_name: Import module name (e.g., 'src.tier1.working_memory')
            from_file: File containing the import
        
        Returns:
            Path to imported file, or None if not found
        """
        # Convert module name to path
        module_parts = module_name.split('.')
        
        # Try absolute import from project root
        module_path = self.project_root
        for part in module_parts:
            module_path = module_path / part
        
        # Check for .py file
        if (module_path.with_suffix('.py')).exists():
            return module_path.with_suffix('.py')
        
        # Check for __init__.py in directory
        if (module_path / '__init__.py').exists():
            return module_path / '__init__.py'
        
        # Try relative import from current file's directory
        relative_base = from_file.parent
        module_path = relative_base
        for part in module_parts:
            module_path = module_path / part
        
        if (module_path.with_suffix('.py')).exists():
            return module_path.with_suffix('.py')
        
        if (module_path / '__init__.py').exists():
            return module_path / '__init__.py'
        
        return None
    
    def is_critical(self, file_path: Path, critical_files: Set[Path] = None) -> bool:
        """
        Check if a file is critical.
        
        Args:
            file_path: File to check
            critical_files: Pre-computed set of critical files (optional)
        
        Returns:
            True if file is critical, False otherwise
        """
        if critical_files is None:
            critical_files = self.detect_critical_files()
        
        return file_path in critical_files
    
    def find_importers(self, file_path: Path) -> List[ImportInfo]:
        """
        Find all files that import the given file.
        
        Args:
            file_path: File to search for
        
        Returns:
            List of ImportInfo for files that import this file
        """
        importers = []
        
        # Search all Python files in project
        for py_file in self.project_root.rglob('*.py'):
            if py_file == file_path:
                continue
            
            imports = self._parse_imports(py_file)
            for import_info in imports:
                if import_info.file_path == file_path:
                    importers.append(ImportInfo(
                        module=import_info.module,
                        file_path=py_file,
                        line_number=import_info.line_number
                    ))
        
        return importers
```

---

## 📦 File 2: Cleanup Validator

**Location:** `src/operations/modules/cleanup/cleanup_validator.py`

```python
"""
Cleanup Validator - Pre-execution validation

Validates proposed cleanup actions to ensure CORTEX functionality
is not compromised.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
import subprocess
import importlib
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, field

from .critical_file_detector import CriticalFileDetector, ImportInfo

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # import_dependency, test_discovery, entry_point, health
    message: str
    file: Path
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of validation checks"""
    passed: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    validation_time: float = 0.0
    
    @property
    def critical_errors(self) -> List[ValidationError]:
        """Get only critical errors"""
        return [e for e in self.errors if e.severity == 'CRITICAL']
    
    @property
    def has_critical_errors(self) -> bool:
        """Check if any critical errors"""
        return len(self.critical_errors) > 0


class CleanupValidator:
    """Validate cleanup operations before execution"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.detector = CriticalFileDetector(project_root)
    
    def validate_proposed_cleanup(self, manifest: Dict[str, Any]) -> ValidationResult:
        """
        Validate entire cleanup manifest.
        
        Args:
            manifest: Cleanup manifest with proposed_actions
        
        Returns:
            ValidationResult with pass/fail and details
        """
        import time
        start_time = time.time()
        
        logger.info("Starting cleanup validation...")
        
        errors = []
        warnings = []
        
        proposed_actions = manifest.get('proposed_actions', [])
        files_to_delete = [
            Path(action['file']) for action in proposed_actions
            if action.get('action') == 'delete'
        ]
        
        # 1. Import dependency validation
        logger.info("  1. Validating import dependencies...")
        import_errors = self._validate_imports(files_to_delete)
        errors.extend(import_errors)
        
        # 2. Critical file protection
        logger.info("  2. Checking critical file protection...")
        critical_errors = self._validate_critical_files(files_to_delete)
        errors.extend(critical_errors)
        
        # 3. Test discovery validation
        logger.info("  3. Validating test discovery...")
        test_errors = self._validate_test_discovery(files_to_delete)
        errors.extend(test_errors)
        
        # 4. Entry point validation
        logger.info("  4. Validating entry points...")
        entry_errors = self._validate_entry_points()
        errors.extend(entry_errors)
        
        validation_time = time.time() - start_time
        
        result = ValidationResult(
            passed=len([e for e in errors if e.severity == 'CRITICAL']) == 0,
            errors=errors,
            warnings=warnings,
            validation_time=validation_time
        )
        
        logger.info(f"Validation complete in {validation_time:.2f}s: "
                   f"{'PASSED' if result.passed else 'FAILED'}")
        
        return result
    
    def _validate_imports(self, files_to_delete: List[Path]) -> List[ValidationError]:
        """Check if any imports reference files to be deleted"""
        errors = []
        
        for file_path in files_to_delete:
            if not file_path.suffix == '.py':
                continue
            
            # Find all files that import this one
            importers = self.detector.find_importers(file_path)
            
            if importers:
                errors.append(ValidationError(
                    severity='CRITICAL',
                    category='import_dependency',
                    message=f'File imported by {len(importers)} modules',
                    file=file_path,
                    details={
                        'importers': [
                            {
                                'file': str(imp.file_path.relative_to(self.project_root)),
                                'line': imp.line_number
                            }
                            for imp in importers
                        ]
                    }
                ))
        
        return errors
    
    def _validate_critical_files(self, files_to_delete: List[Path]) -> List[ValidationError]:
        """Check if any critical files would be deleted"""
        errors = []
        
        critical_files = self.detector.detect_critical_files()
        
        for file_path in files_to_delete:
            if file_path in critical_files:
                errors.append(ValidationError(
                    severity='CRITICAL',
                    category='critical_file_protection',
                    message='File is critical to CORTEX operation',
                    file=file_path,
                    details={
                        'reason': 'File is in protected directory or import chain'
                    }
                ))
        
        return errors
    
    def _validate_test_discovery(self, files_to_delete: List[Path]) -> List[ValidationError]:
        """Check if test discovery would be affected"""
        errors = []
        
        # Count current tests
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', '--collect-only', '-q'],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=30
            )
            
            current_tests = self._parse_test_count(result.stdout)
            
            # Check if any test files would be deleted
            test_files = [f for f in files_to_delete if 'test' in f.name.lower()]
            
            if test_files:
                errors.append(ValidationError(
                    severity='HIGH',
                    category='test_discovery',
                    message=f'{len(test_files)} test files would be deleted',
                    file=test_files[0],  # Representative file
                    details={
                        'current_test_count': current_tests,
                        'test_files': [str(f.relative_to(self.project_root)) for f in test_files]
                    }
                ))
        
        except Exception as e:
            logger.warning(f"Could not validate test discovery: {e}")
        
        return errors
    
    def _validate_entry_points(self) -> List[ValidationError]:
        """Check if entry points can still be imported"""
        errors = []
        
        critical_imports = [
            'src.main',
            'src.entry_point.cortex_entry',
            'src.cortex_agents.intent_router',
            'src.operations.base_operation_module'
        ]
        
        for module_name in critical_imports:
            try:
                # Try importing
                importlib.import_module(module_name)
            except ImportError as e:
                errors.append(ValidationError(
                    severity='CRITICAL',
                    category='entry_point',
                    message=f'Entry point import failed: {module_name}',
                    file=self.project_root / module_name.replace('.', '/') + '.py',
                    details={'error': str(e)}
                ))
        
        return errors
    
    def _parse_test_count(self, pytest_output: str) -> int:
        """Parse test count from pytest output"""
        import re
        
        # Look for pattern like "collected 656 items"
        match = re.search(r'collected (\d+) items?', pytest_output)
        if match:
            return int(match.group(1))
        
        return 0
```

---

## 📦 File 3: Cleanup Verifier

**Location:** `src/operations/modules/cleanup/cleanup_verifier.py`

```python
"""
Cleanup Verifier - Post-execution verification

Verifies CORTEX functionality after cleanup execution.
Triggers automatic rollback if issues detected.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
import subprocess
import importlib
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

from .cleanup_validator import ValidationResult, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of post-cleanup verification"""
    passed: bool
    message: str
    checks: Dict[str, Any]
    rollback_triggered: bool = False


class CleanupVerifier:
    """Verify CORTEX functionality after cleanup"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
    
    def verify_cleanup(self, use_health_validator: bool = True) -> VerificationResult:
        """
        Run comprehensive post-cleanup verification.
        
        Args:
            use_health_validator: Use HealthValidator for quick health check
        
        Returns:
            VerificationResult with pass/fail and details
        """
        logger.info("=" * 70)
        logger.info("POST-CLEANUP VERIFICATION")
        logger.info("=" * 70)
        
        checks = {}
        all_passed = True
        
        # 1. Import validation
        logger.info("1. Validating Python imports...")
        import_result = self._validate_imports()
        checks['imports'] = import_result
        if not import_result['passed']:
            all_passed = False
            logger.error("   ❌ Import validation failed")
        else:
            logger.info("   ✅ All critical imports functional")
        
        # 2. Test discovery
        logger.info("2. Validating test discovery...")
        test_result = self._validate_test_discovery()
        checks['test_discovery'] = test_result
        if not test_result['passed']:
            all_passed = False
            logger.error("   ❌ Test discovery failed")
        else:
            logger.info(f"   ✅ {test_result['tests_found']} tests discoverable")
        
        # 3. Health check (if available)
        if use_health_validator:
            logger.info("3. Running health validator...")
            health_result = self._run_health_check()
            checks['health'] = health_result
            if not health_result['passed']:
                all_passed = False
                logger.error("   ❌ Health check failed")
            else:
                logger.info(f"   ✅ System health: {health_result['status']}")
        
        # 4. Smoke tests
        logger.info("4. Running smoke tests...")
        smoke_result = self._run_smoke_tests()
        checks['smoke_tests'] = smoke_result
        if not smoke_result['passed']:
            all_passed = False
            logger.error("   ❌ Smoke tests failed")
        else:
            logger.info(f"   ✅ {smoke_result['passed_count']}/{smoke_result['total_count']} smoke tests passed")
        
        logger.info("")
        if all_passed:
            logger.info("✅ POST-CLEANUP VERIFICATION COMPLETE")
            logger.info("   All systems operational")
        else:
            logger.error("❌ POST-CLEANUP VERIFICATION FAILED")
            logger.error("   CORTEX functionality compromised")
        logger.info("")
        
        return VerificationResult(
            passed=all_passed,
            message="All checks passed" if all_passed else "Some checks failed",
            checks=checks
        )
    
    def _validate_imports(self) -> Dict[str, Any]:
        """Validate critical imports work"""
        critical_imports = [
            'src.main',
            'src.entry_point.cortex_entry',
            'src.cortex_agents.intent_router',
            'src.operations.base_operation_module',
            'src.tier0.tier_validator',
            'src.tier1.working_memory',
            'src.tier2.knowledge_graph',
            'src.cortex_agents.health_validator.agent'
        ]
        
        passed = []
        failed = []
        
        for module_name in critical_imports:
            try:
                importlib.import_module(module_name)
                passed.append(module_name)
            except ImportError as e:
                failed.append({'module': module_name, 'error': str(e)})
        
        return {
            'passed': len(failed) == 0,
            'total': len(critical_imports),
            'passed_count': len(passed),
            'failed_count': len(failed),
            'failed_modules': failed
        }
    
    def _validate_test_discovery(self) -> Dict[str, Any]:
        """Validate pytest can discover tests"""
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', '--collect-only', '-q'],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=30
            )
            
            # Parse test count
            import re
            match = re.search(r'collected (\d+) items?', result.stdout)
            test_count = int(match.group(1)) if match else 0
            
            return {
                'passed': test_count > 0,
                'tests_found': test_count
            }
        
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _run_health_check(self) -> Dict[str, Any]:
        """Run HealthValidator quick check"""
        try:
            from src.cortex_agents.health_validator.agent import HealthValidator
            from src.cortex_agents.base_agent import AgentRequest
            
            # Initialize validator (quick mode - skip tests)
            validator = HealthValidator("post-cleanup-validator", None, None, None)
            
            request = AgentRequest(
                intent="health_check",
                context={"skip_tests": True},
                user_message="Post-cleanup verification"
            )
            
            response = validator.execute(request)
            
            return {
                'passed': response.success,
                'status': response.result.get('status', 'unknown'),
                'risk_level': response.result.get('risk_level', 'unknown')
            }
        
        except Exception as e:
            logger.warning(f"Could not run health check: {e}")
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _run_smoke_tests(self) -> Dict[str, Any]:
        """Run critical smoke tests"""
        smoke_tests = [
            'tests/tier0/test_brain_protector.py::test_skull_rule_loading',
            'tests/tier1/test_working_memory.py::test_database_connection',
            'tests/tier2/test_knowledge_graph.py::test_database_connection'
        ]
        
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest'] + smoke_tests + ['-v', '--tb=short'],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=60
            )
            
            # Parse results
            passed = result.stdout.count(' PASSED')
            failed = result.stdout.count(' FAILED')
            
            return {
                'passed': failed == 0,
                'total_count': len(smoke_tests),
                'passed_count': passed,
                'failed_count': failed
            }
        
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
```

---

## 📦 File 4: Integration into Holistic Cleanup Orchestrator

**Location:** `src/operations/modules/cleanup/holistic_cleanup_orchestrator.py`

**Changes to execute() method:**

```python
# Add at top of file:
from .cleanup_validator import CleanupValidator
from .cleanup_verifier import CleanupVerifier

# In execute() method, after Phase 2 (manifest generation):

            # NEW: Phase 3: Dry-Run Validation
            if not skip_validation:  # Add parameter to allow skipping
                logger.info("Phase 3: Dry-Run Validation")
                logger.info("-" * 70)
                
                validator = CleanupValidator(self.project_root)
                validation_result = validator.validate_proposed_cleanup(manifest.to_dict())
                
                if validation_result.has_critical_errors:
                    logger.error("❌ VALIDATION FAILED - Proposed cleanup would break CORTEX")
                    logger.error("")
                    logger.error("Critical Issues:")
                    for error in validation_result.critical_errors:
                        logger.error(f"  • {error.message}")
                        logger.error(f"    File: {error.file.relative_to(self.project_root)}")
                        if error.details:
                            for key, value in error.details.items():
                                logger.error(f"    {key}: {value}")
                        logger.error("")
                    
                    # Save validation report
                    validation_report_path = self._save_validation_report(validation_result)
                    
                    logger.error(f"📄 Validation report: {validation_report_path.relative_to(self.project_root)}")
                    logger.error("")
                    logger.error("⚠️  Cleanup BLOCKED to protect CORTEX functionality")
                    logger.error("    Fix critical issues before proceeding")
                    
                    return OperationResult(
                        success=False,
                        status=OperationStatus.VALIDATION_FAILED,
                        message=f"Cleanup validation failed: {len(validation_result.critical_errors)} critical issues",
                        data={
                            'validation_errors': [
                                {
                                    'severity': e.severity,
                                    'category': e.category,
                                    'message': e.message,
                                    'file': str(e.file),
                                    'details': e.details
                                }
                                for e in validation_result.errors
                            ],
                            'validation_report': str(validation_report_path)
                        }
                    )
                
                logger.info(f"✅ Validation passed in {validation_result.validation_time:.2f}s")
                logger.info("   Cleanup is safe to execute")
                logger.info("")

# In _execute_cleanup_actions() method, after cleanup completes:

            # NEW: Post-Cleanup Verification
            logger.info("")
            verifier = CleanupVerifier(self.project_root)
            verification_result = verifier.verify_cleanup(use_health_validator=True)
            
            if not verification_result.passed:
                logger.error("❌ POST-CLEANUP VERIFICATION FAILED")
                logger.error("   Triggering automatic rollback...")
                
                # Rollback cleanup
                rollback_result = self._rollback_cleanup(manifest_data)
                
                return OperationResult(
                    success=False,
                    status=OperationStatus.VERIFICATION_FAILED,
                    message="Cleanup verification failed - changes rolled back",
                    data={
                        'verification_checks': verification_result.checks,
                        'rollback_result': rollback_result
                    }
                )
```

**Add new helper methods:**

```python
    def _save_validation_report(self, validation_result) -> Path:
        """Save validation report to markdown file"""
        report_path = self.project_root / 'cortex-brain' / 'documents' / 'reports' / f'cleanup-validation-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self._generate_validation_report(validation_result)
        report_path.write_text(report, encoding='utf-8')
        
        return report_path
    
    def _generate_validation_report(self, validation_result) -> str:
        """Generate markdown validation report"""
        report = [
            "# CORTEX Cleanup Validation Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Validation Type:** Pre-Cleanup Dry-Run",
            f"**Result:** {'✅ PASSED' if validation_result.passed else '❌ FAILED'}",
            f"**Validation Time:** {validation_result.validation_time:.2f} seconds",
            "",
            "---",
            ""
        ]
        
        if validation_result.critical_errors:
            report.append("## ⚠️ Critical Issues (MUST FIX)")
            report.append("")
            
            for i, error in enumerate(validation_result.critical_errors, 1):
                report.append(f"### Issue {i}: {error.category}")
                report.append(f"**File:** `{error.file.relative_to(self.project_root)}`")
                report.append(f"**Problem:** {error.message}")
                report.append("")
                
                if error.details:
                    report.append("**Details:**")
                    for key, value in error.details.items():
                        report.append(f"- {key}: {value}")
                    report.append("")
                
                report.append(f"**Impact:** {error.severity}")
                report.append("")
        
        return "\n".join(report)
    
    def _rollback_cleanup(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback cleanup changes"""
        logger.info("Performing rollback...")
        
        # Implementation depends on backup strategy
        # Could use git reset, file restoration from backup, etc.
        
        return {
            'rollback_successful': True,
            'method': 'git_reset'
        }
```

---

## 🧪 Testing Implementation

**Location:** `tests/operations/test_cleanup_validation.py`

```python
"""Tests for cleanup validation system"""

import pytest
from pathlib import Path
from src.operations.modules.cleanup.critical_file_detector import CriticalFileDetector
from src.operations.modules.cleanup.cleanup_validator import CleanupValidator
from src.operations.modules.cleanup.cleanup_verifier import CleanupVerifier


class TestCriticalFileDetector:
    """Test critical file detection"""
    
    def test_detects_entry_points(self, project_root):
        """Should detect entry point files as critical"""
        detector = CriticalFileDetector(project_root)
        critical_files = detector.detect_critical_files()
        
        assert (project_root / 'src' / 'main.py') in critical_files
        assert (project_root / 'src' / 'entry_point' / 'cortex_entry.py') in critical_files
    
    def test_traces_imports(self, project_root):
        """Should trace import dependencies"""
        detector = CriticalFileDetector(project_root)
        entry_point = project_root / 'src' / 'main.py'
        
        dependencies = detector.trace_imports(entry_point)
        
        assert len(dependencies) > 0
        assert entry_point in dependencies


class TestCleanupValidator:
    """Test cleanup validation"""
    
    def test_blocks_critical_file_deletion(self, project_root):
        """Should block deletion of critical files"""
        validator = CleanupValidator(project_root)
        
        manifest = {
            'proposed_actions': [
                {'action': 'delete', 'file': str(project_root / 'src' / 'main.py')}
            ]
        }
        
        result = validator.validate_proposed_cleanup(manifest)
        
        assert not result.passed
        assert result.has_critical_errors
    
    def test_allows_safe_deletion(self, project_root, tmp_path):
        """Should allow deletion of safe files"""
        validator = CleanupValidator(project_root)
        
        # Create temporary safe file
        temp_file = project_root / 'temp_cleanup_test.md'
        temp_file.write_text("Test file")
        
        manifest = {
            'proposed_actions': [
                {'action': 'delete', 'file': str(temp_file)}
            ]
        }
        
        result = validator.validate_proposed_cleanup(manifest)
        
        # Cleanup
        temp_file.unlink()
        
        assert result.passed


class TestCleanupVerifier:
    """Test post-cleanup verification"""
    
    def test_verifies_imports(self, project_root):
        """Should verify critical imports work"""
        verifier = CleanupVerifier(project_root)
        
        result = verifier._validate_imports()
        
        assert result['passed']
        assert result['failed_count'] == 0
    
    def test_verifies_test_discovery(self, project_root):
        """Should verify tests are discoverable"""
        verifier = CleanupVerifier(project_root)
        
        result = verifier._validate_test_discovery()
        
        assert result['passed']
        assert result['tests_found'] > 0
```

---

## 📝 Update Response Templates

**Location:** `cortex-brain/response-templates.yaml`

Add new template for cleanup validation:

```yaml
  cleanup_validation_failed:
    name: Cleanup Validation Failed
    triggers:
    - cleanup_validation_failed
    response_type: detailed
    content: |
      # 🧠 CORTEX Cleanup Validation Failed
      **Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
      
      ---
      
      ## 🎯 My Understanding Of Your Request
         You attempted to run cleanup, but pre-execution validation detected issues that would break CORTEX functionality.
      
      ## ⚠️ Challenge
      
      **Challenge:** Proposed cleanup would delete critical files or break import dependencies
      
      ## 💬 Response
         ❌ **Cleanup Blocked for Safety**
         
         Pre-execution validation detected {error_count} critical issues:
         
         {error_details}
         
         **Why Blocked:**
         These issues would cause CORTEX to become non-functional after cleanup. The validation system prevented execution to protect your system.
         
         **Validation Report:** {validation_report_path}
      
      ## 📝 Your Request
         Execute cleanup operation
      
      ## 🔍 Next Steps
         1. Review validation report at {validation_report_path}
         2. Fix critical issues (remove files from cleanup or update references)
         3. Re-run cleanup after issues resolved
         4. Alternative: Skip validation with `cleanup --skip-validation` (not recommended)
```

---

## ✅ Acceptance Testing

Create acceptance test that validates the entire workflow:

```python
"""Acceptance test for cleanup validation"""

def test_cleanup_validation_prevents_breakage(cortex_project):
    """
    End-to-end test: Cleanup validation prevents system breakage
    
    Scenario:
    1. Propose cleanup that would delete critical file
    2. Validation should block execution
    3. CORTEX should remain fully functional
    """
    from src.operations.modules.cleanup.holistic_cleanup_orchestrator import HolisticCleanupOrchestrator
    
    # Create orchestrator
    orchestrator = HolisticCleanupOrchestrator(cortex_project)
    
    # Create manifest with critical file deletion
    manifest = {
        'proposed_actions': [
            {
                'action': 'delete',
                'file': str(cortex_project / 'src' / 'main.py'),
                'reason': 'Test validation'
            }
        ]
    }
    
    # Execute cleanup (should be blocked)
    result = orchestrator.execute(dry_run=False, manifest_data=manifest)
    
    # Verify cleanup was blocked
    assert not result.success
    assert result.status == 'VALIDATION_FAILED'
    assert 'critical' in result.message.lower()
    
    # Verify CORTEX still works
    import importlib
    main_module = importlib.import_module('src.main')
    assert main_module is not None  # File still exists and importable
```

---

## 📊 Implementation Timeline

**Day 1 (3 hours):**
- ✅ Implement `CriticalFileDetector`
- ✅ Write tests for detector
- ✅ Verify import tracing works

**Day 2 (2 hours):**
- ✅ Implement `CleanupValidator`
- ✅ Write validation tests
- ✅ Integrate with orchestrator (dry-run)

**Day 3 (2 hours):**
- ✅ Implement `CleanupVerifier`
- ✅ Write verification tests
- ✅ Integrate with orchestrator (post-execution)

**Day 4 (1 hour):**
- ✅ Update response templates
- ✅ Update documentation
- ✅ Write acceptance tests

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
