"""
CORTEX 3.1 - EPMO Health Check Tests

Tier 0 Governance Tests for Entry Point Module Orchestrators (EPMOs).
Ensures EPMOs remain optimized and SOLID-compliant through automated checks.

These tests enforce:
- Rule #26: Modular File Structure (no bloat, one class per file)
- Rule #7: Single Responsibility Principle (max 3 responsibilities)
- Rule #9: Dependency Inversion Principle (use abstractions)
- Rule #27: Hemisphere Separation (RIGHT vs LEFT brain)
- Rule #29: YAML-Based Planning (no MD bloat)

Test Strategy:
- FAIL on critical violations (duplication, hard limits)
- WARN on soft violations (soft limits, complexity)
- PASS when all EPMOs healthy

See: cortex-brain/cortex-3.0-design/CORTEX-3.1-EPMO-OPTIMIZATION-PLAN.yaml

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0
Date: November 16, 2025
"""

import pytest
from pathlib import Path
from typing import List, Dict, Set
import re
import ast


# Configuration
SOFT_LINE_LIMIT = 500  # lines (Rule #26)
HARD_LINE_LIMIT = 1000  # lines (Rule #26)
MAX_METHODS = 15  # proxy for max 3 responsibilities (Rule #7)
MAX_DEPENDENCIES = 5  # loose coupling (Rule #9)


