"""
Minimal System Alignment Utility - Fast & Reliable Replacement

Lightweight replacement for SystemAlignmentOrchestrator that focuses on
essential system health checks without complex integration scoring.

Design Goals:
    - Execute in <5 seconds
    - Clear pass/fail reporting
    - No complex dependencies
    - Admin-only execution
    - Actionable error messages

Validation Checks (8 Core):
    1. Brain tier structure (tier0-3)
    2. Protection rules (brain-protection-rules.yaml)
    3. Response templates (response-templates.yaml)
    4. Working memory database
    5. Knowledge graph database
    6. Development context database
    7. Core Python modules (orchestrators/agents)
    8. Configuration file (cortex.config.json)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: PRODUCTION
"""

import logging
import json
import sqlite3
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Import centralized config for cross-platform paths
from src.config import config

logger = logging.getLogger(__name__)


def safe_print(message: str) -> None:
    """Print with Unicode fallback for Windows console encoding issues."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Replace emojis with ASCII equivalents
        ascii_message = (message
            .replace('🧠', '[BRAIN]')
            .replace('✅', '[OK]')
            .replace('⚠️', '[WARN]')
            .replace('❌', '[FAIL]')
            .replace('━', '-')
        )
        print(ascii_message)


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    message: str
    details: str = ""
    severity: str = "ERROR"  # ERROR, WARNING, INFO
    
    def __str__(self) -> str:
        """Format for console output."""
        if self.passed:
            icon = "✅ [OK]"
        elif self.severity == "WARNING":
            icon = "⚠️ [WARN]"
        else:
            icon = "❌ [FAIL]"
        
        output = f"{icon} {self.check_name}: {self.message}"
        if self.details:
            output += f"\n  └─ {self.details}"
        return output


@dataclass
class AlignmentReport:
    """Complete system alignment report."""
    timestamp: datetime
    checks: List[ValidationResult] = field(default_factory=list)
    execution_time: float = 0.0
    
    @property
    def passed_count(self) -> int:
        """Count of passed checks."""
        return sum(1 for check in self.checks if check.passed)
    
    @property
    def total_count(self) -> int:
        """Total checks executed."""
        return len(self.checks)
    
    @property
    def is_healthy(self) -> bool:
        """System considered healthy if all ERROR-level checks pass."""
        return all(
            check.passed or check.severity == "WARNING"
            for check in self.checks
        )
    
    @property
    def status_text(self) -> str:
        """Human-readable status."""
        if self.is_healthy:
            return "HEALTHY"
        else:
            failed_critical = sum(
                1 for check in self.checks 
                if not check.passed and check.severity == "ERROR"
            )
            return f"UNHEALTHY ({failed_critical} critical issues)"
    
    def format_console(self) -> str:
        """Format report for console output."""
        lines = [
            "🧠 CORTEX System Alignment Check",
            "━" * 60,
            ""
        ]
        
        for check in self.checks:
            lines.append(str(check))
        
        lines.extend([
            "",
            "━" * 60,
            f"System Status: {self.status_text} ({self.passed_count}/{self.total_count} checks passed)",
            f"Execution Time: {self.execution_time:.1f}s",
        ])
        
        # Add next steps if there are failures
        warnings_or_failures = [
            check for check in self.checks 
            if not check.passed
        ]
        if warnings_or_failures:
            lines.extend([
                "",
                "Next Steps:",
            ])
            for check in warnings_or_failures:
                if check.severity == "ERROR":
                    lines.append(f"• [CRITICAL] {check.details or check.message}")
                else:
                    lines.append(f"• {check.details or check.message}")
        
        return "\n".join(lines)


class AlignUtility:
    """Minimal system alignment validator - fast and reliable."""
    
    def __init__(self):
        """Initialize utility with CORTEX paths."""
        self.brain_path = Path(config.brain_path)
        self.root_path = Path(config.root_path)
        self.start_time = None
    
    def validate_brain_structure(self) -> ValidationResult:
        """Check that all 4 brain tiers exist."""
        try:
            missing_tiers = []
            
            # tier0 is in src/tier0 (code), not cortex-brain/tier0 (data)
            tier0_code_path = self.root_path / "src" / "tier0"
            if not tier0_code_path.exists():
                missing_tiers.append("tier0 (code)")
            
            # tier1-3 are data directories in cortex-brain
            for tier_num in range(1, 4):
                tier_path = self.brain_path / f"tier{tier_num}"
                if not tier_path.exists():
                    missing_tiers.append(f"tier{tier_num} (data)")
            
            if missing_tiers:
                return ValidationResult(
                    check_name="Brain Architecture",
                    passed=False,
                    message=f"Missing tiers: {', '.join(missing_tiers)}",
                    details="Brain tier structure incomplete",
                    severity="ERROR"
                )
            
            return ValidationResult(
                check_name="Brain Architecture",
                passed=True,
                message="All 4 tiers present (tier0 code + tier1-3 data)",
                severity="INFO"
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="Brain Architecture",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_protection_rules(self) -> ValidationResult:
        """Check brain-protection-rules.yaml exists and is valid."""
        try:
            rules_file = self.brain_path / "brain-protection-rules.yaml"
            
            if not rules_file.exists():
                return ValidationResult(
                    check_name="Protection Rules",
                    passed=False,
                    message="brain-protection-rules.yaml not found",
                    details="Critical governance file missing - CORTEX cannot enforce SKULL rules",
                    severity="ERROR"
                )
            
            # Validate YAML structure
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            
            if not rules or not isinstance(rules, dict):
                return ValidationResult(
                    check_name="Protection Rules",
                    passed=False,
                    message="Invalid YAML structure",
                    details="brain-protection-rules.yaml is not a valid YAML dictionary",
                    severity="ERROR"
                )
            
            # Count rules
            rule_count = len(rules.get('rules', []))
            
            return ValidationResult(
                check_name="Protection Rules",
                passed=True,
                message=f"Valid ({rule_count} rules loaded)",
                severity="INFO"
            )
        
        except yaml.YAMLError as e:
            return ValidationResult(
                check_name="Protection Rules",
                passed=False,
                message=f"YAML parsing error: {str(e)}",
                details="Fix YAML syntax in brain-protection-rules.yaml",
                severity="ERROR"
            )
        except Exception as e:
            return ValidationResult(
                check_name="Protection Rules",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_response_templates(self) -> ValidationResult:
        """Check response-templates.yaml exists and is valid."""
        try:
            templates_file = self.brain_path / "response-templates.yaml"
            
            if not templates_file.exists():
                return ValidationResult(
                    check_name="Response Templates",
                    passed=False,
                    message="response-templates.yaml not found",
                    details="Template system unavailable - CORTEX cannot format responses",
                    severity="ERROR"
                )
            
            # Validate YAML structure
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
            
            if not templates or not isinstance(templates, dict):
                return ValidationResult(
                    check_name="Response Templates",
                    passed=False,
                    message="Invalid YAML structure",
                    severity="ERROR"
                )
            
            # Count templates
            template_count = len(templates.get('response_templates', []))
            
            return ValidationResult(
                check_name="Response Templates",
                passed=True,
                message=f"{template_count} templates loaded",
                severity="INFO"
            )
        
        except yaml.YAMLError as e:
            return ValidationResult(
                check_name="Response Templates",
                passed=False,
                message=f"YAML parsing error: {str(e)}",
                severity="ERROR"
            )
        except Exception as e:
            return ValidationResult(
                check_name="Response Templates",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_database(self, db_name: str, tier: int, friendly_name: str) -> ValidationResult:
        """Validate a specific brain database."""
        try:
            db_path = self.brain_path / f"tier{tier}" / db_name
            
            if not db_path.exists():
                return ValidationResult(
                    check_name=friendly_name,
                    passed=False,
                    message=f"Database not found: {db_name}",
                    details=f"Optional - Run 'python3 initialize_databases.py' to create tier{tier} databases",
                    severity="WARNING"  # Changed from ERROR to WARNING - databases are optional
                )
            
            # Check database is readable
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Try to read schema
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            conn.close()
            
            if not tables:
                return ValidationResult(
                    check_name=friendly_name,
                    passed=False,
                    message="Database exists but has no tables",
                    details=f"Database schema not initialized for {db_name}",
                    severity="WARNING"
                )
            
            table_count = len(tables)
            
            return ValidationResult(
                check_name=friendly_name,
                passed=True,
                message=f"Database healthy ({table_count} tables)",
                severity="INFO"
            )
        
        except sqlite3.Error as e:
            return ValidationResult(
                check_name=friendly_name,
                passed=False,
                message=f"SQLite error: {str(e)}",
                details=f"Database corrupted or inaccessible: {db_name}",
                severity="WARNING"  # Changed from ERROR to WARNING
            )
        except Exception as e:
            return ValidationResult(
                check_name=friendly_name,
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="WARNING"  # Changed from ERROR to WARNING
            )
    
    def validate_core_modules(self) -> ValidationResult:
        """Check that core Python modules exist (orchestrators, agents)."""
        try:
            src_path = self.root_path / "src"
            
            if not src_path.exists():
                return ValidationResult(
                    check_name="Core Modules",
                    passed=False,
                    message="src/ directory not found",
                    details="CORTEX source code missing - reinstall required",
                    severity="ERROR"
                )
            
            # Check for key directories
            required_dirs = ["orchestrators", "cortex_agents", "operations"]
            missing_dirs = []
            
            for dir_name in required_dirs:
                if not (src_path / dir_name).exists():
                    missing_dirs.append(dir_name)
            
            if missing_dirs:
                return ValidationResult(
                    check_name="Core Modules",
                    passed=False,
                    message=f"Missing directories: {', '.join(missing_dirs)}",
                    details="Core CORTEX modules missing - reinstall required",
                    severity="ERROR"
                )
            
            # Count orchestrators and agents
            orchestrators = list((src_path / "orchestrators").glob("*.py"))
            agents = list((src_path / "cortex_agents").glob("*.py"))
            
            return ValidationResult(
                check_name="Core Modules",
                passed=True,
                message=f"{len(orchestrators)} orchestrators, {len(agents)} agents discovered",
                severity="INFO"
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="Core Modules",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_configuration(self) -> ValidationResult:
        """Check cortex.config.json exists and is valid."""
        try:
            config_file = self.root_path / "cortex.config.json"
            
            if not config_file.exists():
                return ValidationResult(
                    check_name="Configuration",
                    passed=False,
                    message="cortex.config.json not found",
                    details="Create config from cortex.config.template.json",
                    severity="ERROR"
                )
            
            # Validate JSON structure
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if not config_data or not isinstance(config_data, dict):
                return ValidationResult(
                    check_name="Configuration",
                    passed=False,
                    message="Invalid JSON structure",
                    severity="ERROR"
                )
            
            # Check for critical keys
            if 'machines' not in config_data:
                return ValidationResult(
                    check_name="Configuration",
                    passed=False,
                    message="Missing 'machines' configuration",
                    details="Config file must contain machine-specific paths",
                    severity="WARNING"
                )
            
            return ValidationResult(
                check_name="Configuration",
                passed=True,
                message="cortex.config.json valid",
                severity="INFO"
            )
        
        except json.JSONDecodeError as e:
            return ValidationResult(
                check_name="Configuration",
                passed=False,
                message=f"JSON parsing error: {str(e)}",
                details="Fix JSON syntax in cortex.config.json",
                severity="ERROR"
            )
        except Exception as e:
            return ValidationResult(
                check_name="Configuration",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def run_alignment(self) -> AlignmentReport:
        """Execute all validation checks and generate report."""
        self.start_time = datetime.now()
        
        report = AlignmentReport(timestamp=self.start_time)
        
        # Execute 8 core validation checks
        report.checks.append(self.validate_brain_structure())
        report.checks.append(self.validate_protection_rules())
        report.checks.append(self.validate_response_templates())
        report.checks.append(self.validate_database("working_memory.db", 1, "Working Memory"))
        report.checks.append(self.validate_database("knowledge_graph.db", 2, "Knowledge Graph"))
        report.checks.append(self.validate_database("development_context.db", 3, "Development Context"))
        report.checks.append(self.validate_core_modules())
        report.checks.append(self.validate_configuration())
        
        # Calculate execution time
        end_time = datetime.now()
        report.execution_time = (end_time - self.start_time).total_seconds()
        
        return report


def run_align_utility() -> Dict[str, Any]:
    """
    Entry point for align utility - callable from orchestrators or CLI.
    
    Returns:
        Dict with 'success', 'message', 'report_text', 'report_data'
    """
    try:
        utility = AlignUtility()
        report = utility.run_alignment()
        
        # Format console output
        console_output = report.format_console()
        safe_print(console_output)
        
        # Return structured data for programmatic access
        return {
            'success': report.is_healthy,
            'message': f"System Status: {report.status_text}",
            'report_text': console_output,
            'report_data': {
                'timestamp': report.timestamp.isoformat(),
                'execution_time': report.execution_time,
                'checks_passed': report.passed_count,
                'checks_total': report.total_count,
                'is_healthy': report.is_healthy,
                'checks': [
                    {
                        'name': check.check_name,
                        'passed': check.passed,
                        'message': check.message,
                        'details': check.details,
                        'severity': check.severity
                    }
                    for check in report.checks
                ]
            }
        }
    
    except Exception as e:
        error_message = f"Align utility execution failed: {str(e)}"
        logger.error(error_message, exc_info=True)
        return {
            'success': False,
            'message': error_message,
            'report_text': error_message,
            'report_data': None
        }


if __name__ == "__main__":
    """CLI execution for testing."""
    import sys
    result = run_align_utility()
    sys.exit(0 if result['success'] else 1)
