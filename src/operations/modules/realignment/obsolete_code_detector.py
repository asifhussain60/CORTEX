"""
Obsolete Code Detector for CORTEX Align Orchestrator v2.0

This module detects obsolete code across the repository including:
- Orchestrators that have been migrated to utilities
- Tests for deleted orchestrators
- Obsolete scripts (backups, deprecated, temp)
- Files with deprecated import patterns

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ImportAnalysis:
    """Analysis of imports in a file."""
    file: Path
    has_deprecated: bool
    findings: List[Dict[str, str]] = field(default_factory=list)
    total_deprecated_imports: int = 0


@dataclass
class CleanupPlan:
    """Comprehensive plan for cleaning up obsolete code."""
    obsolete_orchestrators: List[Path] = field(default_factory=list)
    obsolete_tests: List[Path] = field(default_factory=list)
    obsolete_scripts: List[Path] = field(default_factory=list)
    files_with_deprecated_imports: List[ImportAnalysis] = field(default_factory=list)
    estimated_removal_size_mb: float = 0.0
    safety_checks_required: bool = True
    total_files: int = 0
    
    def __post_init__(self):
        """Calculate totals after initialization."""
        self.total_files = (
            len(self.obsolete_orchestrators) +
            len(self.obsolete_tests) +
            len(self.obsolete_scripts) +
            len(self.files_with_deprecated_imports)
        )
    
    def get_all_files(self) -> List[Path]:
        """Get list of all files in cleanup plan."""
        files = []
        files.extend(self.obsolete_orchestrators)
        files.extend(self.obsolete_tests)
        files.extend(self.obsolete_scripts)
        # Don't include files with deprecated imports in removal list
        # They need migration, not deletion
        return files


class ObsoleteCodeDetector:
    """Detects obsolete code across the CORTEX repository."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the obsolete code detector.
        
        Args:
            project_root: Path to CORTEX project root. If None, auto-detects.
        """
        self.project_root = project_root or self._detect_project_root()
        self.orchestrators_dir = self.project_root / "src" / "orchestrators"
        self.operations_dir = self.project_root / "src" / "operations"
        self.tests_dir = self.project_root / "tests"
        self.scripts_dir = self.project_root / "scripts"
        
        # Patterns for obsolete scripts
        self.obsolete_script_patterns = [
            "*_OLD.py",
            "*_backup.py",
            "*_deprecated.py",
            "*_temp.py",
            "*.bak",
            "*~",
            "*.backup"
        ]
        
        # Deprecated import patterns
        self.deprecated_imports = [
            r'from\s+src\.orchestrators\.',
            r'from\s+orchestrators\.',
            r'import\s+src\.orchestrators\.',
            r'import\s+orchestrators\.',
        ]
        
        # Protected directories (never scan for obsolete code)
        self.protected_dirs = {
            '.git',
            '.venv',
            'venv',
            'node_modules',
            '__pycache__',
            '.pytest_cache',
            'cortex-brain',
            '.vscode'
        }
        
        # Protected orchestrators (DO NOT mark as obsolete)
        # These orchestrators have advanced features NOT in utilities
        self.protected_orchestrators = {
            'planning_orchestrator',  # Has UX enhancements: planning mode, session restoration, challenge system
            'git_checkpoint_orchestrator',  # TDD workflow integration, required by planning orchestrator
        }
    
    def _detect_project_root(self) -> Path:
        """Auto-detect CORTEX project root."""
        current = Path.cwd()
        
        if (current / "cortex-operations.yaml").exists():
            return current
        
        for parent in current.parents:
            if (parent / "cortex-operations.yaml").exists():
                return parent
        
        raise FileNotFoundError("Cannot detect CORTEX project root")
    
    def _is_protected_path(self, path: Path) -> bool:
        """Check if path is in protected directory."""
        parts = path.parts
        return any(protected in parts for protected in self.protected_dirs)
    
    def has_migrated_utility(self, orchestrator_name: str) -> bool:
        """
        Check if an orchestrator has a corresponding utility in operations/modules/.
        
        Args:
            orchestrator_name: Name of orchestrator (e.g., 'planning_orchestrator')
        
        Returns:
            True if corresponding utility exists, False otherwise
        """
        # Remove '_orchestrator' suffix
        base_name = orchestrator_name.replace('_orchestrator', '')
        
        # Look for utility in operations/modules/
        modules_dir = self.operations_dir / "modules"
        
        if not modules_dir.exists():
            return False
        
        # Search all category directories
        for category_dir in modules_dir.iterdir():
            if not category_dir.is_dir() or self._is_protected_path(category_dir):
                continue
            
            utility_file = category_dir / f"{base_name}_utility.py"
            if utility_file.exists():
                return True
        
        return False
    
    def scan_for_obsolete_orchestrators(self) -> List[Path]:
        """
        Find orchestrator files that have been migrated to utilities.
        
        Returns:
            List of obsolete orchestrator file paths
        """
        obsolete = []
        
        if not self.orchestrators_dir.exists():
            logger.info(f"Orchestrators directory not found: {self.orchestrators_dir}")
            return obsolete
        
        for file in self.orchestrators_dir.glob("*_orchestrator.py"):
            if file.stem == '__init__':
                continue
            
            # PROTECTION: Check if orchestrator is protected (has advanced features)
            if file.stem in self.protected_orchestrators:
                logger.info(f"Protected orchestrator: {file.name} (has advanced features not in utility)")
                continue
            
            # Check if this orchestrator has been migrated
            if self.has_migrated_utility(file.stem):
                obsolete.append(file)
                logger.info(f"Found obsolete orchestrator: {file.name} (migrated to utility)")
        
        return obsolete
    
    def scan_for_obsolete_tests(self) -> List[Path]:
        """
        Find test files for orchestrators that no longer exist.
        
        Returns:
            List of obsolete test file paths
        """
        obsolete = []
        
        if not self.tests_dir.exists():
            logger.warning(f"Tests directory not found: {self.tests_dir}")
            return obsolete
        
        # Find all test files for orchestrators
        for test_file in self.tests_dir.rglob("test_*_orchestrator.py"):
            if self._is_protected_path(test_file):
                continue
            
            # Extract orchestrator name from test file
            # test_planning_orchestrator.py -> planning_orchestrator
            orch_name = test_file.stem.replace('test_', '')
            
            # Check if orchestrator file exists in multiple locations
            possible_locations = [
                self.orchestrators_dir / f"{orch_name}.py",  # src/orchestrators/
                self.project_root / "src" / "tier3" / "orchestrators" / f"{orch_name}.py",  # src/tier3/orchestrators/
                self.project_root / "src" / "tier2" / "orchestrators" / f"{orch_name}.py",  # src/tier2/orchestrators/
            ]
            
            if not any(loc.exists() for loc in possible_locations):
                obsolete.append(test_file)
                logger.info(f"Found obsolete test: {test_file.name} (orchestrator deleted)")
        
        return obsolete
    
    def scan_for_obsolete_scripts(self) -> List[Path]:
        """
        Find obsolete scripts (backups, deprecated, temp files).
        
        Returns:
            List of obsolete script file paths
        """
        obsolete = []
        
        if not self.scripts_dir.exists():
            logger.warning(f"Scripts directory not found: {self.scripts_dir}")
            return obsolete
        
        for pattern in self.obsolete_script_patterns:
            for file in self.scripts_dir.glob(pattern):
                if file.is_file() and not self._is_protected_path(file):
                    obsolete.append(file)
                    logger.info(f"Found obsolete script: {file.name} (pattern: {pattern})")
        
        # Also check for test scripts in scripts/ directory
        for file in self.scripts_dir.glob("test_*.py"):
            if file.is_file():
                obsolete.append(file)
                logger.info(f"Found test script in scripts/: {file.name} (should be in tests/)")
        
        return obsolete
    
    def analyze_import_usage(self, file_path: Path) -> ImportAnalysis:
        """
        Analyze a file for deprecated import patterns.
        
        Args:
            file_path: Path to file to analyze
        
        Returns:
            ImportAnalysis with findings
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return ImportAnalysis(file=file_path, has_deprecated=False)
        
        # Check each deprecated pattern
        for pattern in self.deprecated_imports:
            matches = re.finditer(pattern, content, re.MULTILINE)
            
            for match in matches:
                # Get line number
                line_number = content[:match.start()].count('\n') + 1
                
                # Get the full import statement
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(content)
                full_line = content[line_start:line_end].strip()
                
                # Suggest replacement
                replacement = full_line.replace('orchestrators', 'operations.modules')
                
                findings.append({
                    'line': line_number,
                    'pattern': pattern,
                    'original': full_line,
                    'replacement': replacement,
                    'type': 'deprecated_import'
                })
        
        return ImportAnalysis(
            file=file_path,
            has_deprecated=len(findings) > 0,
            findings=findings,
            total_deprecated_imports=len(findings)
        )
    
    def scan_all_for_deprecated_imports(self) -> List[ImportAnalysis]:
        """
        Scan all Python files for deprecated imports.
        
        Returns:
            List of ImportAnalysis for files with deprecated imports
        """
        files_with_deprecated = []
        
        # Scan src/ directory
        src_dir = self.project_root / "src"
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                if self._is_protected_path(py_file):
                    continue
                
                analysis = self.analyze_import_usage(py_file)
                if analysis.has_deprecated:
                    files_with_deprecated.append(analysis)
        
        # Scan tests/ directory
        if self.tests_dir.exists():
            for py_file in self.tests_dir.rglob("*.py"):
                if self._is_protected_path(py_file):
                    continue
                
                analysis = self.analyze_import_usage(py_file)
                if analysis.has_deprecated:
                    files_with_deprecated.append(analysis)
        
        logger.info(f"Found {len(files_with_deprecated)} files with deprecated imports")
        return files_with_deprecated
    
    def calculate_total_size(self, files: List[Path]) -> float:
        """
        Calculate total size of files in MB.
        
        Args:
            files: List of file paths
        
        Returns:
            Total size in MB
        """
        total_bytes = 0
        
        for file in files:
            try:
                if file.exists() and file.is_file():
                    total_bytes += file.stat().st_size
            except Exception as e:
                logger.warning(f"Failed to get size of {file}: {e}")
        
        return total_bytes / (1024 * 1024)  # Convert to MB
    
    def detect_all(self) -> Dict[str, List[Path]]:
        """
        Detect all types of obsolete code.
        
        This is a simplified version of generate_cleanup_plan() that returns
        a dictionary with categorized obsolete files.
        
        Returns:
            Dictionary with keys:
                - deprecated: List of obsolete orchestrator files
                - test_files: List of obsolete test files  
                - temp_files: List of obsolete script/temp files
        """
        logger.info("Detecting obsolete code...")
        
        return {
            "deprecated": self.scan_for_obsolete_orchestrators(),
            "test_files": self.scan_for_obsolete_tests(),
            "temp_files": self.scan_for_obsolete_scripts()
        }
    
    def generate_cleanup_plan(self) -> CleanupPlan:
        """
        Generate comprehensive cleanup plan.
        
        Returns:
            CleanupPlan with all detected obsolete code
        """
        logger.info("Scanning for obsolete code...")
        
        # Scan for different types of obsolete code
        obsolete_orchestrators = self.scan_for_obsolete_orchestrators()
        obsolete_tests = self.scan_for_obsolete_tests()
        obsolete_scripts = self.scan_for_obsolete_scripts()
        files_with_deprecated = self.scan_all_for_deprecated_imports()
        
        # Calculate total size
        all_files = obsolete_orchestrators + obsolete_tests + obsolete_scripts
        total_size = self.calculate_total_size(all_files)
        
        plan = CleanupPlan(
            obsolete_orchestrators=obsolete_orchestrators,
            obsolete_tests=obsolete_tests,
            obsolete_scripts=obsolete_scripts,
            files_with_deprecated_imports=files_with_deprecated,
            estimated_removal_size_mb=total_size,
            safety_checks_required=True
        )
        
        logger.info(f"Cleanup plan generated: {plan.total_files} files, {total_size:.2f} MB")
        return plan
    
    def generate_report(self, plan: CleanupPlan) -> str:
        """
        Generate formatted report from cleanup plan.
        
        Args:
            plan: CleanupPlan to format
        
        Returns:
            Formatted markdown report
        """
        report_lines = [
            "# Obsolete Code Detection Report",
            "",
            f"**Total Files:** {plan.total_files}",
            f"**Estimated Size:** {plan.estimated_removal_size_mb:.2f} MB",
            f"**Safety Checks Required:** {'Yes' if plan.safety_checks_required else 'No'}",
            "",
            "## Summary",
            "",
            f"- **Obsolete Orchestrators:** {len(plan.obsolete_orchestrators)} files",
            f"- **Obsolete Tests:** {len(plan.obsolete_tests)} files",
            f"- **Obsolete Scripts:** {len(plan.obsolete_scripts)} files",
            f"- **Files with Deprecated Imports:** {len(plan.files_with_deprecated_imports)} files",
            "",
        ]
        
        if plan.obsolete_orchestrators:
            report_lines.extend([
                "## ⚠️ Obsolete Orchestrators",
                "",
                "These orchestrators have been migrated to utilities and can be removed:",
                ""
            ])
            for file in plan.obsolete_orchestrators:
                size_kb = file.stat().st_size / 1024
                report_lines.append(f"- `{file.name}` ({size_kb:.1f} KB)")
            report_lines.append("")
        
        if plan.obsolete_tests:
            report_lines.extend([
                "## ⚠️ Obsolete Tests",
                "",
                "These tests are for orchestrators that no longer exist:",
                ""
            ])
            for file in plan.obsolete_tests:
                size_kb = file.stat().st_size / 1024
                report_lines.append(f"- `{file.name}` ({size_kb:.1f} KB)")
            report_lines.append("")
        
        if plan.obsolete_scripts:
            report_lines.extend([
                "## ⚠️ Obsolete Scripts",
                "",
                "These scripts are backups, deprecated, or temp files:",
                ""
            ])
            for file in plan.obsolete_scripts:
                size_kb = file.stat().st_size / 1024
                report_lines.append(f"- `{file.name}` ({size_kb:.1f} KB)")
            report_lines.append("")
        
        if plan.files_with_deprecated_imports:
            report_lines.extend([
                "## ⚠️ Files with Deprecated Imports",
                "",
                "These files import from old orchestrators directory:",
                ""
            ])
            for analysis in plan.files_with_deprecated_imports[:10]:  # Limit to first 10
                relative_path = analysis.file.relative_to(self.project_root)
                report_lines.append(
                    f"- `{relative_path}` ({analysis.total_deprecated_imports} imports)"
                )
            
            if len(plan.files_with_deprecated_imports) > 10:
                remaining = len(plan.files_with_deprecated_imports) - 10
                report_lines.append(f"- ... and {remaining} more files")
            report_lines.append("")
        
        report_lines.extend([
            "## 🔧 Recommended Actions",
            "",
            "1. Review obsolete files before deletion",
            "2. Run `align migrate-tests --dry-run` to preview test migrations",
            "3. Run `align cleanup --dry-run` to preview cleanup",
            "4. Run `align cleanup --execute` to perform cleanup (with safety checks)",
            ""
        ])
        
        if plan.total_files == 0:
            report_lines.extend([
                "## ✅ All Clear",
                "",
                "No obsolete code detected. Repository is clean!",
                ""
            ])
        
        return "\n".join(report_lines)


def main():
    """CLI entry point for standalone obsolete detection."""
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        detector = ObsoleteCodeDetector()
        plan = detector.generate_cleanup_plan()
        
        print(detector.generate_report(plan))
        
        # Exit with code 1 if obsolete code found (for CI/CD)
        sys.exit(1 if plan.total_files > 0 else 0)
    
    except Exception as e:
        logger.error(f"Detection failed: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