class EPMOAnalyzer:
    """Analyzer for EPMO health metrics."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.operations_dir = project_root / "src" / "operations" / "modules"
    
    def find_all_epmos(self) -> List[Path]:
        """Find all EPMO orchestrator files."""
        if not self.operations_dir.exists():
            return []
        
        return list(self.operations_dir.rglob("*_orchestrator.py"))
    
    def get_line_count(self, epmo_file: Path) -> int:
        """Get line count for EPMO file."""
        return len(epmo_file.read_text(encoding='utf-8').splitlines())
    
    def get_class_names(self, epmo_file: Path) -> List[str]:
        """Extract class names from EPMO file."""
        content = epmo_file.read_text(encoding='utf-8')
        matches = re.findall(r'class\s+(\w+Orchestrator)\s*\(', content)
        return matches
    
    def get_method_count(self, epmo_file: Path) -> int:
        """Count methods in EPMO file (proxy for responsibilities)."""
        content = epmo_file.read_text(encoding='utf-8')
        # Count instance methods (indented with 4 spaces, starting with 'def ')
        matches = re.findall(r'\n    def \w+\(', content)
        return len(matches)
    
    def get_import_count(self, epmo_file: Path) -> int:
        """Count direct imports (dependency coupling)."""
        content = epmo_file.read_text(encoding='utf-8')
        # Count 'import' and 'from X import Y' statements
        import_lines = [
            line for line in content.splitlines()
            if line.strip().startswith(('import ', 'from '))
            and not line.strip().startswith('#')
        ]
        return len(import_lines)
    
    def check_duplication(self, epmo_files: List[Path]) -> Dict[str, List[Path]]:
        """Check for duplicate EPMO class names across files."""
        class_to_files = {}
        
        for epmo_file in epmo_files:
            class_names = self.get_class_names(epmo_file)
            for class_name in class_names:
                if class_name not in class_to_files:
                    class_to_files[class_name] = []
                class_to_files[class_name].append(epmo_file)
        
        # Return only duplicates
        return {
            name: files for name, files in class_to_files.items()
            if len(files) > 1
        }
    
    def check_base_inheritance(self, epmo_file: Path) -> bool:
        """Check if EPMO inherits from BaseOperationModule."""
        content = epmo_file.read_text(encoding='utf-8')
        return 'BaseOperationModule' in content
    
    def check_required_methods(self, epmo_file: Path) -> Dict[str, bool]:
        """Check if EPMO has required methods."""
        content = epmo_file.read_text(encoding='utf-8')
        return {
            'get_metadata': 'def get_metadata(' in content,
            'execute': 'def execute(' in content
        }


@pytest.fixture
def project_root() -> Path:
    """Get CORTEX project root."""
    # Navigate up from tests/tier0/ to project root
    return Path(__file__).parent.parent.parent


@pytest.fixture
def epmo_analyzer(project_root: Path) -> EPMOAnalyzer:
    """Create EPMO analyzer."""
    return EPMOAnalyzer(project_root)


@pytest.fixture
def all_epmos(epmo_analyzer: EPMOAnalyzer) -> List[Path]:
    """Get all EPMO files."""
    return epmo_analyzer.find_all_epmos()


class TestEPMODuplication:
    """Test for EPMO duplication (Rule #26)."""
    
    def test_no_epmo_duplication(self, epmo_analyzer: EPMOAnalyzer, all_epmos: List[Path]):
        """
        CRITICAL: Each EPMO class name must be unique across codebase.
        
        Violation Example:
            OptimizeCortexOrchestrator found in:
            - src/operations/modules/optimize/optimize_cortex_orchestrator.py
            - src/operations/modules/optimization/optimize_cortex_orchestrator.py
            - src/operations/modules/system/optimize_system_orchestrator.py (different purpose)
        
        Remediation:
            1. Choose ONE canonical version
            2. Delete duplicate files
            3. Update all imports to use canonical version
            4. Run all tests to verify
        
        See: cortex-brain/documents/analysis/EPMO-OPTIMIZATION-ANALYSIS.md
        """
        duplicates = epmo_analyzer.check_duplication(all_epmos)
        
        if duplicates:
            error_msg = "EPMO duplication detected:\n"
            for class_name, files in duplicates.items():
                file_list = '\n    '.join([str(f.relative_to(epmo_analyzer.project_root)) for f in files])
                error_msg += f"\n  {class_name} found in {len(files)} locations:\n    {file_list}\n"
            
            error_msg += "\nRemediation:\n"
            error_msg += "  1. Choose ONE canonical version\n"
            error_msg += "  2. Delete duplicate files\n"
            error_msg += "  3. Update imports\n"
            error_msg += "  See: cortex-brain/documents/analysis/EPMO-OPTIMIZATION-ANALYSIS.md\n"
            
            pytest.fail(error_msg)


class TestEPMOBloat:
    """Test for EPMO bloat (Rule #26)."""
    
    def test_epmo_line_count_soft_limit(self, epmo_analyzer: EPMOAnalyzer, all_epmos: List[Path]):
        """
        WARNING: EPMOs should stay under 500 line soft limit.
        
        Rationale:
            Files over 500 lines suggest multiple responsibilities (SRP violation).
            Large files harder to maintain, test, and understand.
        
        Remediation:
            - Extract methods to helper classes
            - Split responsibilities into focused orchestrators
            - Move configuration to YAML files
            - Delegate to specialized modules
        
        See: cortex-brain/cortex-3.0-design/CORTEX-3.1-EPMO-OPTIMIZATION-PLAN.yaml
        """
        violations = []
        
        for epmo_file in all_epmos:
            line_count = epmo_analyzer.get_line_count(epmo_file)
            if line_count > SOFT_LINE_LIMIT:
                violations.append({
                    'file': epmo_file.name,
                    'path': str(epmo_file.relative_to(epmo_analyzer.project_root)),
                    'lines': line_count,
                    'limit': SOFT_LINE_LIMIT
                })
        
        if violations:
            error_msg = "EPMOs exceeding soft limit (500 lines):\n"
            for v in violations:
                error_msg += f"  ⚠️ {v['file']}: {v['lines']} lines (limit: {v['limit']})\n"
                error_msg += f"     Path: {v['path']}\n"
            
            error_msg += "\nRemediation:\n"
            error_msg += "  - Extract methods to helper classes\n"
            error_msg += "  - Split into focused orchestrators (SRP)\n"
            error_msg += "  - Move config to YAML\n"
            
            pytest.warn(error_msg)
    
    def test_epmo_line_count_hard_limit(self, epmo_analyzer: EPMOAnalyzer, all_epmos: List[Path]):
        """
        CRITICAL: EPMOs MUST NOT exceed 1000 line hard limit.
        
        This is a blocking violation. Files over 1000 lines are:
        - Unmaintainable (too complex)
        - Violate SRP (clearly multiple responsibilities)
        - Hard to test (too many paths)
        - Bloat context (trigger Copilot summarization)
        
        Remediation:
            MUST refactor before merge. Split into multiple orchestrators.
        
        See: Rule #26 in src/tier0/governance.yaml
        """
        violations = []
        
        for epmo_file in all_epmos:
            line_count = epmo_analyzer.get_line_count(epmo_file)
            if line_count > HARD_LINE_LIMIT:
                violations.append({
                    'file': epmo_file.name,
                    'path': str(epmo_file.relative_to(epmo_analyzer.project_root)),
                    'lines': line_count,
                    'limit': HARD_LINE_LIMIT
                })
        
        if violations:
            error_msg = "CRITICAL: EPMOs exceeding hard limit (1000 lines):\n"
            for v in violations:
                error_msg += f"  🔴 {v['file']}: {v['lines']} lines (HARD LIMIT: {v['limit']})\n"
                error_msg += f"     Path: {v['path']}\n"
            
            error_msg += "\n❌ BLOCKING: Must refactor before merge\n"
            error_msg += "Remediation:\n"
            error_msg += "  1. Split into multiple focused orchestrators\n"
            error_msg += "  2. Each orchestrator: 1-3 responsibilities max\n"
            error_msg += "  3. Update imports and tests\n"
            
            pytest.fail(error_msg)


class TestEPMOSOLIDCompliance:
    """Test for SOLID principle compliance."""
    
    def test_epmo_srp_compliance(self, epmo_analyzer: EPMOAnalyzer, all_epmos: List[Path]):
        """
        FAIL: EPMOs must follow Single Responsibility Principle (Rule #7).
        
        Heuristic: Method count > 15 suggests > 3 responsibilities.
        
        Each EPMO should have 1-3 clear responsibilities:
        - Orchestration (coordinate sub-operations)
        - Validation (pre/post checks)
        - Reporting (generate results)
        
        Violation Example:
            OptimizeCortexOrchestrator with 11 responsibilities:
            - Structure validation
            - Import optimization
            - Class refactoring
            - Test management
            - Documentation
            - Metrics analysis
            - Backup management
            - Deployment
            - User notification
            - Logging
            - Cleanup
        
        Remediation:
            Split into focused orchestrators (e.g., OptimizeStructureOrchestrator,
            OptimizeTestingOrchestrator, OptimizeDeploymentOrchestrator)
        
        See: Rule #7 in src/tier0/governance.yaml
        """
        violations = []
        
        for epmo_file in all_epmos:
            method_count = epmo_analyzer.get_method_count(epmo_file)
            if method_count > MAX_METHODS:
                violations.append({
                    'file': epmo_file.name,
                    'path': str(epmo_file.relative_to(epmo_analyzer.project_root)),
                    'methods': method_count,
                    'limit': MAX_METHODS
                })
        
        if violations:
            error_msg = "SRP violations detected (too many methods):\n"
            for v in violations:
                error_msg += f"  🔴 {v['file']}: {v['methods']} methods (suggests >3 responsibilities)\n"
                error_msg += f"     Path: {v['path']}\n"
            
            error_msg += "\nRemediation:\n"
            error_msg += "  Split into focused orchestrators:\n"
            error_msg += "  - Each with 1-3 clear responsibilities\n"
            error_msg += "  - Delegate to helper classes\n"
            error_msg += "  See: Rule #7 (Single Responsibility Principle)\n"
            
            pytest.fail(error_msg)
    
    def test_epmo_dip_compliance(self, epmo_analyzer: EPMOAnalyzer, all_epmos: List[Path]):
        """
        WARNING: EPMOs should use dependency injection (Rule #9).
        
        High import count suggests direct instantiation of concrete classes
        instead of accepting abstractions via dependency injection.
        
        Target: < 5 direct imports (loose coupling)
        
        Good Pattern:
            class MyOrchestrator(BaseOperationModule):
                def __init__(self, validator: IValidator, optimizer: IOptimizer):
                    self.validator = validator  # Injected!
                    self.optimizer = optimizer
        
        Bad Pattern:
            class MyOrchestrator(BaseOperationModule):
                def __init__(self):
                    self.validator = ConcreteValidator()  # Tight coupling!
                    self.optimizer = ConcreteOptimizer()
        
        See: Rule #9 in src/tier0/governance.yaml
        """
        violations = []
        
        for epmo_file in all_epmos:
            import_count = epmo_analyzer.get_import_count(epmo_file)
            if import_count > MAX_DEPENDENCIES:
                violations.append({
                    'file': epmo_file.name,
                    'path': str(epmo_file.relative_to(epmo_analyzer.project_root)),
                    'imports': import_count,
                    'limit': MAX_DEPENDENCIES
                })
        
        if violations:
            error_msg = "Potential DIP violations (high import count):\n"
            for v in violations:
                error_msg += f"  ⚠️ {v['file']}: {v['imports']} imports (loose coupling target: <{v['limit']})\n"
                error_msg += f"     Path: {v['path']}\n"
            
            error_msg += "\nRemediation:\n"
            error_msg += "  - Use dependency injection (accept abstractions in __init__)\n"
            error_msg += "  - Depend on interfaces, not concrete classes\n"
            error_msg += "  See: Rule #9 (Dependency Inversion Principle)\n"
            
            pytest.warn(error_msg)


class TestEPMOStructure:
    """Test EPMO structural requirements."""
    
    def test_one_class_per_epmo_file(self, epmo_analyzer: EPMOAnalyzer, all_epmos: List[Path]):
        """
        Each EPMO file should contain exactly 1 orchestrator class.
        
        EPMOs follow single-purpose pattern: one orchestrator per file.
        Helper classes should be in separate files.
        """
        violations = []
        
        for epmo_file in all_epmos:
            class_names = epmo_analyzer.get_class_names(epmo_file)
            if len(class_names) > 1:
                violations.append({
                    'file': epmo_file.name,
                    'classes': class_names
                })
        
        if violations:
            error_msg = "Multiple orchestrator classes per file:\n"
            for v in violations:
                error_msg += f"  {v['file']}: {', '.join(v['classes'])}\n"
            
            error_msg += "\nRemediation: Extract to separate files (one class per file)\n"
            pytest.fail(error_msg)
    
    def test_epmo_inherits_base_module(self, epmo_analyzer: EPMOAnalyzer, all_epmos: List[Path]):
        """
        All EPMOs must inherit from BaseOperationModule.
        
        This ensures consistent interface and behavior across all orchestrators.
        """
        violations = []
        
        for epmo_file in all_epmos:
            if not epmo_analyzer.check_base_inheritance(epmo_file):
                violations.append(epmo_file.name)
        
        if violations:
            error_msg = "EPMOs not inheriting BaseOperationModule:\n"
            for file_name in violations:
                error_msg += f"  - {file_name}\n"
            
            error_msg += "\nAll EPMOs must inherit from BaseOperationModule\n"
            pytest.fail(error_msg)
    
    def test_epmo_has_required_methods(self, epmo_analyzer: EPMOAnalyzer, all_epmos: List[Path]):
        """
        All EPMOs must implement required methods:
        - get_metadata() - Returns operation metadata
        - execute(context) - Main execution logic
        """
        violations = []
        
        for epmo_file in all_epmos:
            required = epmo_analyzer.check_required_methods(epmo_file)
            missing = [method for method, present in required.items() if not present]
            
            if missing:
                violations.append({
                    'file': epmo_file.name,
                    'missing': missing
                })
        
        if violations:
            error_msg = "EPMOs missing required methods:\n"
            for v in violations:
                error_msg += f"  {v['file']}: missing {', '.join(v['missing'])}\n"
            
            pytest.fail(error_msg)


class TestEPMOHealthScore:
    """Overall EPMO health score calculation."""
    
    def test_overall_epmo_health(self, epmo_analyzer: EPMOAnalyzer, all_epmos: List[Path]):
        """
        Calculate overall EPMO health score (0-100).
        
        Scoring:
        - Start at 100
        - -20 per hard limit violation (1000 lines)
        - -5 per soft limit violation (500 lines)
        - -15 per duplication
        - -10 per SRP violation (>15 methods)
        - -5 per DIP warning (>5 imports)
        
        Thresholds:
        - >= 85: HEALTHY ✅
        - 70-84: WARNING ⚠️
        - < 70: CRITICAL 🔴
        
        This test always passes but reports the score.
        """
        health_score = 100.0
        issues = []
        
        # Check bloat
        for epmo_file in all_epmos:
            line_count = epmo_analyzer.get_line_count(epmo_file)
            if line_count > HARD_LINE_LIMIT:
                health_score -= 20
                issues.append(f"HARD LIMIT: {epmo_file.name} ({line_count} lines)")
            elif line_count > SOFT_LINE_LIMIT:
                health_score -= 5
                issues.append(f"SOFT LIMIT: {epmo_file.name} ({line_count} lines)")
        
        # Check duplication
        duplicates = epmo_analyzer.check_duplication(all_epmos)
        for class_name, files in duplicates.items():
            health_score -= 15
            issues.append(f"DUPLICATE: {class_name} in {len(files)} locations")
        
        # Check SRP
        for epmo_file in all_epmos:
            method_count = epmo_analyzer.get_method_count(epmo_file)
            if method_count > MAX_METHODS:
                health_score -= 10
                issues.append(f"SRP: {epmo_file.name} ({method_count} methods)")
        
        # Check DIP
        for epmo_file in all_epmos:
            import_count = epmo_analyzer.get_import_count(epmo_file)
            if import_count > MAX_DEPENDENCIES:
                health_score -= 5
                issues.append(f"DIP: {epmo_file.name} ({import_count} imports)")
        
        health_score = max(0.0, health_score)
        
        # Determine status
        if health_score >= 85:
            status = "HEALTHY ✅"
        elif health_score >= 70:
            status = "WARNING ⚠️"
        else:
            status = "CRITICAL 🔴"
        
        # Report
        report = f"\n{'='*70}\n"
        report += f"EPMO Health Score: {health_score:.1f}/100 ({status})\n"
        report += f"{'='*70}\n"
        report += f"Total EPMOs: {len(all_epmos)}\n"
        report += f"Issues: {len(issues)}\n"
        
        if issues:
            report += "\nDetailed Issues:\n"
            for issue in issues:
                report += f"  - {issue}\n"
        
        report += f"\n{'='*70}\n"
        
        print(report)
        
        # Add to pytest output
        if health_score < 85:
            pytest.warn(f"EPMO health below target: {health_score:.1f}/100")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
