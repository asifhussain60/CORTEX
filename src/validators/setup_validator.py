"""
Setup validation framework for CORTEX installation
Validates directories, configs, databases, and dependencies

Part of Phase 4: Alignment Orchestrator
"""

import json
import sqlite3
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
import importlib


class IssueSeverity(Enum):
    """Severity levels for validation issues"""
    CRITICAL = "critical"  # System cannot function
    ERROR = "error"        # Major functionality broken
    WARNING = "warning"    # Minor issues, system still works
    INFO = "info"         # Informational, no action needed


@dataclass
class ValidationIssue:
    """Represents a validation issue found during checks"""
    severity: IssueSeverity
    category: str
    description: str
    fix_suggestion: str
    affected_path: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validation checks"""
    is_valid: bool
    issues: List[ValidationIssue]
    
    def get_issues_by_severity(self, severity: IssueSeverity) -> List[ValidationIssue]:
        """Filter issues by severity level"""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def has_critical_issues(self) -> bool:
        """Check if any critical issues exist"""
        return any(issue.severity == IssueSeverity.CRITICAL for issue in self.issues)


class SetupValidator:
    """
    Validates CORTEX installation integrity
    
    Checks:
    - Brain directory structure (tier0-tier3, documents)
    - Configuration files (cortex.config.json)
    - Database schemas (working_memory.db, etc.)
    - Python dependencies
    - Critical brain files
    """
    
    REQUIRED_BRAIN_DIRS = [
        "tier0",
        "tier1", 
        "tier2",
        "tier3",
        "documents",
        "admin",
        "agents"
    ]
    
    REQUIRED_BRAIN_FILES = [
        "brain-protection-rules.yaml",
        "response-templates.yaml",
        "capabilities.yaml"
    ]
    
    REQUIRED_DATABASES = {
        "tier1/working_memory.db": ["conversations", "entities"],
        "tier2/knowledge_graph.db": ["patterns", "relationships"],
        "tier3/development_context.db": ["metrics", "hotspots"]
    }
    
    REQUIRED_PYTHON_PACKAGES = [
        "yaml",
        "sqlite3",
        "pydantic",
        "pytest"
    ]
    
    def __init__(self, root_path: Path):
        """
        Initialize validator
        
        Args:
            root_path: Path to CORTEX root directory
        """
        self.root_path = Path(root_path)
        self.brain_path = self.root_path / "cortex-brain"
    
    def validate_brain_directories(self) -> ValidationResult:
        """
        Validate brain directory structure exists
        
        Returns:
            ValidationResult with any missing directory issues
        """
        issues = []
        
        # Check brain directory exists
        if not self.brain_path.exists():
            issues.append(ValidationIssue(
                severity=IssueSeverity.CRITICAL,
                category="directory",
                description="Brain directory not found: cortex-brain/",
                fix_suggestion="Run 'cortex init' to create brain structure",
                affected_path=str(self.brain_path)
            ))
            return ValidationResult(is_valid=False, issues=issues)
        
        # Check each required subdirectory
        for dir_name in self.REQUIRED_BRAIN_DIRS:
            dir_path = self.brain_path / dir_name
            if not dir_path.exists():
                issues.append(ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    category="directory",
                    description=f"Required directory missing: cortex-brain/{dir_name}/",
                    fix_suggestion=f"Create directory: mkdir -p {dir_path}",
                    affected_path=str(dir_path)
                ))
        
        is_valid = len(issues) == 0
        return ValidationResult(is_valid=is_valid, issues=issues)
    
    def validate_config_file(self) -> ValidationResult:
        """
        Validate cortex.config.json exists and has valid structure
        
        Returns:
            ValidationResult with any config issues
        """
        issues = []
        config_path = self.root_path / "cortex.config.json"
        
        # Check file exists
        if not config_path.exists():
            issues.append(ValidationIssue(
                severity=IssueSeverity.CRITICAL,
                category="config",
                description="Configuration file not found: cortex.config.json",
                fix_suggestion="Copy cortex.config.template.json to cortex.config.json and configure",
                affected_path=str(config_path)
            ))
            return ValidationResult(is_valid=False, issues=issues)
        
        # Check valid JSON
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            issues.append(ValidationIssue(
                severity=IssueSeverity.CRITICAL,
                category="config",
                description=f"Configuration file has invalid JSON: {str(e)}",
                fix_suggestion="Fix JSON syntax or restore from cortex.config.template.json",
                affected_path=str(config_path)
            ))
            return ValidationResult(is_valid=False, issues=issues)
        
        # Check required keys
        if "machines" not in config:
            issues.append(ValidationIssue(
                severity=IssueSeverity.ERROR,
                category="config",
                description="Configuration missing required 'machines' key",
                fix_suggestion="Add 'machines' section with hostname configuration",
                affected_path=str(config_path)
            ))
        
        if "version" not in config:
            issues.append(ValidationIssue(
                severity=IssueSeverity.WARNING,
                category="config",
                description="Configuration missing 'version' field",
                fix_suggestion="Add 'version' field to track CORTEX version",
                affected_path=str(config_path)
            ))
        
        is_valid = len(issues) == 0
        return ValidationResult(is_valid=is_valid, issues=issues)
    
    def validate_database_schemas(self) -> ValidationResult:
        """
        Validate database files exist and have correct schemas
        
        Returns:
            ValidationResult with any database issues
        """
        issues = []
        
        for db_relative_path, required_tables in self.REQUIRED_DATABASES.items():
            db_path = self.brain_path / db_relative_path
            
            # Check database file exists
            if not db_path.exists():
                issues.append(ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    category="database",
                    description=f"Database not found: {db_relative_path}",
                    fix_suggestion=f"Initialize database: python scripts/init_db.py",
                    affected_path=str(db_path)
                ))
                continue
            
            # Check schema has required tables
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                for required_table in required_tables:
                    if required_table not in existing_tables:
                        issues.append(ValidationIssue(
                            severity=IssueSeverity.WARNING,
                            category="database",
                            description=f"Table '{required_table}' missing in {db_relative_path}",
                            fix_suggestion=f"Run schema migration for {db_relative_path}",
                            affected_path=str(db_path)
                        ))
            except sqlite3.Error as e:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    category="database",
                    description=f"Cannot read database {db_relative_path}: {str(e)}",
                    fix_suggestion=f"Restore database from backup or reinitialize",
                    affected_path=str(db_path)
                ))
        
        is_valid = len(issues) == 0
        return ValidationResult(is_valid=is_valid, issues=issues)
    
    def validate_python_dependencies(self) -> ValidationResult:
        """
        Validate required Python packages are installed
        
        Returns:
            ValidationResult with any missing dependency issues
        """
        issues = []
        
        for package_name in self.REQUIRED_PYTHON_PACKAGES:
            try:
                importlib.import_module(package_name)
            except ImportError:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    category="dependency",
                    description=f"Required Python package not found: {package_name}",
                    fix_suggestion=f"Install package: pip install {package_name}",
                    affected_path=None
                ))
        
        is_valid = len(issues) == 0
        return ValidationResult(is_valid=is_valid, issues=issues)
    
    def validate_brain_files(self) -> ValidationResult:
        """
        Validate critical brain files exist
        
        Returns:
            ValidationResult with any missing file issues
        """
        issues = []
        
        for file_name in self.REQUIRED_BRAIN_FILES:
            file_path = self.brain_path / file_name
            
            if not file_path.exists():
                issues.append(ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category="brain_file",
                    description=f"Critical brain file missing: {file_name}",
                    fix_suggestion=f"Restore from backup or run 'cortex repair'",
                    affected_path=str(file_path)
                ))
        
        is_valid = len(issues) == 0
        return ValidationResult(is_valid=is_valid, issues=issues)
    
    def validate_all(self) -> ValidationResult:
        """
        Run all validation checks
        
        Returns:
            Comprehensive ValidationResult with all issues
        """
        all_issues = []
        
        # Run all validations
        validations = [
            self.validate_brain_directories(),
            self.validate_config_file(),
            self.validate_brain_files(),
            self.validate_database_schemas(),
            self.validate_python_dependencies()
        ]
        
        for result in validations:
            all_issues.extend(result.issues)
        
        # Overall validity based on critical issues
        is_valid = not any(
            issue.severity == IssueSeverity.CRITICAL 
            for issue in all_issues
        )
        
        return ValidationResult(is_valid=is_valid, issues=all_issues)
    
    def generate_report(self, result: ValidationResult) -> str:
        """
        Generate human-readable validation report
        
        Args:
            result: ValidationResult to format
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("CORTEX SETUP VALIDATION REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        if result.is_valid:
            lines.append("✅ Validation PASSED - No critical issues found")
        else:
            lines.append("❌ Validation FAILED - Issues detected")
        
        lines.append("")
        lines.append(f"Total Issues: {len(result.issues)}")
        
        # Group by severity
        for severity in IssueSeverity:
            severity_issues = result.get_issues_by_severity(severity)
            if severity_issues:
                lines.append(f"\n{severity.value.upper()}: {len(severity_issues)} issue(s)")
                lines.append("-" * 70)
                
                for issue in severity_issues:
                    lines.append(f"\n[{issue.category}] {issue.description}")
                    lines.append(f"  Fix: {issue.fix_suggestion}")
                    if issue.affected_path:
                        lines.append(f"  Path: {issue.affected_path}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
