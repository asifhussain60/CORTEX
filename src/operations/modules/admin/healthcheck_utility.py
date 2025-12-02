"""
Minimal Health Check Utility - Fast & Reliable

Lightweight healthcheck for CORTEX system monitoring without complex dependencies.

Design Goals:
    - Execute in <3 seconds
    - Clear pass/fail reporting
    - No complex dependencies
    - User-facing operation
    - Actionable error messages

Health Checks (8 Core):
    1. System resources (CPU, memory, disk)
    2. Brain tier structure (tier0-3)
    3. Database health (working_memory, knowledge_graph, development_context)
    4. Response templates loaded
    5. Protection rules valid
    6. Core modules present (orchestrators/agents)
    7. Configuration valid (cortex.config.json)
    8. Brain integrity (basic validation)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: PRODUCTION
"""

import logging
import json
import sqlite3
import yaml
import psutil
from pathlib import Path
from typing import Dict, Any, List
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
class HealthCheckResult:
    """Result of a single health check."""
    check_name: str
    passed: bool
    message: str
    details: str = ""
    severity: str = "ERROR"  # ERROR, WARNING, INFO
    metrics: Dict[str, Any] = field(default_factory=dict)
    
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
class HealthReport:
    """Complete system health report."""
    timestamp: datetime
    checks: List[HealthCheckResult] = field(default_factory=list)
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
        """Overall health status."""
        return all(check.passed or check.severity == "WARNING" for check in self.checks)
    
    @property
    def status_text(self) -> str:
        """Human-readable status."""
        if self.is_healthy:
            return f"HEALTHY ({self.passed_count}/{self.total_count} checks passed)"
        else:
            failed = self.total_count - self.passed_count
            return f"UNHEALTHY ({failed} checks failed)"
    
    def format_console(self) -> str:
        """Format report for console output."""
        lines = []
        lines.append("🧠 CORTEX System Health Check")
        lines.append("━" * 70)
        lines.append("")
        
        # Show each check
        for check in self.checks:
            lines.append(str(check))
        
        lines.append("")
        lines.append("━" * 70)
        lines.append(f"System Status: {self.status_text}")
        lines.append(f"Execution Time: {self.execution_time:.1f}s")
        
        return "\n".join(lines)


