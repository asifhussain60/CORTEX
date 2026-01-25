"""
WiringValidationAgent - Tool 2 of 3-Tool Safety System.

Validates component wiring correctness by checking:
1. Class exists (Python file with class definition)
2. Registered (in DatabaseBackedRegistry - SQLite SSOT)
3. Initialized (in MasterOrchestrator.__init__)
4. Called (in MasterOrchestrator.execute_operation)
5. Tested (test file exists)

AC-UNWIRED-VALIDATE-001: WiringValidationAgent implementation
AC-PERMANENT-FIX-009: DatabaseBackedRegistry integration (23/23 wired)

Author: Asif Hussain
Date: 2026-01-25
Updated: 2026-01-XX - Migrated from repo-registry.yaml to DatabaseBackedRegistry
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Status of component wiring."""
    FULLY_WIRED = "FULLY_WIRED"  # All 5 checks pass
    PARTIALLY_WIRED = "PARTIALLY_WIRED"  # Initialized but not called
    UNWIRED = "UNWIRED"  # Exists but not initialized
    ORPHANED = "ORPHANED"  # Called but not registered
    MISSING = "MISSING"  # Doesn't exist


@dataclass
class ValidationResult:
    """Result of component wiring validation.
    
    Attributes:
        component_name: Name of the component being validated
        status: Overall wiring status (FULLY_WIRED, PARTIALLY_WIRED, etc.)
        checks: Dictionary of 5 boolean checks
        issues: List of specific problems found
        recommendations: List of actionable fixes
        file_path: Path to component file (if exists)
    """
    component_name: str
    status: ComponentStatus
    checks: Dict[str, bool] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    file_path: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert ValidationResult to dictionary.
        
        Returns:
            Dictionary representation of validation result
        """
        return {
            'component_name': self.component_name,
            'status': self.status.value,
            'checks': self.checks,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'file_path': self.file_path,
        }


class WiringValidationAgent:
    """Validates component wiring correctness.
    
    This agent performs 5 checks for each component:
    1. class_exists: Python class file exists
    2. registered: Listed in repo-registry.yaml
    3. initialized: Created in MasterOrchestrator.__init__
    4. called: Invoked in MasterOrchestrator.execute_operation
    5. tested: Test file exists
    
    Based on check results, assigns status:
    - FULLY_WIRED: All 5 checks pass
    - PARTIALLY_WIRED: Initialized but not called
    - UNWIRED: Exists but not initialized
    - ORPHANED: Called but not registered
    - MISSING: Class doesn't exist
    
    Usage:
        agent = WiringValidationAgent()
        result = agent.validate_component('InteractionOrchestrator')
        print(result.status)  # ComponentStatus.PARTIALLY_WIRED
        
        report = agent.generate_report()
        print(report['summary'])
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """Initialize WiringValidationAgent.
        
        Args:
            cortex_root: Root directory of CORTEX project.
                        If None, auto-detects from current file location.
        """
        if cortex_root is None:
            # Auto-detect: go up from cortex/tools/ to project root
            self.cortex_root = Path(__file__).parent.parent.parent
        else:
            self.cortex_root = Path(cortex_root)
        
        self.orchestrators_dir = self.cortex_root / 'cortex' / 'orchestrators'
        self.master_orchestrator_file = self.cortex_root / 'cortex' / 'orchestrators' / 'core' / 'master_orchestrator.py'
        self.tests_dir = self.cortex_root / 'tests'
        
        # Cache for performance
        self._db_registry_cache: Optional[Set[str]] = None
        self._master_init_cache: Optional[str] = None
        self._master_execute_cache: Optional[str] = None
    
    def validate_component(self, component_name: str) -> ValidationResult:
        """Validate wiring of a single component.
        
        Args:
            component_name: Name of component to validate (e.g., 'InteractionOrchestrator')
        
        Returns:
            ValidationResult with status, checks, issues, and recommendations
        """
        checks = {
            'class_exists': self._check_class_exists(component_name),
            'registered': self._check_registered(component_name),
            'initialized': self._check_initialized(component_name),
            'called': self._check_called(component_name),
            'tested': self._check_tested(component_name),
        }
        
        # Determine status based on checks
        status = self._determine_status(checks)
        
        # Identify issues
        issues = self._identify_issues(component_name, checks, status)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(component_name, checks, status)
        
        # Find file path
        file_path = self._find_file_path(component_name) if checks['class_exists'] else None
        
        return ValidationResult(
            component_name=component_name,
            status=status,
            checks=checks,
            issues=issues,
            recommendations=recommendations,
            file_path=file_path,
        )
    
    def validate_all(self) -> Dict[str, ValidationResult]:
        """Validate all registered components from DatabaseBackedRegistry.
        
        Returns:
            Dictionary mapping component names to ValidationResults
        """
        results = {}
        
        # Get all registered components from DatabaseBackedRegistry
        registered_names = self._get_registered_from_db()
        for component_name in registered_names:
            if component_name:
                results[component_name] = self.validate_component(component_name)
        
        # Also check mentioned-but-not-implemented components
        mentioned_missing = [
            'EnforcementOrchestrator',
            'GovernanceEnforcementAgent',
            'SecurityCheckpointAgent',
            'ComplianceValidationAgent',
        ]
        
        for component_name in mentioned_missing:
            if component_name not in results:
                results[component_name] = self.validate_component(component_name)
        
        return results
    
    def generate_report(self) -> Dict:
        """Generate comprehensive wiring validation report.
        
        Returns:
            Dictionary with:
            - summary: Counts by status
            - components: Detailed results for each component
            - recommendations: Prioritized action items
        """
        all_results = self.validate_all()
        
        # Count by status
        status_counts = {
            'total_components': len(all_results),
            'fully_wired': 0,
            'partially_wired': 0,
            'unwired': 0,
            'orphaned': 0,
            'missing': 0,
        }
        
        for result in all_results.values():
            if result.status == ComponentStatus.FULLY_WIRED:
                status_counts['fully_wired'] += 1
            elif result.status == ComponentStatus.PARTIALLY_WIRED:
                status_counts['partially_wired'] += 1
            elif result.status == ComponentStatus.UNWIRED:
                status_counts['unwired'] += 1
            elif result.status == ComponentStatus.ORPHANED:
                status_counts['orphaned'] += 1
            elif result.status == ComponentStatus.MISSING:
                status_counts['missing'] += 1
        
        # Convert results to dict format
        components_dict = {
            name: result.to_dict()
            for name, result in all_results.items()
        }
        
        # Generate prioritized recommendations
        recommendations = self._generate_prioritized_recommendations(all_results)
        
        return {
            'summary': status_counts,
            'components': components_dict,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat(),
        }
    
    def _check_class_exists(self, component_name: str) -> bool:
        """Check if component class file exists.
        
        Args:
            component_name: Name of component (e.g., 'InteractionOrchestrator')
        
        Returns:
            True if class file found, False otherwise
        """
        # Search for Python files containing the class definition
        if not self.orchestrators_dir.exists():
            return False
        
        # Convert class name to potential file patterns
        # e.g., InteractionOrchestrator → interaction_orchestrator.py
        file_pattern = re.sub(r'(?<!^)(?=[A-Z])', '_', component_name).lower()
        
        # Search recursively
        for py_file in self.orchestrators_dir.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                # Look for class definition
                if re.search(rf'class\s+{re.escape(component_name)}\s*[(\:]', content):
                    return True
            except Exception:
                continue
        
        # Also check cortex/brain/ for some components
        brain_dir = self.cortex_root / 'cortex' / 'brain'
        if brain_dir.exists():
            for py_file in brain_dir.rglob('*.py'):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    if re.search(rf'class\s+{re.escape(component_name)}\s*[(\:]', content):
                        return True
                except Exception:
                    continue
        
        return False
    
    def _check_registered(self, component_name: str) -> bool:
        """Check if component is registered in DatabaseBackedRegistry.
        
        Args:
            component_name: Name of component
        
        Returns:
            True if registered, False otherwise
        """
        registered_names = self._get_registered_from_db()
        return component_name in registered_names
    
    def _check_initialized(self, component_name: str) -> bool:
        """Check if component is initialized in MasterOrchestrator.__init__.
        
        Args:
            component_name: Name of component
        
        Returns:
            True if initialized, False otherwise
        """
        if self._master_init_cache is None:
            self._master_init_cache = self._read_master_init()
        
        content = self._master_init_cache
        
        # Look for initialization patterns:
        # self.interaction_orchestrator = InteractionOrchestrator(...)
        # self._dor_gate = DoRApprovalGate(...)
        # self.tdd_orchestrator = get_tdd_orchestrator(...)
        
        # Convert to snake_case attribute name
        # Handle acronyms: TDDOrchestrator → tdd_orchestrator (not t_d_d_orchestrator)
        attr_name = component_name
        # First, handle consecutive capitals (TDD → TDD_)
        attr_name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', attr_name)
        # Then normal CamelCase → snake_case
        attr_name = re.sub(r'([a-z])([A-Z])', r'\1_\2', attr_name)
        attr_name = attr_name.lower()
        
        # Search for various initialization patterns
        patterns = [
            rf'self\.{re.escape(attr_name)}\s*=',  # Direct assignment
            rf'self\._.*{re.escape(attr_name)}\s*=',  # Private attribute
            rf'{re.escape(component_name)}\(',  # Direct instantiation
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _check_called(self, component_name: str) -> bool:
        """Check if component is called in MasterOrchestrator.execute_operation.
        
        Args:
            component_name: Name of component
        
        Returns:
            True if called, False otherwise
        """
        if self._master_execute_cache is None:
            self._master_execute_cache = self._read_master_execute()
        
        content = self._master_execute_cache
        
        # Convert to snake_case attribute name
        # Handle acronyms: TDDOrchestrator → tdd_orchestrator (not t_d_d_orchestrator)
        attr_name = component_name
        # First, handle consecutive capitals (TDD → TDD_)
        attr_name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', attr_name)
        # Then normal CamelCase → snake_case
        attr_name = re.sub(r'([a-z])([A-Z])', r'\1_\2', attr_name)
        attr_name = attr_name.lower()
        
        # Search for method calls:
        # self.interaction_orchestrator.execute(...)
        # self.tdd_orchestrator.orchestrate(...)
        # self._dor_gate.request_approval(...)
        
        patterns = [
            rf'self\.{re.escape(attr_name)}\.',  # Method call
            rf'self\._.*{re.escape(attr_name)}\.',  # Private attribute call
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _check_tested(self, component_name: str) -> bool:
        """Check if test file exists for component.
        
        Args:
            component_name: Name of component
        
        Returns:
            True if test file found, False otherwise
        """
        if not self.tests_dir.exists():
            return False
        
        # Convert class name to test file pattern
        # e.g., InteractionOrchestrator → test_interaction_orchestrator.py
        # Handle acronyms: TDDOrchestrator → test_tdd_orchestrator.py
        file_pattern = component_name
        file_pattern = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', file_pattern)
        file_pattern = re.sub(r'([a-z])([A-Z])', r'\1_\2', file_pattern)
        file_pattern = file_pattern.lower()
        test_file_name = f'test_{file_pattern}.py'
        
        # Search recursively for exact test file name
        for test_file in self.tests_dir.rglob(test_file_name):
            return True
        
        # Also check for tests that import and test the component (not just mention it)
        # Look for: from cortex.xxx import ComponentName or class TestComponentName
        for test_file in self.tests_dir.rglob('test_*.py'):
            try:
                content = test_file.read_text(encoding='utf-8')
                # Must have both import/class definition AND usage (not just mention)
                if (f'import {component_name}' in content or 
                    f'class Test{component_name}' in content):
                    return True
            except Exception:
                continue
        
        return False
    
    def _determine_status(self, checks: Dict[str, bool]) -> ComponentStatus:
        """Determine component status based on checks.
        
        Args:
            checks: Dictionary of 5 boolean checks
        
        Returns:
            ComponentStatus enum value
        """
        if not checks['class_exists']:
            return ComponentStatus.MISSING
        
        if checks['called'] and not checks['registered']:
            return ComponentStatus.ORPHANED
        
        if all(checks.values()):
            return ComponentStatus.FULLY_WIRED
        
        if checks['initialized'] and not checks['called']:
            return ComponentStatus.PARTIALLY_WIRED
        
        if checks['class_exists'] and not checks['initialized']:
            return ComponentStatus.UNWIRED
        
        # Default to unwired
        return ComponentStatus.UNWIRED
    
    def _identify_issues(self, component_name: str, checks: Dict[str, bool], status: ComponentStatus) -> List[str]:
        """Identify specific issues with component wiring.
        
        Args:
            component_name: Name of component
            checks: Dictionary of check results
            status: Determined status
        
        Returns:
            List of issue descriptions
        """
        issues = []
        
        if status == ComponentStatus.MISSING:
            issues.append(f"{component_name} class does not exist (mentioned but not implemented)")
        
        if not checks['registered'] and checks['class_exists']:
            issues.append(f"{component_name} not registered in DatabaseBackedRegistry")
        
        if not checks['initialized'] and checks['registered']:
            issues.append(f"{component_name} registered but not initialized in MasterOrchestrator.__init__")
        
        if not checks['called'] and checks['initialized']:
            issues.append(f"{component_name} initialized but not called in MasterOrchestrator.execute_operation")
        
        if not checks['tested'] and checks['class_exists']:
            issues.append(f"{component_name} has no test file")
        
        if checks['called'] and not checks['registered']:
            issues.append(f"{component_name} is called but not registered (orphaned)")
        
        return issues
    
    def _generate_recommendations(self, component_name: str, checks: Dict[str, bool], status: ComponentStatus) -> List[str]:
        """Generate actionable recommendations for component.
        
        Args:
            component_name: Name of component
            checks: Dictionary of check results
            status: Determined status
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if status == ComponentStatus.MISSING:
            recommendations.append(f"Implement {component_name} class")
            recommendations.append(f"Create test file: tests/unit/orchestrators/test_{re.sub(r'(?<!^)(?=[A-Z])', '_', component_name).lower()}.py")
        
        if status == ComponentStatus.PARTIALLY_WIRED:
            recommendations.append(f"Wire {component_name} into MasterOrchestrator.execute_operation()")
            recommendations.append(f"Add invocation in appropriate pipeline stage")
        
        if status == ComponentStatus.UNWIRED:
            if checks['registered']:
                recommendations.append(f"Initialize {component_name} in MasterOrchestrator.__init__()")
                recommendations.append(f"Wire into execute_operation()")
            else:
                recommendations.append(f"Register {component_name} in DatabaseBackedRegistry")
                recommendations.append(f"Initialize in MasterOrchestrator.__init__()")
        
        if status == ComponentStatus.ORPHANED:
            recommendations.append(f"Register {component_name} in DatabaseBackedRegistry")
        
        if not checks['tested'] and checks['class_exists']:
            recommendations.append(f"Create test file for {component_name}")
        
        return recommendations
    
    def _generate_prioritized_recommendations(self, all_results: Dict[str, ValidationResult]) -> List[Dict]:
        """Generate prioritized recommendations across all components.
        
        Args:
            all_results: Dictionary of all validation results
        
        Returns:
            List of prioritized recommendation dictionaries
        """
        recommendations = []
        
        # CRITICAL: Missing components (Stage 3 enforcement)
        missing_components = [
            name for name, result in all_results.items()
            if result.status == ComponentStatus.MISSING
        ]
        if missing_components:
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Implement missing components for Stage 3 enforcement',
                'components': missing_components,
                'count': len(missing_components),
            })
        
        # HIGH: Partially wired (initialized but not called)
        partially_wired = [
            name for name, result in all_results.items()
            if result.status == ComponentStatus.PARTIALLY_WIRED
        ]
        if partially_wired:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Wire initialized components into execute_operation (Stage 1-2 pipeline)',
                'components': partially_wired,
                'count': len(partially_wired),
            })
        
        # MEDIUM: Unwired (exists but not initialized)
        unwired_components = [
            name for name, result in all_results.items()
            if result.status == ComponentStatus.UNWIRED
        ]
        if unwired_components:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Initialize and wire unwired components',
                'components': unwired_components,
                'count': len(unwired_components),
            })
        
        # LOW: Orphaned (called but not registered)
        orphaned_components = [
            name for name, result in all_results.items()
            if result.status == ComponentStatus.ORPHANED
        ]
        if orphaned_components:
            recommendations.append({
                'priority': 'LOW',
                'action': 'Register orphaned components in DatabaseBackedRegistry',
                'components': orphaned_components,
                'count': len(orphaned_components),
            })
        
        return recommendations
    
    def _find_file_path(self, component_name: str) -> Optional[str]:
        """Find file path for component.
        
        Args:
            component_name: Name of component
        
        Returns:
            Relative file path or None
        """
        # Search for Python files containing the class definition
        for py_file in self.orchestrators_dir.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                if re.search(rf'class\s+{re.escape(component_name)}\s*[(\:]', content):
                    return str(py_file.relative_to(self.cortex_root)).replace('\\', '/')
            except Exception:
                continue
        
        # Also check cortex/brain/
        brain_dir = self.cortex_root / 'cortex' / 'brain'
        if brain_dir.exists():
            for py_file in brain_dir.rglob('*.py'):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    if re.search(rf'class\s+{re.escape(component_name)}\s*[(\:]', content):
                        return str(py_file.relative_to(self.cortex_root)).replace('\\', '/')
                except Exception:
                    continue
        
        return None
    
    def _get_registered_from_db(self) -> Set[str]:
        """Get registered component names from DatabaseBackedRegistry.
        
        Returns:
            Set of component names registered in the database
        """
        if self._db_registry_cache is not None:
            return self._db_registry_cache
        
        try:
            from cortex.orchestrators.core.database_registry import (
                get_database_registry,
                initialize_registry
            )
            
            # Initialize registry if needed
            init_result = initialize_registry()
            if init_result.is_err():
                logger.warning(f"Failed to initialize registry: {init_result.error}")
                return set()
            
            # Get wiring statistics from DB
            registry = get_database_registry()
            stats = registry.get_wiring_statistics()
            
            # Extract orchestrator names from categories
            registered_names: Set[str] = set()
            for category, orchestrators in stats.get('by_category', {}).items():
                for name in orchestrators:
                    registered_names.add(name)
            
            self._db_registry_cache = registered_names
            return registered_names
            
        except ImportError as e:
            logger.warning(f"DatabaseBackedRegistry not available: {e}")
            return set()
        except Exception as e:
            logger.error(f"Error reading database registry: {e}")
            return set()
    
    def _read_master_init(self) -> str:
        """Read MasterOrchestrator.__init__ method.
        
        Returns:
            String content of __init__ method
        """
        if not self.master_orchestrator_file.exists():
            return ""
        
        try:
            content = self.master_orchestrator_file.read_text(encoding='utf-8')
            
            # Extract __init__ method - look for the full method including nested code
            # Match from "def __init__" until we hit a method at the same indentation level
            match = re.search(r'    def __init__\(.*?\):(.*?)(?=\n    def [a-z_])', content, re.DOTALL)
            if match:
                return match.group(1)
            
            return ""
        except Exception as e:
            print(f"Error reading master orchestrator: {e}")
            return ""
    
    def _read_master_execute(self) -> str:
        """Read MasterOrchestrator.execute_operation method.
        
        Returns:
            String content of execute_operation method
        """
        if not self.master_orchestrator_file.exists():
            return ""
        
        try:
            content = self.master_orchestrator_file.read_text(encoding='utf-8')
            
            # Extract execute_operation method - look for method at class level (4 spaces)
            match = re.search(r'    def execute_operation\(.*?\):(.*?)(?=\n    def [a-z_])', content, re.DOTALL)
            if match:
                return match.group(1)
            
            return ""
        except Exception as e:
            print(f"Error reading execute_operation: {e}")
            return ""


def main():
    """CLI entry point for WiringValidationAgent."""
    print("🔍 CORTEX Wiring Validation Agent")
    print("=" * 60)
    print()
    
    agent = WiringValidationAgent()
    report = agent.generate_report()
    
    # Print summary
    summary = report['summary']
    print("📊 Summary:")
    print(f"  Total components: {summary['total_components']}")
    print(f"  ✅ Fully wired: {summary['fully_wired']}")
    print(f"  ⚠️  Partially wired: {summary['partially_wired']}")
    print(f"  ❌ Unwired: {summary['unwired']}")
    print(f"  🚨 Orphaned: {summary['orphaned']}")
    print(f"  💀 Missing: {summary['missing']}")
    print()
    
    # Print recommendations
    print("📋 Recommendations:")
    for rec in report['recommendations']:
        priority_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟡',
            'MEDIUM': '🟠',
            'LOW': '🟢',
        }
        emoji = priority_emoji.get(rec['priority'], '⚪')
        print(f"\n{emoji} [{rec['priority']}] {rec['action']}")
        print(f"   Components ({rec['count']}): {', '.join(rec['components'][:5])}")
        if len(rec['components']) > 5:
            print(f"   ... and {len(rec['components']) - 5} more")
    
    print()
    print("=" * 60)
    print(f"Report generated at: {report['timestamp']}")


if __name__ == '__main__':
    main()
