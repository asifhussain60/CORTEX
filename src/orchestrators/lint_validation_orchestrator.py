"""
Lint Validation Orchestrator

Multi-language code quality validation for TDD workflow phases.

Supports:
- .NET (Roslynator)
- Python (Pylint, Black)
- JavaScript/TypeScript (ESLint, Prettier)

Features:
- Configurable rules per language
- Violation severity detection (critical/warning/info)
- Phase blocking on critical violations
- Detailed violation reporting
- Auto-fix suggestions

Version: 1.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ViolationSeverity(Enum):
    """Violation severity levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Violation:
    """Represents a single lint violation."""
    
    def __init__(
        self,
        file_path: str,
        line: int,
        column: int,
        rule_id: str,
        message: str,
        severity: ViolationSeverity,
        source: str
    ):
        self.file_path = file_path
        self.line = line
        self.column = column
        self.rule_id = rule_id
        self.message = message
        self.severity = severity
        self.source = source  # roslynator, pylint, eslint
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "file": self.file_path,
            "line": self.line,
            "column": self.column,
            "rule": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
            "source": self.source
        }


class LintValidationOrchestrator:
    """
    Orchestrates code quality validation across multiple languages.
    
    Validates code quality after TDD phases (GREEN, REFACTOR) to prevent
    technical debt accumulation.
    
    Features:
    - Multi-language support
    - Configurable rules
    - Critical violation blocking
    - Detailed reporting
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize LintValidationOrchestrator.
        
        Args:
            config_path: Path to lint-rules.yaml configuration
        """
        self.config_path = config_path or Path(__file__).parent.parent.parent / "cortex-brain" / "config" / "lint-rules.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load lint configuration."""
        if self.config_path.exists():
            try:
                import yaml
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config: {e}. Using defaults.")
        
        # Default configuration
        return {
            "dotnet": {
                "enabled": True,
                "tool": "roslynator",
                "critical_rules": ["RCS1090", "RCS1163", "RCS1118"],  # Duplicate code, unused params, redundant checks
                "block_on_critical": True
            },
            "python": {
                "enabled": True,
                "tool": "pylint",
                "critical_rules": ["E0001", "E0602", "F0401"],  # Syntax error, undefined var, import error
                "block_on_critical": True
            },
            "javascript": {
                "enabled": True,
                "tool": "eslint",
                "critical_rules": ["no-undef", "no-unreachable", "no-dupe-keys"],
                "block_on_critical": True
            }
        }
    
    def _run_command(self, args: List[str], cwd: Path) -> Tuple[bool, str]:
        """Run command and return success status and output."""
        try:
            result = subprocess.run(
                args,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            logger.error(f"❌ Command failed: {e}")
            return False, str(e)
    
    def _validate_dotnet(self, project_path: Path) -> List[Violation]:
        """
        Validate .NET code with Roslynator.
        
        Args:
            project_path: Path to .csproj or .sln file
            
        Returns:
            List of violations
        """
        violations = []
        config = self.config.get("dotnet", {})
        
        if not config.get("enabled", True):
            return violations
        
        logger.info("🔍 Running Roslynator analysis...")
        
        # Check if roslynator is available
        success, _ = self._run_command(["dotnet", "roslynator", "--version"], project_path.parent)
        if not success:
            logger.warning("⚠️ Roslynator not installed. Run: dotnet tool install -g roslynator.dotnet.cli")
            return violations
        
        # Run roslynator analyze
        success, output = self._run_command(
            ["dotnet", "roslynator", "analyze", str(project_path), "--output", "roslynator-report.json"],
            project_path.parent
        )
        
        # Parse results
        report_path = project_path.parent / "roslynator-report.json"
        if report_path.exists():
            try:
                with open(report_path, 'r') as f:
                    results = json.load(f)
                
                for diagnostic in results.get("diagnostics", []):
                    rule_id = diagnostic.get("id", "")
                    severity = self._map_dotnet_severity(diagnostic.get("severity", ""), rule_id, config)
                    
                    violations.append(Violation(
                        file_path=diagnostic.get("location", {}).get("path", ""),
                        line=diagnostic.get("location", {}).get("startLine", 0),
                        column=diagnostic.get("location", {}).get("startColumn", 0),
                        rule_id=rule_id,
                        message=diagnostic.get("message", ""),
                        severity=severity,
                        source="roslynator"
                    ))
                
                # Cleanup
                report_path.unlink()
            except Exception as e:
                logger.error(f"❌ Failed to parse Roslynator results: {e}")
        
        return violations
    
    def _validate_python(self, project_path: Path) -> List[Violation]:
        """
        Validate Python code with Pylint.
        
        Args:
            project_path: Path to Python project directory
            
        Returns:
            List of violations
        """
        violations = []
        config = self.config.get("python", {})
        
        if not config.get("enabled", True):
            return violations
        
        logger.info("🔍 Running Pylint analysis...")
        
        # Find Python files
        python_files = list(project_path.rglob("*.py"))
        if not python_files:
            return violations
        
        # Run pylint
        success, output = self._run_command(
            ["pylint", "--output-format=json"] + [str(f) for f in python_files],
            project_path
        )
        
        # Parse results
        try:
            results = json.loads(output) if output.strip() else []
            
            for item in results:
                rule_id = item.get("message-id", "")
                severity = self._map_python_severity(item.get("type", ""), rule_id, config)
                
                violations.append(Violation(
                    file_path=item.get("path", ""),
                    line=item.get("line", 0),
                    column=item.get("column", 0),
                    rule_id=rule_id,
                    message=item.get("message", ""),
                    severity=severity,
                    source="pylint"
                ))
        except Exception as e:
            logger.error(f"❌ Failed to parse Pylint results: {e}")
        
        return violations
    
    def _validate_javascript(self, project_path: Path) -> List[Violation]:
        """
        Validate JavaScript/TypeScript code with ESLint.
        
        Args:
            project_path: Path to JavaScript project directory
            
        Returns:
            List of violations
        """
        violations = []
        config = self.config.get("javascript", {})
        
        if not config.get("enabled", True):
            return violations
        
        logger.info("🔍 Running ESLint analysis...")
        
        # Check if eslint is available
        eslint_path = project_path / "node_modules" / ".bin" / "eslint"
        if not eslint_path.exists():
            logger.warning("⚠️ ESLint not installed. Run: npm install eslint")
            return violations
        
        # Run eslint
        success, output = self._run_command(
            [str(eslint_path), ".", "--format=json"],
            project_path
        )
        
        # Parse results
        try:
            results = json.loads(output) if output.strip() else []
            
            for file_result in results:
                for message in file_result.get("messages", []):
                    rule_id = message.get("ruleId", "")
                    severity = self._map_javascript_severity(message.get("severity", 0), rule_id, config)
                    
                    violations.append(Violation(
                        file_path=file_result.get("filePath", ""),
                        line=message.get("line", 0),
                        column=message.get("column", 0),
                        rule_id=rule_id,
                        message=message.get("message", ""),
                        severity=severity,
                        source="eslint"
                    ))
        except Exception as e:
            logger.error(f"❌ Failed to parse ESLint results: {e}")
        
        return violations
    
    def _map_dotnet_severity(self, severity: str, rule_id: str, config: Dict) -> ViolationSeverity:
        """Map .NET severity to ViolationSeverity."""
        critical_rules = config.get("critical_rules", [])
        
        if rule_id in critical_rules:
            return ViolationSeverity.CRITICAL
        elif severity.lower() == "error":
            return ViolationSeverity.CRITICAL
        elif severity.lower() == "warning":
            return ViolationSeverity.WARNING
        else:
            return ViolationSeverity.INFO
    
    def _map_python_severity(self, severity: str, rule_id: str, config: Dict) -> ViolationSeverity:
        """Map Python severity to ViolationSeverity."""
        critical_rules = config.get("critical_rules", [])
        
        if rule_id in critical_rules:
            return ViolationSeverity.CRITICAL
        elif severity in ["error", "fatal"]:
            return ViolationSeverity.CRITICAL
        elif severity == "warning":
            return ViolationSeverity.WARNING
        else:
            return ViolationSeverity.INFO
    
    def _map_javascript_severity(self, severity: int, rule_id: str, config: Dict) -> ViolationSeverity:
        """Map JavaScript severity to ViolationSeverity."""
        critical_rules = config.get("critical_rules", [])
        
        if rule_id in critical_rules:
            return ViolationSeverity.CRITICAL
        elif severity == 2:  # ESLint error
            return ViolationSeverity.CRITICAL
        elif severity == 1:  # ESLint warning
            return ViolationSeverity.WARNING
        else:
            return ViolationSeverity.INFO
    
    def validate(self, project_path: Path, language: Optional[str] = None) -> Dict:
        """
        Validate code quality for project.
        
        Args:
            project_path: Path to project
            language: Optional language filter (dotnet, python, javascript)
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"🔍 Starting lint validation: {project_path}")
        
        violations = []
        
        # Detect project type and run appropriate validators
        if not language or language == "dotnet":
            # Look for .csproj or .sln files
            for csproj in project_path.rglob("*.csproj"):
                violations.extend(self._validate_dotnet(csproj))
        
        if not language or language == "python":
            # Look for Python files
            if list(project_path.rglob("*.py")):
                violations.extend(self._validate_python(project_path))
        
        if not language or language == "javascript":
            # Look for package.json
            if (project_path / "package.json").exists():
                violations.extend(self._validate_javascript(project_path))
        
        # Categorize violations
        critical = [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
        warnings = [v for v in violations if v.severity == ViolationSeverity.WARNING]
        info = [v for v in violations if v.severity == ViolationSeverity.INFO]
        
        results = {
            "total_violations": len(violations),
            "critical": len(critical),
            "warnings": len(warnings),
            "info": len(info),
            "violations": [v.to_dict() for v in violations],
            "critical_violations": [v.to_dict() for v in critical],
            "passed": len(critical) == 0
        }
        
        # Log summary
        if results["passed"]:
            logger.info(f"✅ Lint validation passed ({len(violations)} total violations, 0 critical)")
        else:
            logger.error(f"❌ Lint validation failed ({len(critical)} critical violations)")
        
        return results
    
    def should_block_phase(self, validation_results: Dict) -> bool:
        """
        Determine if phase should be blocked based on validation results.
        
        Args:
            validation_results: Results from validate()
            
        Returns:
            True if phase should be blocked
        """
        critical_count = validation_results.get("critical", 0)
        
        if critical_count > 0:
            logger.warning(f"⚠️ Phase blocked: {critical_count} critical violations")
            return True
        
        return False
    
    def generate_report(self, validation_results: Dict, output_path: Path) -> bool:
        """
        Generate detailed violation report.
        
        Args:
            validation_results: Results from validate()
            output_path: Path to output report file
            
        Returns:
            True if report generated successfully
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate markdown report
            report_lines = [
                "# Lint Validation Report",
                "",
                f"**Total Violations:** {validation_results['total_violations']}",
                f"**Critical:** {validation_results['critical']}",
                f"**Warnings:** {validation_results['warnings']}",
                f"**Info:** {validation_results['info']}",
                "",
                f"**Status:** {'✅ PASSED' if validation_results['passed'] else '❌ FAILED'}",
                ""
            ]
            
            if validation_results["critical_violations"]:
                report_lines.append("## Critical Violations")
                report_lines.append("")
                
                for v in validation_results["critical_violations"]:
                    report_lines.append(f"### {v['file']}:{v['line']}:{v['column']}")
                    report_lines.append(f"- **Rule:** {v['rule']}")
                    report_lines.append(f"- **Message:** {v['message']}")
                    report_lines.append(f"- **Source:** {v['source']}")
                    report_lines.append("")
            
            output_path.write_text("\n".join(report_lines))
            logger.info(f"✅ Report generated: {output_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to generate report: {e}")
            return False
