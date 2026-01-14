"""
Repository Structure Validator - feat08-cleanup Phase 2

Validates repository structure for organizational integrity:
- No orphaned files in root
- All tests in tests/
- All source in src/
- Brain structure valid

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set


@dataclass
class StructureViolation:
    """Represents a structure validation violation"""
    severity: str  # ERROR, WARNING, INFO
    category: str  # orphaned_file, misplaced_test, misplaced_source, invalid_brain
    path: Path
    message: str
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "severity": self.severity,
            "category": self.category,
            "path": str(self.path),
            "message": self.message,
            "recommendation": self.recommendation
        }


@dataclass
class StructureReport:
    """Complete structure validation report"""
    workspace: Path
    timestamp: str
    valid: bool
    violations: List[StructureViolation] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "workspace": str(self.workspace),
            "timestamp": self.timestamp,
            "valid": self.valid,
            "violations": [v.to_dict() for v in self.violations],
            "stats": self.stats,
            "recommendations": self.recommendations
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict(), indent=indent)


class RepositoryStructureValidator:
    """
    Validates repository structure for organizational integrity
    
    Checks:
    1. No orphaned files in root (except allowed files)
    2. All tests in tests/ directory
    3. All source in src/ directory
    4. Brain structure valid (cortex-brain/)
    """
    
    # Files allowed in repository root
    ALLOWED_ROOT_FILES = {
        "README.md",
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        ".gitignore",
        ".gitattributes",
        "requirements.txt",
        "setup.py",
        "setup.cfg",
        "pyproject.toml",
        "pytest.ini",
        "mypy.ini",
        ".pylintrc",
        "tox.ini",
        "Makefile",
        "Dockerfile",
        ".dockerignore",
        "docker-compose.yml",
        ".env.example",
        "package.json",
        "package-lock.json",
        "tsconfig.json",
        ".editorconfig",
        ".pre-commit-config.yaml",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "AUTHORS.md",
        "DEPLOYMENT.md",
        "QUICK-LAUNCH.md",
        "PUBLISH-GUIDE.txt",
        "GIT-SYNC-INSTRUCTIONS-ACTIVE-PLANS.md",
        "cortex.config.json",
        "deployment-manifest.json",
        "cortex-operations.yaml",
        # Scripts (common in repos)
        "cortex-cleanup.ps1",
        "cortex-upgrade.ps1",
        "cortex-upgrade.sh",
        "create-cortex-5.5-branch.ps1",
        "cortex-upgrade-plan.py"
    }
    
    # Directories allowed in repository root
    ALLOWED_ROOT_DIRS = {
        "src",
        "tests",
        "docs",
        "scripts",
        "cortex-brain",
        "cortex-toolkit",
        "cortex-sample-apps",
        "cortex-lens-output",
        "logs",
        ".git",
        ".github",
        ".asif",
        ".vscode",
        ".idea",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        "venv",
        ".venv",
        "env",
        ".env",
        "node_modules",
        "dist",
        "build",
        ".eggs",
        "*.egg-info"
    }
    
    # Required brain subdirectories
    REQUIRED_BRAIN_DIRS = {
        "tier0",
        "tier1",
        "tier2",
        "tier3",
        "manifests",
        "config",
        "documents"
    }
    
    def __init__(self, workspace: Path):
        """
        Initialize validator
        
        Args:
            workspace: Repository root directory
        """
        self.workspace = Path(workspace)
        self.violations: List[StructureViolation] = []
        
    def validate(self) -> StructureReport:
        """
        Validate repository structure
        
        Returns:
            StructureReport with validation results
        """
        self.violations = []
        
        # Run all validations
        self._validate_root_files()
        self._validate_test_files()
        self._validate_source_files()
        self._validate_brain_structure()
        
        # Calculate statistics
        stats = self._calculate_stats()
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        # Create report
        report = StructureReport(
            workspace=self.workspace,
            timestamp=datetime.now().isoformat(),
            valid=len([v for v in self.violations if v.severity == "ERROR"]) == 0,
            violations=self.violations,
            stats=stats,
            recommendations=recommendations
        )
        
        return report
    
    def _validate_root_files(self) -> None:
        """Validate no orphaned files in root"""
        if not self.workspace.exists():
            self.violations.append(StructureViolation(
                severity="ERROR",
                category="invalid_workspace",
                path=self.workspace,
                message=f"Workspace does not exist: {self.workspace}",
                recommendation="Verify workspace path is correct"
            ))
            return
        
        # Check root directory
        for item in self.workspace.iterdir():
            # Skip allowed directories
            if item.is_dir():
                if not self._is_allowed_dir(item.name):
                    self.violations.append(StructureViolation(
                        severity="WARNING",
                        category="orphaned_directory",
                        path=item,
                        message=f"Unexpected directory in root: {item.name}",
                        recommendation=f"Move to appropriate location or add to ALLOWED_ROOT_DIRS"
                    ))
            else:
                # Check if file is allowed
                if not self._is_allowed_file(item.name):
                    self.violations.append(StructureViolation(
                        severity="ERROR",
                        category="orphaned_file",
                        path=item,
                        message=f"Orphaned file in root: {item.name}",
                        recommendation=f"Move to docs/, scripts/, or appropriate location"
                    ))
    
    def _validate_test_files(self) -> None:
        """Validate all test files are in tests/"""
        # Find test files outside tests/
        for pattern in ["**/test_*.py", "**/*_test.py"]:
            for test_file in self.workspace.glob(pattern):
                # Skip if in tests/ directory
                if "tests" in test_file.parts:
                    continue
                
                # Skip if in virtual environments
                if any(venv in test_file.parts for venv in ["venv", ".venv", "env", ".env", "node_modules"]):
                    continue
                
                self.violations.append(StructureViolation(
                    severity="ERROR",
                    category="misplaced_test",
                    path=test_file,
                    message=f"Test file outside tests/ directory: {test_file.name}",
                    recommendation=f"Move to tests/ with appropriate subdirectory structure"
                ))
    
    def _validate_source_files(self) -> None:
        """Validate all source files are in src/"""
        # Find Python files outside src/ (but not tests)
        for py_file in self.workspace.glob("**/*.py"):
            # Skip if in src/ or tests/
            if "src" in py_file.parts or "tests" in py_file.parts:
                continue
            
            # Skip if in allowed root dirs
            if any(d in py_file.parts for d in self.ALLOWED_ROOT_DIRS):
                continue
            
            # Skip if it's a setup.py or similar
            if py_file.name in ["setup.py", "conftest.py", "cortex-upgrade-plan.py"]:
                continue
            
            # Skip if in hidden directories
            if any(part.startswith(".") for part in py_file.parts):
                continue
            
            # Skip if in virtual environments
            if any(venv in py_file.parts for venv in ["venv", ".venv", "env", ".env", "node_modules"]):
                continue
            
            self.violations.append(StructureViolation(
                severity="WARNING",
                category="misplaced_source",
                path=py_file,
                message=f"Source file outside src/: {py_file}",
                recommendation=f"Move to src/ with appropriate module structure"
            ))
    
    def _validate_brain_structure(self) -> None:
        """Validate cortex-brain structure"""
        brain_dir = self.workspace / "cortex-brain"
        
        if not brain_dir.exists():
            # Brain directory is optional for non-CORTEX repos
            return
        
        # Check required subdirectories
        for required_dir in self.REQUIRED_BRAIN_DIRS:
            dir_path = brain_dir / required_dir
            if not dir_path.exists():
                self.violations.append(StructureViolation(
                    severity="WARNING",
                    category="invalid_brain",
                    path=dir_path,
                    message=f"Missing required brain directory: {required_dir}",
                    recommendation=f"Create {required_dir} directory in cortex-brain/"
                ))
    
    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file is allowed in root"""
        # Check exact matches
        if filename in self.ALLOWED_ROOT_FILES:
            return True
        
        # Check patterns
        if filename.startswith("."):
            return True  # Hidden files usually OK
        
        return False
    
    def _is_allowed_dir(self, dirname: str) -> bool:
        """Check if directory is allowed in root"""
        # Check exact matches
        if dirname in self.ALLOWED_ROOT_DIRS:
            return True
        
        # Check patterns
        if dirname.startswith("."):
            return True  # Hidden dirs usually OK
        
        # Check glob patterns
        import fnmatch
        for pattern in self.ALLOWED_ROOT_DIRS:
            if fnmatch.fnmatch(dirname, pattern):
                return True
        
        return False
    
    def _calculate_stats(self) -> Dict[str, Any]:
        """Calculate validation statistics"""
        total_violations = len(self.violations)
        errors = len([v for v in self.violations if v.severity == "ERROR"])
        warnings = len([v for v in self.violations if v.severity == "WARNING"])
        info = len([v for v in self.violations if v.severity == "INFO"])
        
        # Count by category
        by_category = {}
        for violation in self.violations:
            cat = violation.category
            if cat not in by_category:
                by_category[cat] = 0
            by_category[cat] += 1
        
        # Count files/dirs
        src_files = len(list(self.workspace.glob("src/**/*.py")))
        test_files = len(list(self.workspace.glob("tests/**/*.py")))
        
        return {
            "total_violations": total_violations,
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "by_category": by_category,
            "src_files": src_files,
            "test_files": test_files,
            "has_brain": (self.workspace / "cortex-brain").exists()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []
        
        errors = [v for v in self.violations if v.severity == "ERROR"]
        warnings = [v for v in self.violations if v.severity == "WARNING"]
        
        if errors:
            recommendations.append(f"Fix {len(errors)} ERROR violations before proceeding")
        
        if warnings:
            recommendations.append(f"Review {len(warnings)} WARNING violations for cleanup")
        
        # Category-specific recommendations
        orphaned_files = [v for v in self.violations if v.category == "orphaned_file"]
        if orphaned_files:
            recommendations.append(f"Move {len(orphaned_files)} orphaned files to appropriate locations")
        
        misplaced_tests = [v for v in self.violations if v.category == "misplaced_test"]
        if misplaced_tests:
            recommendations.append(f"Move {len(misplaced_tests)} test files to tests/ directory")
        
        misplaced_source = [v for v in self.violations if v.category == "misplaced_source"]
        if misplaced_source:
            recommendations.append(f"Move {len(misplaced_source)} source files to src/ directory")
        
        invalid_brain = [v for v in self.violations if v.category == "invalid_brain"]
        if invalid_brain:
            recommendations.append(f"Fix {len(invalid_brain)} brain structure issues")
        
        if not self.violations:
            recommendations.append("✅ Repository structure is valid!")
        
        return recommendations


def generate_structure_report(report: StructureReport, output_path: Optional[Path] = None) -> str:
    """
    Generate human-readable structure report
    
    Args:
        report: Structure report
        output_path: Optional path to save report
    
    Returns:
        Report text
    """
    status = "✅ VALID" if report.valid else "❌ INVALID"
    
    report_text = f"""
╔══════════════════════════════════════════════════════════════╗
║         REPOSITORY STRUCTURE VALIDATION REPORT               ║
╚══════════════════════════════════════════════════════════════╝

Workspace: {report.workspace}
Timestamp: {report.timestamp}
Status: {status}

Statistics:
  Total Violations: {report.stats['total_violations']}
  Errors: {report.stats['errors']}
  Warnings: {report.stats['warnings']}
  Info: {report.stats['info']}
  
  Source Files: {report.stats['src_files']} (in src/)
  Test Files: {report.stats['test_files']} (in tests/)
  Brain Structure: {"Present" if report.stats['has_brain'] else "Not present"}
"""
    
    if report.violations:
        report_text += "\n\nViolations:\n"
        
        # Group by severity
        errors = [v for v in report.violations if v.severity == "ERROR"]
        warnings = [v for v in report.violations if v.severity == "WARNING"]
        info = [v for v in report.violations if v.severity == "INFO"]
        
        if errors:
            report_text += f"\n  ❌ ERRORS ({len(errors)}):\n"
            for violation in errors[:10]:  # First 10
                report_text += f"    - {violation.path.name}: {violation.message}\n"
            if len(errors) > 10:
                report_text += f"    ... and {len(errors) - 10} more\n"
        
        if warnings:
            report_text += f"\n  ⚠️  WARNINGS ({len(warnings)}):\n"
            for violation in warnings[:10]:
                report_text += f"    - {violation.path.name}: {violation.message}\n"
            if len(warnings) > 10:
                report_text += f"    ... and {len(warnings) - 10} more\n"
    
    if report.recommendations:
        report_text += "\n\nRecommendations:\n"
        for rec in report.recommendations:
            report_text += f"  • {rec}\n"
    
    if output_path:
        output_path.write_text(report_text)
    
    return report_text