class HealthCheckUtility:
    """
    Fast system health validator.
    
    Usage:
        utility = HealthCheckUtility()
        report = utility.run_healthcheck()
        print(report.format_console())
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize health check utility.
        
        Args:
            project_root: Project root path (default: config.root_path)
        """
        self.project_root = project_root or config.root_path
        self.brain_path = config.brain_path
        self.start_time = None
    
    def validate_system_resources(self) -> HealthCheckResult:
        """
        Check system resources (CPU, memory, disk).
        
        Returns:
            HealthCheckResult with resource metrics
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(str(self.project_root))
            
            # Thresholds
            cpu_critical = 90.0
            memory_critical = 90.0
            disk_critical = 95.0
            
            issues = []
            if cpu_percent > cpu_critical:
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            if memory.percent > memory_critical:
                issues.append(f"High memory usage: {memory.percent:.1f}%")
            if disk.percent > disk_critical:
                issues.append(f"Low disk space: {disk.percent:.1f}% used")
            
            metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }
            
            if issues:
                return HealthCheckResult(
                    check_name="System Resources",
                    passed=False,
                    message=f"{len(issues)} resource issue(s) detected",
                    details="; ".join(issues),
                    severity="WARNING",
                    metrics=metrics
                )
            
            return HealthCheckResult(
                check_name="System Resources",
                passed=True,
                message=f"CPU {cpu_percent:.1f}%, Memory {memory.percent:.1f}%, Disk {disk.percent:.1f}%",
                severity="INFO",
                metrics=metrics
            )
        
        except Exception as e:
            return HealthCheckResult(
                check_name="System Resources",
                passed=False,
                message=f"Resource check error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_brain_structure(self) -> HealthCheckResult:
        """
        Check brain tier structure (tier0-3).
        
        Returns:
            HealthCheckResult for brain architecture
        """
        try:
            required_tiers = {
                'tier0': self.project_root / 'src' / 'tier0',
                'tier1': self.brain_path / 'tier1',
                'tier2': self.brain_path / 'tier2',
                'tier3': self.brain_path / 'tier3'
            }
            
            missing = [name for name, path in required_tiers.items() if not path.exists()]
            
            if missing:
                return HealthCheckResult(
                    check_name="Brain Architecture",
                    passed=False,
                    message=f"Missing tiers: {', '.join(missing)}",
                    details="Brain structure incomplete",
                    severity="ERROR"
                )
            
            return HealthCheckResult(
                check_name="Brain Architecture",
                passed=True,
                message="All 4 tiers present (tier0 code + tier1-3 data)",
                severity="INFO"
            )
        
        except Exception as e:
            return HealthCheckResult(
                check_name="Brain Architecture",
                passed=False,
                message=f"Structure check error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_database(self, db_name: str, tier: int, display_name: str) -> HealthCheckResult:
        """
        Check database health.
        
        Args:
            db_name: Database filename
            tier: Tier number (1, 2, 3)
            display_name: Human-readable name
        
        Returns:
            HealthCheckResult for database
        """
        try:
            db_path = self.brain_path / f"tier{tier}" / db_name
            
            if not db_path.exists():
                return HealthCheckResult(
                    check_name=display_name,
                    passed=False,
                    message=f"Database not found at {db_path}",
                    severity="ERROR"
                )
            
            # Check database integrity
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Integrity check
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            
            # Count tables
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Get database size
            db_size_mb = db_path.stat().st_size / (1024 * 1024)
            
            conn.close()
            
            if integrity != "ok":
                return HealthCheckResult(
                    check_name=display_name,
                    passed=False,
                    message=f"Database corrupted: {integrity}",
                    severity="ERROR"
                )
            
            return HealthCheckResult(
                check_name=display_name,
                passed=True,
                message=f"Database healthy ({table_count} tables, {db_size_mb:.2f} MB)",
                severity="INFO",
                metrics={'table_count': table_count, 'size_mb': db_size_mb}
            )
        
        except Exception as e:
            return HealthCheckResult(
                check_name=display_name,
                passed=False,
                message=f"Database check error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_protection_rules(self) -> HealthCheckResult:
        """
        Check brain protection rules.
        
        Returns:
            HealthCheckResult for protection rules
        """
        try:
            rules_path = self.brain_path / "brain-protection-rules.yaml"
            
            if not rules_path.exists():
                return HealthCheckResult(
                    check_name="Protection Rules",
                    passed=False,
                    message=f"brain-protection-rules.yaml not found",
                    severity="ERROR"
                )
            
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            
            if not rules or not isinstance(rules, dict):
                return HealthCheckResult(
                    check_name="Protection Rules",
                    passed=False,
                    message="Invalid rules format",
                    severity="ERROR"
                )
            
            # Count rules (various formats supported)
            rule_count = 0
            if 'skull_protection_layers' in rules:
                rule_count = len(rules['skull_protection_layers'])
            elif 'tier_0_instincts' in rules:
                rule_count = len(rules['tier_0_instincts'])
            elif 'rules' in rules:
                rule_count = len(rules['rules'])
            
            return HealthCheckResult(
                check_name="Protection Rules",
                passed=True,
                message=f"Valid ({rule_count} rules loaded)",
                severity="INFO"
            )
        
        except Exception as e:
            return HealthCheckResult(
                check_name="Protection Rules",
                passed=False,
                message=f"Rules validation error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_response_templates(self) -> HealthCheckResult:
        """
        Check response templates.
        
        Returns:
            HealthCheckResult for templates
        """
        try:
            templates_path = self.brain_path / "response-templates.yaml"
            
            if not templates_path.exists():
                return HealthCheckResult(
                    check_name="Response Templates",
                    passed=False,
                    message="response-templates.yaml not found",
                    severity="WARNING"  # Warning because system can work without templates
                )
            
            with open(templates_path, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
            
            if not templates or not isinstance(templates, dict):
                return HealthCheckResult(
                    check_name="Response Templates",
                    passed=False,
                    message="Invalid templates format",
                    severity="WARNING"
                )
            
            # Count templates
            template_count = len(templates.get('templates', {}))
            
            return HealthCheckResult(
                check_name="Response Templates",
                passed=True,
                message=f"{template_count} templates loaded",
                severity="INFO"
            )
        
        except Exception as e:
            return HealthCheckResult(
                check_name="Response Templates",
                passed=False,
                message=f"Template validation error: {str(e)}",
                severity="WARNING"
            )
    
    def validate_core_modules(self) -> HealthCheckResult:
        """
        Check core modules present (orchestrators/agents).
        
        Returns:
            HealthCheckResult for modules
        """
        try:
            src_path = self.project_root / 'src'
            
            # Count orchestrators
            orchestrators = list((src_path / 'orchestrators').glob('*.py')) if (src_path / 'orchestrators').exists() else []
            orchestrators = [f for f in orchestrators if f.name != '__init__.py']
            
            # Count agents
            agents = list((src_path / 'cortex_agents').rglob('*.py')) if (src_path / 'cortex_agents').exists() else []
            agents = [f for f in agents if f.name != '__init__.py' and not f.name.startswith('test_')]
            
            if len(orchestrators) == 0 and len(agents) == 0:
                return HealthCheckResult(
                    check_name="Core Modules",
                    passed=False,
                    message="No orchestrators or agents found",
                    severity="ERROR"
                )
            
            return HealthCheckResult(
                check_name="Core Modules",
                passed=True,
                message=f"{len(orchestrators)} orchestrators, {len(agents)} agents discovered",
                severity="INFO"
            )
        
        except Exception as e:
            return HealthCheckResult(
                check_name="Core Modules",
                passed=False,
                message=f"Module discovery error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_configuration(self) -> HealthCheckResult:
        """
        Check cortex.config.json validity.
        
        Returns:
            HealthCheckResult for configuration
        """
        try:
            config_path = self.project_root / "cortex.config.json"
            
            if not config_path.exists():
                return HealthCheckResult(
                    check_name="Configuration",
                    passed=False,
                    message="cortex.config.json not found",
                    severity="ERROR"
                )
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Basic validation
            if not isinstance(config_data, dict):
                return HealthCheckResult(
                    check_name="Configuration",
                    passed=False,
                    message="Invalid config format",
                    severity="ERROR"
                )
            
            return HealthCheckResult(
                check_name="Configuration",
                passed=True,
                message="cortex.config.json valid",
                severity="INFO"
            )
        
        except json.JSONDecodeError as e:
            return HealthCheckResult(
                check_name="Configuration",
                passed=False,
                message=f"JSON parsing error: {str(e)}",
                details="Fix JSON syntax in cortex.config.json",
                severity="ERROR"
            )
        except Exception as e:
            return HealthCheckResult(
                check_name="Configuration",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def run_healthcheck(self) -> HealthReport:
        """Execute all health checks and generate report."""
        self.start_time = datetime.now()
        
        report = HealthReport(timestamp=self.start_time)
        
        # Execute 8 core health checks
        report.checks.append(self.validate_system_resources())
        report.checks.append(self.validate_brain_structure())
        report.checks.append(self.validate_database("working_memory.db", 1, "Working Memory"))
        report.checks.append(self.validate_database("knowledge_graph.db", 2, "Knowledge Graph"))
        report.checks.append(self.validate_database("development_context.db", 3, "Development Context"))
        report.checks.append(self.validate_protection_rules())
        report.checks.append(self.validate_response_templates())
        report.checks.append(self.validate_core_modules())
        report.checks.append(self.validate_configuration())
        
        end_time = datetime.now()
        report.execution_time = (end_time - self.start_time).total_seconds()
        
        return report


def run_healthcheck_utility() -> Dict[str, Any]:
    """
    Entry point for health check utility - callable from orchestrators or CLI.
    
    Returns:
        Dict with 'success', 'message', 'report_text', 'report_data'
    """
    try:
        utility = HealthCheckUtility()
        report = utility.run_healthcheck()
        
        # Format console output
        console_output = report.format_console()
        safe_print(console_output)
        
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
                        'severity': check.severity,
                        'metrics': check.metrics
                    }
                    for check in report.checks
                ]
            }
        }
    
    except Exception as e:
        error_message = f"Health check utility execution failed: {str(e)}"
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
    result = run_healthcheck_utility()
    sys.exit(0 if result['success'] else 1)
